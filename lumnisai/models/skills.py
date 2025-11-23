"""Models for Skills API."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SkillGuidelineCreate(BaseModel):
    """Schema for creating a skill guideline."""
    name: str = Field(..., max_length=1000, description="Human-readable skill name")
    description: str = Field(..., description="Concise description used for embeddings and semantic search")
    content: str = Field(..., description="Full skill guideline content with detailed methodologies")
    category: Optional[str] = Field(None, max_length=100, description="Skill category (e.g., 'people_search')")
    version: str = Field("1.0.0", max_length=20, description="Semantic version for skill updates")


class SkillGuidelineUpdate(BaseModel):
    """Schema for updating a skill guideline."""
    name: Optional[str] = Field(None, max_length=1000)
    description: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class SkillGuideline(BaseModel):
    """Schema for skill guideline responses."""
    id: UUID
    name: str
    description: str
    content: str
    category: Optional[str] = None
    version: str
    tenant_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class SkillGuidelineListResponse(BaseModel):
    """Schema for paginated skill guideline lists."""
    skills: List[SkillGuideline]
    total: int
    page: int = 1
    page_size: int = 50