from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ThreadObject(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)})

    thread_id: UUID
    tenant_id: UUID
    user_id: UUID | None = None
    title: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    response_count: int = 0
    last_response_at: datetime | None = None

    def __str__(self):
        return f"Thread ID: {self.thread_id}\nTenant ID: {self.tenant_id}\nUser ID: {self.user_id}\nTitle: {self.title}\nCreated At: {self.created_at}\nUpdated At: {self.updated_at}\nResponse Count: {self.response_count}\nLast Response At: {self.last_response_at}"


class ThreadListResponse(BaseModel):
    threads: list[ThreadObject]
    total: int
    limit: int
    offset: int


class UpdateThreadRequest(BaseModel):
    title: str | None = Field(None, max_length=500, description="Thread title")
