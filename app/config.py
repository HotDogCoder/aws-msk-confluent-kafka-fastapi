from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field(default="MSK FastAPI", env="APP_NAME")

    # Kafka/MSK connection
    bootstrap_servers: str = Field(default="localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    security_protocol: str = Field(default="PLAINTEXT", env="KAFKA_SECURITY_PROTOCOL")  # SSL or SASL_SSL for MSK
    sasl_mechanism: Optional[str] = Field(default=None, env="KAFKA_SASL_MECHANISM")  # PLAIN or SCRAM-SHA-512
    sasl_username: Optional[str] = Field(default=None, env="KAFKA_SASL_USERNAME")
    sasl_password: Optional[str] = Field(default=None, env="KAFKA_SASL_PASSWORD")
    ssl_ca_location: Optional[str] = Field(default=None, env="KAFKA_SSL_CA_LOCATION")  # e.g., ./certs/AmazonRootCA1.pem

    client_id: str = Field(default="msk-fastapi", env="KAFKA_CLIENT_ID")
    topic_default: str = Field(default="events", env="KAFKA_TOPIC_DEFAULT")
    consumer_group_id: str = Field(default="msk-fastapi-group", env="KAFKA_CONSUMER_GROUP_ID")
    consumer_auto_offset_reset: str = Field(default="earliest", env="KAFKA_CONSUMER_AUTO_OFFSET_RESET")
    enable_idempotence: bool = Field(default=True, env="KAFKA_ENABLE_IDEMPOTENCE")
    delivery_timeout_ms: int = Field(default=120000, env="KAFKA_DELIVERY_TIMEOUT_MS")
    extra_topics: Optional[str] = Field(default=None, env="KAFKA_EXTRA_TOPICS")  # comma-separated additional topics

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def kafka_common(self) -> dict:
        conf = {
            "bootstrap.servers": self.bootstrap_servers,
            "client.id": self.client_id,
            "security.protocol": self.security_protocol,
        }
        if self.sasl_mechanism:
            conf["sasl.mechanism"] = self.sasl_mechanism
        if self.sasl_username:
            conf["sasl.username"] = self.sasl_username
        if self.sasl_password:
            conf["sasl.password"] = self.sasl_password
        if self.ssl_ca_location:
            conf["ssl.ca.location"] = self.ssl_ca_location
            conf["ssl.endpoint.identification.algorithm"] = "https"
        return conf

    def kafka_producer(self) -> dict:
        conf = self.kafka_common()
        conf.update(
            {
                "enable.idempotence": self.enable_idempotence,
                "acks": "all",
                "delivery.timeout.ms": self.delivery_timeout_ms,
            }
        )
        return conf

    def kafka_consumer(self) -> dict:
        conf = self.kafka_common()
        conf.update(
            {
                "group.id": self.consumer_group_id,
                "auto.offset.reset": self.consumer_auto_offset_reset,
                "enable.auto.commit": True,
            }
        )
        return conf

    def consumer_topics(self) -> List[str]:
        topics = [self.topic_default]
        if self.extra_topics:
            topics += [t.strip() for t in self.extra_topics.split(",") if t.strip()]
        return topics


@lru_cache
def get_settings() -> Settings:
    return Settings()