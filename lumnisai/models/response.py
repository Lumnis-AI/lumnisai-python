from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .model_preferences import ModelOverrides


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ProgressEntry(BaseModel):
    ts: datetime = Field(description="Timestamp")
    state: str = Field(description="Current state (e.g. 'processing', 'completed', 'failed')")
    message: str
    output_text: str | None = None

    def __str__(self):
        return f"{self.ts.isoformat()} - {self.state.upper()} {self.message}"

class ArtifactPart(BaseModel):
    kind: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class Artifact(BaseModel):
    artifactId: str
    name: str
    description: str
    parts: list[ArtifactPart]
    metadata: dict[str, Any] = Field(default_factory=dict)
    extensions: list[Any] = Field(default_factory=list)

class CreateResponseRequest(BaseModel):
    thread_id: UUID | None = Field(None, description="Optional thread ID for conversation continuity")
    messages: list[Message] = Field(..., min_length=1, description="Input messages")
    user_id: str | None = Field(None, description="Optional user ID for tracking")
    response_format: dict[str, Any] | None = Field(None, description="JSON Schema to structure the response output")
    response_format_instructions: str | None = Field(None, description="Additional instructions for how to format the structured response")
    model_overrides: ModelOverrides | None = Field(None, description="Runtime model overrides for this request")

class ResponseObject(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat(), Decimal: lambda v: float(v), UUID: lambda v: str(v)})
    response_id: UUID
    thread_id: UUID
    tenant_id: UUID
    user_id: UUID | None = None
    status: Literal["queued", "in_progress", "succeeded", "failed", "cancelled"]
    progress: list[ProgressEntry] = Field(default_factory=list)

    input_messages: list[Message] | None = None

    output_text: str | None = None  # Main content field from API
    structured_response: dict[str, Any] | None = None  # Structured output that conforms to the provided JSON Schema
    artifacts: list[Artifact] | None = None  # New artifacts field
    error: dict[str, Any] | None = None

    created_at: datetime
    completed_at: datetime | None = None

    @property
    def content(self) -> str | None:
        return self.output_text
    
    def __str__(self):
        return f"Response ID: {self.response_id}\nThread ID: {self.thread_id}\nStatus: {self.status}\nCreated At: {self.created_at}\nCompleted At: {self.completed_at}"



class CancelResponse(BaseModel):
    status: Literal["cancelled"]
    message: str


class CreateResponseResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)})

    response_id: UUID
    thread_id: UUID
    status: Literal["queued", "in_progress", "succeeded", "failed", "cancelled"]
    tenant_id: UUID
    created_at: datetime


