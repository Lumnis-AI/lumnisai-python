from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StoreApiKeyRequest(BaseModel):
    provider: str
    api_key: str = Field(..., min_length=3, max_length=2000, description="The external API key to store")
    key_name: Optional[str] = Field(None, max_length=100, description="Optional friendly name for the key")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date for the key")


class ExternalApiKeyResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)})

    key_id: str
    provider: str
    key_name: Optional[str] = None
    is_active: bool
    expires_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None


class ApiKeyModeRequest(BaseModel):
    mode: str


class ApiKeyModeResponse(BaseModel):
    api_key_mode: str
