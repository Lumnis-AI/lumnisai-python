"""Models for MCP Server Management API."""
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# Transport types
TransportType = Literal["stdio", "streamable_http", "sse"]
Scope = Literal["tenant", "user"]


class MCPServerCreateRequest(BaseModel):
    """Request model for creating an MCP server configuration."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique server name"
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="Server description"
    )
    transport: TransportType = Field(
        ...,
        description="Transport type: stdio, streamable_http, or sse"
    )
    scope: Scope = Field(
        ...,
        description="Configuration scope: tenant or user"
    )
    user_identifier: str | None = Field(
        None,
        description="User UUID or email (required for user scope)"
    )

    # Transport-specific fields
    command: str | None = Field(
        None,
        max_length=255,
        description="Command for stdio transport"
    )
    args: list[str] | None = Field(
        None,
        description="Arguments for stdio command"
    )
    url: str | None = Field(
        None,
        max_length=1024,
        description="URL for HTTP transports"
    )

    # Secrets (encrypted before storage)
    env: dict[str, str] | None = Field(
        None,
        description="Environment variables (encrypted)"
    )
    headers: dict[str, str] | None = Field(
        None,
        description="HTTP headers (encrypted)"
    )

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: str | None, info) -> str | None:
        """Validate command is provided for stdio transport."""
        transport = info.data.get("transport")
        if transport == "stdio" and not v:
            raise ValueError("command is required for stdio transport")
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str | None, info) -> str | None:
        """Validate URL is provided for HTTP transports."""
        transport = info.data.get("transport")
        if transport in ("streamable_http", "sse"):
            if not v:
                raise ValueError(f"url is required for {transport} transport")
            if not v.startswith(("http://", "https://")):
                raise ValueError("url must start with http:// or https://")
        return v

    @field_validator("user_identifier")
    @classmethod
    def validate_user_identifier(cls, v: str | None, info) -> str | None:
        """Validate user_identifier based on scope."""
        scope = info.data.get("scope")
        if scope == "user" and not v:
            raise ValueError("user_identifier is required for user scope")
        elif scope == "tenant" and v:
            raise ValueError("user_identifier must be omitted for tenant scope")
        return v


class MCPServerUpdateRequest(BaseModel):
    """Request model for updating an MCP server configuration."""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="New server name"
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="Updated description"
    )
    url: str | None = Field(
        None,
        max_length=1024,
        description="Updated URL (HTTP transports only)"
    )
    env: dict[str, str] | None = Field(
        None,
        description="Updated env vars (replaces all existing)"
    )
    headers: dict[str, str] | None = Field(
        None,
        description="Updated headers (replaces all existing)"
    )
    is_active: bool | None = Field(
        None,
        description="Enable/disable server"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        """Validate URL format if provided."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("url must start with http:// or https://")
        return v


class MCPServerResponse(BaseModel):
    """Response model for MCP server configuration."""

    id: UUID = Field(..., description="Server configuration ID")
    tenant_id: UUID = Field(..., description="Tenant ID")
    user_id: UUID | None = Field(None, description="User ID (null for tenant-scoped)")
    scope: Scope = Field(..., description="Configuration scope")
    name: str = Field(..., description="Server name")
    description: str | None = Field(None, description="Server description")
    transport: TransportType = Field(..., description="Transport type")
    command: str | None = Field(None, description="Command (stdio only)")
    args: list[str] | None = Field(None, description="Arguments (stdio only)")
    url: str | None = Field(None, description="URL (HTTP transports only)")
    is_active: bool = Field(..., description="Whether server is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class MCPServerListResponse(BaseModel):
    """Response model for listing MCP servers."""

    servers: list[MCPServerResponse] = Field(..., description="Array of server configurations")
    total: int = Field(..., description="Total number of servers matching query")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum records returned")


class MCPToolResponse(BaseModel):
    """Response model for an individual MCP tool."""

    name: str = Field(..., description="Tool name as provided by MCP server")
    description: str = Field(..., description="Tool description")
    input_schema: dict[str, Any] = Field(..., description="JSON schema for tool parameters")


class MCPToolListResponse(BaseModel):
    """Response model for listing tools from an MCP server."""

    server_id: UUID = Field(..., description="MCP server ID")
    server_name: str = Field(..., description="MCP server name")
    tools: list[MCPToolResponse] = Field(..., description="Array of available tools")
    total: int = Field(..., description="Total number of tools")


class MCPTestConnectionResponse(BaseModel):
    """Response model for testing MCP server connection."""

    success: bool = Field(..., description="Whether connection test succeeded")
    message: str = Field(..., description="Success or error message")
    tool_count: int | None = Field(None, description="Number of tools (if successful)")
    error_details: str | None = Field(None, description="Detailed error info (if failed)")


# Simplified models for SDK usage (without validation)
class MCPServer(MCPServerResponse):
    """MCP server model for SDK usage."""
    pass


class MCPServerCreate(BaseModel):
    """Simplified create model for SDK usage."""

    name: str
    description: str | None = None
    transport: TransportType
    scope: Scope
    user_identifier: str | None = None
    command: str | None = None
    args: list[str] | None = None
    url: str | None = None
    env: dict[str, str] | None = None
    headers: dict[str, str] | None = None


class MCPServerUpdate(BaseModel):
    """Simplified update model for SDK usage."""

    name: str | None = None
    description: str | None = None
    url: str | None = None
    env: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    is_active: bool | None = None
