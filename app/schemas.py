from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field


class PublishRequest(BaseModel):
    topic: Optional[str] = Field(default=None, description="Kafka topic to publish to")
    key: Optional[str] = Field(default=None, description="Optional message key")
    value: Union[str, Dict[str, Any]] = Field(description="Message payload (string or JSON object)")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Optional headers as key-value pairs")
    sync: bool = Field(default=False, description="Wait for delivery confirmation")


class IntegrationEventRequest(BaseModel):
    integration: str = Field(description="Integrator source, e.g., openai, pollinations")
    action: str = Field(description="Action name, e.g., image, start, status")
    payload: Dict[str, Any] = Field(description="Event payload from integrator")
    topic: Optional[str] = Field(default=None, description="Kafka topic override; defaults to settings.topic_default")
    key: Optional[str] = Field(default=None, description="Optional message key")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Optional headers to include")
    sync: bool = Field(default=False, description="Wait for delivery confirmation")


class ImageGeneratedRequest(BaseModel):
    integration: str = Field(description="Integrator source, e.g., openai, pollinations, stable_horde")
    image_url: str = Field(description="Public URL of the saved image (S3 or local)")
    prompt: Optional[str] = Field(default=None, description="Prompt used to generate the image")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the event")
    site_id: Optional[str] = Field(default=None, description="Origin site identifier from Django integrator")
    user_id: Optional[str] = Field(default=None, description="Origin user identifier from Django integrator")
    topic: Optional[str] = Field(default=None, description="Kafka topic override; defaults to settings.topic_default")
    key: Optional[str] = Field(default=None, description="Optional message key")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Optional headers to include")
    sync: bool = Field(default=False, description="Wait for delivery confirmation")


class VideoGeneratedRequest(BaseModel):
    integration: str = Field(description="Integrator source, e.g., replicate")
    video_url: str = Field(description="Public URL of the saved video (S3 or local)")
    prompt: Optional[str] = Field(default=None, description="Prompt used to generate the video")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the event")
    site_id: Optional[str] = Field(default=None, description="Origin site identifier from Django integrator")
    user_id: Optional[str] = Field(default=None, description="Origin user identifier from Django integrator")
    topic: Optional[str] = Field(default=None, description="Kafka topic override; defaults to settings.topic_default")
    key: Optional[str] = Field(default=None, description="Optional message key")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Optional headers to include")
    sync: bool = Field(default=False, description="Wait for delivery confirmation")