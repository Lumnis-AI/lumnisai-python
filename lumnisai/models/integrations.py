"""Integration models for Lumnis SDK."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class InitiateConnectionRequest(BaseModel):
    """Request model for initiating a connection."""

    user_id: str = Field(..., description="User identifier within tenant")
    app_name: str = Field(..., description="App name (e.g., 'GITHUB', 'SLACK')")
    integration_id: str | None = Field(None, description="Custom integration identifier")
    redirect_url: str | None = Field(None, description="Custom OAuth redirect URL")
    auth_mode: str | None = Field(None, description="Authentication mode (reserved for future use)")
    connection_params: dict[str, Any] | None = Field(None, description="Connection parameters (reserved for future use)")

    def __str__(self):
        parts = [f"User ID: {self.user_id}", f"App: {self.app_name}"]
        if self.integration_id:
            parts.append(f"Integration ID: {self.integration_id}")
        if self.redirect_url:
            parts.append(f"Redirect URL: {self.redirect_url}")
        if self.auth_mode:
            parts.append(f"Auth Mode: {self.auth_mode}")
        return "InitiateConnectionRequest:\n  " + "\n  ".join(parts)


class InitiateConnectionResponse(BaseModel):
    """Response model for initiating a connection."""

    redirect_url: str | None = Field(None, description="OAuth redirect URL")
    status: str = Field(..., description="Connection status")
    message: str | None = Field(None, description="Status message")

    def __str__(self):
        parts = [f"Status: {self.status}"]
        if self.message:
            parts.append(f"Message: {self.message}")
        if self.redirect_url:
            parts.append(f"Redirect URL: {self.redirect_url}")
        return "InitiateConnectionResponse:\n  " + "\n  ".join(parts)


class ConnectionStatus(BaseModel):
    """Model for connection status."""

    app_name: str = Field(..., description="App name")
    status: Literal["pending", "active", "failed", "expired", "not_connected"] = Field(..., description="Connection status")
    connected_at: datetime | None = Field(None, description="Connection timestamp")
    error_message: str | None = Field(None, description="Error message if connection failed")

    def __str__(self):
        parts = [f"App: {self.app_name}", f"Status: {self.status}"]
        if self.connected_at:
            parts.append(f"Connected at: {self.connected_at}")
        if self.error_message:
            parts.append(f"Error: {self.error_message}")
        return "Connection Status:\n  " + "\n  ".join(parts)


class ListConnectionsResponse(BaseModel):
    """Response model for listing connections."""

    user_id: str = Field(..., description="User identifier")
    connections: list[ConnectionStatus] = Field(..., description="List of user connections")

    def __str__(self):
        header = f"User Connections (User ID: {self.user_id}):"
        if not self.connections:
            return f"{header}\n  No connections found"

        connections_list = []
        for conn in self.connections:
            status_info = f"{conn.app_name}: {conn.status}"
            if conn.connected_at:
                status_info += f" (connected: {conn.connected_at})"
            if conn.error_message:
                status_info += f" - Error: {conn.error_message}"
            connections_list.append(status_info)

        connections_str = "\n  ".join(connections_list)
        return f"{header}\n  {connections_str}\n\nTotal connections: {len(self.connections)}"


class CallbackRequest(BaseModel):
    """Request model for OAuth callback."""

    connection_id: str = Field(..., description="Connection identifier")
    code: str = Field(..., description="OAuth authorization code")
    state: str = Field(..., description="OAuth state parameter")
    error: str | None = Field(None, description="OAuth error if any")

    def __str__(self):
        parts = [f"Connection ID: {self.connection_id}", f"State: {self.state}"]
        if self.error:
            parts.append(f"Error: {self.error}")
        else:
            parts.append("Authorization code received")
        return "OAuth Callback:\n  " + "\n  ".join(parts)


class ToolParameter(BaseModel):
    """Model for tool parameter schema."""

    type: str = Field(..., description="Parameter type")
    description: str | None = Field(None, description="Parameter description")
    properties: dict[str, Any] | None = Field(None, description="Properties for object type")
    required: list[str] | None = Field(None, description="Required properties")

    def __str__(self):
        parts = [f"Type: {self.type}"]
        if self.description:
            parts.append(f"Description: {self.description}")
        if self.required:
            parts.append(f"Required fields: {', '.join(self.required)}")
        return "Tool Parameter:\n  " + "\n  ".join(parts)


class Tool(BaseModel):
    """Model for a tool."""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    app_name: str = Field(..., description="App that provides this tool")
    parameters: ToolParameter = Field(..., description="Tool parameters schema")

    def __str__(self):
        return f"Tool: {self.name}\n  App: {self.app_name}\n  Description: {self.description}\n  Parameters: {self.parameters.type}"


class GetToolsRequest(BaseModel):
    """Request model for getting tools."""

    user_id: str = Field(..., description="User identifier")
    app_filter: list[str] | None = Field(None, description="Filter tools by apps")

    def __str__(self):
        parts = [f"User ID: {self.user_id}"]
        if self.app_filter:
            parts.append(f"App Filter: {', '.join(self.app_filter)}")
        else:
            parts.append("App Filter: All apps")
        return "Get Tools Request:\n  " + "\n  ".join(parts)


class GetToolsResponse(BaseModel):
    """Response model for getting tools."""

    user_id: str = Field(..., description="User identifier")
    tools: list[Tool] = Field(..., description="Available tools")
    tool_count: int = Field(..., description="Total number of tools")

    def __str__(self):
        header = f"Available Tools (User ID: {self.user_id}):"
        if not self.tools:
            return f"{header}\n  No tools available"

        tools_by_app = {}
        for tool in self.tools:
            if tool.app_name not in tools_by_app:
                tools_by_app[tool.app_name] = []
            tools_by_app[tool.app_name].append(f"{tool.name}: {tool.description}")

        tools_list = []
        for app_name, app_tools in tools_by_app.items():
            tools_list.append(f"{app_name}:")
            for tool_info in app_tools:
                tools_list.append(f"  • {tool_info}")

        tools_str = "\n  ".join(tools_list)
        return f"{header}\n  {tools_str}\n\nTotal tools: {self.tool_count}"


class ListAppsResponse(BaseModel):
    """Response model for listing apps."""

    enabled_apps: list[str] = Field(..., description="List of enabled app names")
    total_enabled: int = Field(..., description="Total number of enabled apps")
    available_apps: list[str] | None = Field(None, description="List of all available apps (if requested)")
    total_available: int | None = Field(None, description="Total number of available apps (if requested)")

    def __str__(self):
        header = "App Status:"
        parts = [f"Enabled Apps ({self.total_enabled}): {', '.join(self.enabled_apps) if self.enabled_apps else 'None'}"]

        if self.available_apps is not None:
            parts.append(f"Available Apps ({self.total_available}): {', '.join(self.available_apps)}")

        return f"{header}\n  " + "\n  ".join(parts)


class AppEnabledResponse(BaseModel):
    """Response model for checking if an app is enabled."""

    app_name: str = Field(..., description="App name (uppercase)")
    enabled: bool = Field(..., description="Whether the app is enabled")
    message: str = Field(..., description="Status message")

    def __str__(self):
        status = "✓ Enabled" if self.enabled else "✗ Disabled"
        return f"App Status Check:\n  App: {self.app_name}\n  Status: {status}\n  Message: {self.message}"


class SetAppEnabledResponse(BaseModel):
    """Response model for enabling/disabling an app."""

    app_name: str = Field(..., description="App name (uppercase)")
    enabled: bool = Field(..., description="Whether the app is now enabled")
    message: str = Field(..., description="Status message")
    updated_at: datetime = Field(..., description="Timestamp of the update")

    def __str__(self):
        status = "✓ Enabled" if self.enabled else "✗ Disabled"
        return f"App Status Update:\n  App: {self.app_name}\n  New Status: {status}\n  Message: {self.message}\n  Updated: {self.updated_at}"
