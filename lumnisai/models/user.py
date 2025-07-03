from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the user")
    email: EmailStr = Field(..., description="User's email address")
    first_name: str | None = Field(None, description="User's first name")
    last_name: str | None = Field(None, description="User's last name")
    tenant_id: UUID = Field(..., description="Tenant ID the user belongs to")
    is_active: bool = Field(True, description="Whether the user is active")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="User last update timestamp")


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    first_name: str | None = Field(None, description="User's first name")
    last_name: str | None = Field(None, description="User's last name")


class UserUpdate(BaseModel):
    first_name: str | None = Field(None, description="User's first name")
    last_name: str | None = Field(None, description="User's last name")


class PaginationInfo(BaseModel):
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class UsersListResponse(BaseModel):
    users: list[User]
    pagination: PaginationInfo = Field(..., description="Pagination information")
