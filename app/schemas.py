from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field


class PublishRequest(BaseModel):
    topic: Optional[str] = Field(default=None, description="Kafka topic to publish to")
    key: Optional[str] = Field(default=None, description="Optional message key")
    value: Union[str, Dict[str, Any]] = Field(description="Message payload (string or JSON object)")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Optional headers as key-value pairs")
    sync: bool = Field(default=False, description="Wait for delivery confirmation")