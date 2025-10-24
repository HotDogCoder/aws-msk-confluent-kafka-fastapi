import logging
from typing import Dict

from fastapi import FastAPI

from app.config import get_settings
from app.kafka.consumer import start_consumer, stop_consumer
from app.kafka.producer import close_producer, produce_message
from app.schemas import PublishRequest, IntegrationEventRequest, ImageGeneratedRequest, VideoGeneratedRequest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("app")

app = FastAPI(title=get_settings().app_name)


@app.on_event("startup")
async def startup():
    # Start consumer in the background; logs consumed messages by default
    start_consumer()
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown():
    # Gracefully stop consumer and flush/close producer
    stop_consumer()
    close_producer()
    logger.info("Application shutdown complete")


@app.get("/health")
async def health() -> Dict[str, str]:
    # Lightweight health check; attempts to fetch metadata via producer
    try:
        # Lazy import to avoid creating a Producer instance unnecessarily
        from confluent_kafka import Producer

        conf = get_settings().kafka_producer()
        p = Producer(conf)
        _ = p.list_topics(timeout=5)
        status = "ok"
    except Exception as e:
        logger.exception("Kafka health check failed: %s", e)
        status = "error"
    return {"status": status}


@app.post("/publish")
async def publish(req: PublishRequest) -> Dict[str, str]:
    settings = get_settings()
    topic = req.topic or settings.topic_default
    result = produce_message(
        topic=topic,
        value=req.value,
        key=req.key,
        headers=req.headers,
        sync=req.sync,
    )
    return {"topic": result["topic"], "status": result["status"]}

@app.post("/integrations/event")
async def integrations_event(req: IntegrationEventRequest) -> Dict[str, str]:
    settings = get_settings()
    topic = req.topic or settings.topic_default
    headers = (req.headers or {}) | {"integration": req.integration, "action": req.action}
    payload = {
        "type": "integration_event",
        "integration": req.integration,
        "action": req.action,
        "payload": req.payload,
    }
    result = produce_message(
        topic=topic,
        value=payload,
        key=req.key,
        headers=headers,
        sync=req.sync,
    )
    return {"topic": result["topic"], "status": result["status"]}

@app.post("/integrations/image-generated")
async def integrations_image_generated(req: ImageGeneratedRequest) -> Dict[str, str]:
    settings = get_settings()
    topic = req.topic or settings.topic_default
    headers = (req.headers or {}) | {"integration": req.integration, "event": "image_generated"}
    payload = {
        "type": "image_generated",
        "integration": req.integration,
        "image_url": req.image_url,
        "prompt": req.prompt,
        "meta": req.meta or {},
        "site_id": req.site_id,
        "user_id": req.user_id,
    }
    result = produce_message(
        topic=topic,
        value=payload,
        key=req.key,
        headers=headers,
        sync=req.sync,
    )
    return {"topic": result["topic"], "status": result["status"]}

@app.post("/integrations/video-generated")
async def integrations_video_generated(req: VideoGeneratedRequest) -> Dict[str, str]:
    settings = get_settings()
    topic = req.topic or settings.topic_default
    headers = (req.headers or {}) | {"integration": req.integration, "event": "video_generated"}
    payload = {
        "type": "video_generated",
        "integration": req.integration,
        "video_url": req.video_url,
        "prompt": req.prompt,
        "meta": req.meta or {},
        "site_id": req.site_id,
        "user_id": req.user_id,
    }
    result = produce_message(
        topic=topic,
        value=payload,
        key=req.key,
        headers=headers,
        sync=req.sync,
    )
    return {"topic": result["topic"], "status": result["status"]}