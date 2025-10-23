import logging
import threading
from typing import Callable, Optional

from confluent_kafka import Consumer, KafkaException

from app.config import get_settings

logger = logging.getLogger("kafka.consumer")


class KafkaConsumerWorker:
    def __init__(self, handler: Optional[Callable] = None):
        self._settings = get_settings()
        self._consumer: Optional[Consumer] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._handler = handler or self._default_handler

    def _default_handler(self, msg):
        headers = msg.headers() or []
        header_map = {k: (v.decode("utf-8") if isinstance(v, (bytes, bytearray)) else v) for k, v in headers}
        logger.info(
            "Consumed: topic=%s partition=%s offset=%s key=%s value=%s headers=%s",
            msg.topic(),
            msg.partition(),
            msg.offset(),
            msg.key().decode("utf-8") if msg.key() else None,
            (msg.value().decode("utf-8") if msg.value() else None),
            header_map,
        )

    def start(self):
        if self._running:
            logger.info("Consumer already running")
            return
        try:
            conf = self._settings.kafka_consumer()
            self._consumer = Consumer(conf)
            self._consumer.subscribe(self._settings.consumer_topics())
            self._running = True
            self._thread = threading.Thread(target=self._loop, name="KafkaConsumer", daemon=True)
            self._thread.start()
            logger.info("Kafka Consumer started with topics: %s", self._settings.consumer_topics())
        except Exception as e:
            logger.exception("Failed to start consumer: %s", e)
            self._running = False

    def _loop(self):
        assert self._consumer is not None
        while self._running:
            try:
                msg = self._consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error("Consumer error: %s", msg.error())
                    continue
                self._handler(msg)
            except KafkaException as ke:
                logger.error("KafkaException: %s", ke)
            except Exception as e:
                logger.exception("Unexpected consumer error: %s", e)
        logger.info("Consumer loop exiting")

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        if self._consumer:
            try:
                self._consumer.close()
            except Exception:
                pass
        logger.info("Kafka Consumer stopped")


_worker: Optional[KafkaConsumerWorker] = None


def start_consumer(handler: Optional[Callable] = None):
    global _worker
    if _worker is None:
        _worker = KafkaConsumerWorker(handler=handler)
    _worker.start()


def stop_consumer():
    global _worker
    if _worker is not None:
        _worker.stop()
        _worker = None