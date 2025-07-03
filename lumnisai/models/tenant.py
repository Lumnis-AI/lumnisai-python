from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TenantInfo(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)})

    tenant_id: UUID = Field(alias="id")
    name: str
    api_key_mode: str
    created_at: datetime
    updated_at: datetime | None = None
