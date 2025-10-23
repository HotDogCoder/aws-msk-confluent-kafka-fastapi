import json
import logging
from typing import Any, Dict, Optional, Union, List, Tuple

from confluent_kafka import Producer

from app.config import get_settings

logger = logging.getLogger("kafka.producer")

_producer: Optional[Producer] = None


def _build_headers(headers: Optional[Dict[str, str]]) -> Optional[List[Tuple[str, bytes]]]:
    if not headers:
        return None
    out: List[Tuple[str, bytes]] = []
    for k, v in headers.items():
        out.append((k, str(v).encode("utf-8")))
    return out


def get_producer() -> Producer:
    global _producer
    if _producer is None:
        conf = get_settings().kafka_producer()
        _producer = Producer(conf)
        logger.info("Kafka Producer initialized")
    return _producer


def _delivery_report(err, msg):
    if err is not None:
        logger.error("Delivery failed: %s", err)
    else:
        logger.debug(
            "Message delivered to %s [%d] at offset %d",
            msg.topic(),
            msg.partition(),
            msg.offset(),
        )


def produce_message(
    topic: str,
    value: Union[str, bytes, Dict[str, Any]],
    key: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    sync: bool = False,
    timeout: float = 5.0,
) -> Dict[str, Any]:
    """Produce a message to Kafka.

    - If value is dict, it will be JSON-serialized.
    - If sync=True, flush waits for delivery.
    """
    producer = get_producer()

    payload_bytes: bytes
    if isinstance(value, bytes):
        payload_bytes = value
    elif isinstance(value, str):
        payload_bytes = value.encode("utf-8")
    else:
        payload_bytes = json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    hdrs = _build_headers(headers)

    producer.produce(
        topic=topic,
        key=key.encode("utf-8") if key else None,
        value=payload_bytes,
        headers=hdrs,
        on_delivery=_delivery_report,
    )
    # Trigger delivery callbacks
    producer.poll(0)

    if sync:
        producer.flush(timeout)
        status = "delivered"
    else:
        status = "enqueued"

    return {"topic": topic, "status": status}


def close_producer():
    global _producer
    if _producer is not None:
        try:
            _producer.flush(5.0)
        finally:
            _producer = None
            logger.info("Kafka Producer closed")