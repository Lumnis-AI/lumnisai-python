from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ProgressEntry(BaseModel):
    ts: datetime = Field(description="Timestamp")
    state: str = Field(description="Current state (e.g. 'planning', 'coding')")
    message: str

    def __str__(self):
        return f"{self.ts.isoformat()} - {self.state.upper()} {self.message}"

class CreateResponseRequest(BaseModel):
    thread_id: Optional[UUID] = Field(None, description="Optional thread ID for conversation continuity")
    messages: List[Message] = Field(..., min_length=1, description="Input messages")
    user_id: Optional[str] = Field(None, description="Optional user ID for tracking")

class ResponseObject(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat(), Decimal: lambda v: float(v), UUID: lambda v: str(v)})
    response_id: UUID
    thread_id: UUID
    tenant_id: UUID
    user_id: Optional[UUID] = None
    status: Literal["queued", "in_progress", "succeeded", "failed", "cancelled"]
    progress: List[ProgressEntry] = Field(default_factory=list)

    input_messages: Optional[List[Message]] = None
    
    output_text: Optional[str] = None  # Main content field from API
    error: Optional[Dict[str, Any]] = None
    
    created_at: datetime
    completed_at: Optional[datetime] = None

    @property
    def content(self) -> Optional[str]:
        return self.output_text



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


