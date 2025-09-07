"""MCP Server Management resource for LumnisAI."""
from typing import Any, Literal, overload
from uuid import UUID

from ..models.mcp_servers import (
    MCPServer,
    MCPServerCreateRequest,
    MCPServerListResponse,
    MCPServerUpdateRequest,
    MCPTestConnectionResponse,
    MCPToolListResponse,
    Scope,
    TransportType,
)
from .base import BaseResource


class MCPServersResource(BaseResource):
    """Resource for managing MCP servers."""

    async def create(
        self,
        *,
        name: str,
        transport: TransportType,
        scope: Scope,
        description: str | None = None,
        user_identifier: str | None = None,
        command: str | None = None,
        args: list[str] | None = None,
        url: str | None = None,
        env: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> MCPServer:
        """Create a new MCP server configuration.
        
        Args:
            name: Unique server name (1-255 chars)
            transport: Transport type: "stdio", "streamable_http", or "sse"
            scope: Configuration scope: "tenant" or "user"
            description: Optional server description (max 1000 chars)
            user_identifier: User UUID or email (required for user scope)
            command: Command for stdio transport (required for stdio)
            args: Arguments for stdio command
            url: URL for HTTP transports (required for HTTP transports)
            env: Environment variables (will be encrypted)
            headers: HTTP headers (will be encrypted)
            
        Returns:
            Created MCP server configuration
            
        Raises:
            ValueError: If validation fails (e.g., missing required fields)
            LumnisAPIError: If API request fails
        """
        # Create the request model (with validation)
        create_request = MCPServerCreateRequest(
            name=name,
            transport=transport,
            scope=scope,
            description=description,
            user_identifier=user_identifier,
            command=command,
            args=args,
            url=url,
            env=env,
            headers=headers,
        )

        response_data = await self._transport.request(
            "POST",
            "/v1/mcp-servers",
            json=create_request.model_dump(exclude_none=True),
        )

        return MCPServer(**response_data)

    @overload
    async def list(
        self,
        *,
        scope: Literal["tenant", "user", "all"] | None = None,
        user_identifier: str | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> MCPServerListResponse: ...

    async def list(
        self,
        *,
        scope: str | None = None,
        user_identifier: str | None = None,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> MCPServerListResponse:
        """List MCP servers for the authenticated tenant.
        
        Args:
            scope: Filter by scope ("tenant", "user", or "all"). Default: "all"
            user_identifier: Filter by specific user (UUID or email)
            is_active: Filter by active status
            skip: Number of records to skip for pagination. Default: 0
            limit: Maximum records to return (max 100). Default: 100
            
        Returns:
            List of MCP server configurations with pagination info
        """
        params: dict[str, Any] = {
            "skip": skip,
            "limit": min(limit, 100),
        }

        if scope is not None:
            params["scope"] = scope
        if user_identifier is not None:
            params["user_identifier"] = user_identifier
        if is_active is not None:
            params["is_active"] = str(is_active).lower()

        response_data = await self._transport.request(
            "GET",
            "/v1/mcp-servers",
            params=params,
        )

        return MCPServerListResponse(**response_data)

    async def get(self, server_id: str | UUID) -> MCPServer:
        """Retrieve a specific MCP server configuration.
        
        Args:
            server_id: UUID of the server configuration
            
        Returns:
            MCP server configuration
            
        Raises:
            LumnisNotFoundError: If server not found
        """
        response_data = await self._transport.request(
            "GET",
            f"/v1/mcp-servers/{server_id}",
        )

        return MCPServer(**response_data)

    async def update(
        self,
        server_id: str | UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        url: str | None = None,
        env: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        is_active: bool | None = None,
    ) -> MCPServer:
        """Update an existing MCP server configuration.
        
        Only provided fields are updated. Secrets (env, headers) are replaced
        entirely if provided.
        
        Args:
            server_id: UUID of the server configuration
            name: New server name
            description: Updated description
            url: Updated URL (HTTP transports only)
            env: Updated env vars (replaces all existing)
            headers: Updated headers (replaces all existing)
            is_active: Enable/disable server
            
        Returns:
            Updated MCP server configuration
            
        Raises:
            LumnisNotFoundError: If server not found
            ValueError: If validation fails
        """
        update_request = MCPServerUpdateRequest(
            name=name,
            description=description,
            url=url,
            env=env,
            headers=headers,
            is_active=is_active,
        )

        response_data = await self._transport.request(
            "PATCH",
            f"/v1/mcp-servers/{server_id}",
            json=update_request.model_dump(exclude_none=True),
        )

        return MCPServer(**response_data)

    async def delete(self, server_id: str | UUID) -> None:
        """Permanently delete an MCP server configuration.
        
        This will also delete all associated secrets and indexes.
        
        Args:
            server_id: UUID of the server configuration
            
        Raises:
            LumnisNotFoundError: If server not found
        """
        await self._transport.request(
            "DELETE",
            f"/v1/mcp-servers/{server_id}",
        )

    async def list_tools(self, server_id: str | UUID) -> MCPToolListResponse:
        """List all tools provided by a specific MCP server.
        
        Args:
            server_id: UUID of the server configuration
            
        Returns:
            List of tools with their schemas
            
        Raises:
            LumnisNotFoundError: If server not found
        """
        response_data = await self._transport.request(
            "GET",
            f"/v1/mcp-servers/{server_id}/tools",
        )

        return MCPToolListResponse(**response_data)

    async def test_connection(self, server_id: str | UUID) -> MCPTestConnectionResponse:
        """Test connection to an MCP server.
        
        Verifies the server is properly configured and can be reached.
        
        Args:
            server_id: UUID of the server configuration
            
        Returns:
            Test result with success status and details
            
        Raises:
            LumnisNotFoundError: If server not found
        """
        response_data = await self._transport.request(
            "POST",
            f"/v1/mcp-servers/{server_id}/test",
        )

        return MCPTestConnectionResponse(**response_data)
