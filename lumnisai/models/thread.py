from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ThreadObject(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)})

    thread_id: UUID
    tenant_id: UUID
    user_id: Optional[UUID] = None
    title: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    response_count: int = 0
    last_response_at: Optional[datetime] = None


class ThreadListResponse(BaseModel):
    threads: List[ThreadObject]
    total: int
    limit: int
    offset: int


class UpdateThreadRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=500, description="Thread title")