"""Integration resource for Lumnis SDK."""

from __future__ import annotations

from ..models.integrations import (
    AppEnabledResponse,
    CallbackRequest,
    ConnectionStatus,
    GetToolsRequest,
    GetToolsResponse,
    InitiateConnectionRequest,
    InitiateConnectionResponse,
    ListAppsResponse,
    ListConnectionsResponse,
    SetAppEnabledResponse,
)
from .base import BaseResource


class IntegrationsResource(BaseResource):
    """Resource for managing integrations."""

    async def initiate_connection(
        self,
        *,
        user_id: str,
        app_name: str,
        integration_id: str | None = None,
        redirect_url: str | None = None,
        auth_mode: str | None = None,
        connection_params: dict[str, str | int | bool] | None = None,
    ) -> InitiateConnectionResponse:
        """Initiate a connection to an external app.

        Args:
            user_id: User identifier within tenant
            app_name: App name (e.g., 'GITHUB', 'SLACK') - will be uppercased
            integration_id: Custom integration identifier
            redirect_url: Custom OAuth redirect URL
            auth_mode: Authentication mode (reserved for future use)
            connection_params: Connection parameters (reserved for future use)

        Returns:
            InitiateConnectionResponse containing connection_id and redirect_url
        """
        request_data = InitiateConnectionRequest(
            user_id=user_id,
            app_name=app_name.upper(),
            integration_id=integration_id,
            redirect_url=redirect_url,
            auth_mode=auth_mode,
            connection_params=connection_params,
        )

        response_data = await self._transport.request(
            "POST",
            "/v1/integrations/connections/initiate",
            json=request_data.model_dump(exclude_none=True),
        )

        return InitiateConnectionResponse(**response_data)

    async def get_connection_status(
        self,
        user_id: str,
        app_name: str,
    ) -> ConnectionStatus:
        """Get connection status for a specific app.

        Args:
            user_id: User identifier
            app_name: App name (will be uppercased)

        Returns:
            ConnectionStatus containing app status and connection details
        """
        response_data = await self._transport.request(
            "GET",
            f"/v1/integrations/connections/{user_id}/{app_name.upper()}",
        )

        return ConnectionStatus(**response_data)

    async def list_connections(
        self,
        user_id: str,
        *,
        app_filter: str | None = None,
    ) -> ListConnectionsResponse:
        """List all connections for a user.

        Args:
            user_id: User identifier
            app_filter: Optional comma-separated list of app names to filter

        Returns:
            ListConnectionsResponse containing all user connections
        """
        params = {}
        if app_filter:
            params["app_filter"] = app_filter

        response_data = await self._transport.request(
            "GET",
            f"/v1/integrations/connections/{user_id}",
            params=params,
        )

        return ListConnectionsResponse(**response_data)

    async def callback(
        self,
        *,
        connection_id: str,
        code: str,
        state: str,
        error: str | None = None,
    ) -> dict[str, str | bool]:
        """Handle OAuth callback.

        Args:
            connection_id: Connection identifier
            code: OAuth authorization code
            state: OAuth state parameter
            error: OAuth error if any

        Returns:
            Dictionary with callback processing result
        """
        request_data = CallbackRequest(
            connection_id=connection_id,
            code=code,
            state=state,
            error=error,
        )

        response_data = await self._transport.request(
            "POST",
            "/v1/integrations/connections/callback",
            json=request_data.model_dump(exclude_none=True),
        )

        return response_data

    async def get_tools(
        self,
        *,
        user_id: str,
        app_filter: list[str] | None = None,
    ) -> GetToolsResponse:
        """Get available tools based on user's active connections.

        Args:
            user_id: User identifier
            app_filter: Optional list of app names to filter tools

        Returns:
            GetToolsResponse containing available tools
        """
        request_data = GetToolsRequest(
            user_id=user_id,
            app_filter=[app.upper() for app in app_filter] if app_filter else None,
        )

        response_data = await self._transport.request(
            "POST",
            "/v1/integrations/tools",
            json=request_data.model_dump(exclude_none=True),
        )

        return GetToolsResponse(**response_data)

    async def get_non_oauth_required_fields(
        self,
        app_name: str,
    ) -> dict[str, str | list[dict[str, str]]]:
        """Get required fields for non-OAuth authentication.

        Note: This endpoint is reserved for future use and will return 501 Not Implemented.

        Args:
            app_name: App name (will be uppercased)

        Returns:
            Dictionary containing required fields for API key authentication
        """
        response_data = await self._transport.request(
            "GET",
            f"/v1/integrations/non-oauth/required-fields/{app_name.upper()}",
        )

        return response_data

    # App Management Methods

    async def list_apps(
        self,
        *,
        include_available: bool = True,
    ) -> ListAppsResponse:
        """List apps enabled for the tenant.

        Args:
            include_available: If True, also returns all available apps that could be enabled

        Returns:
            ListAppsResponse containing enabled apps and optionally available apps
        """
        params = {"include_available": include_available}

        response_data = await self._transport.request(
            "GET",
            "/v1/integrations/apps",
            params=params,
        )

        return ListAppsResponse(**response_data)

    async def is_app_enabled(
        self,
        app_name: str,
    ) -> AppEnabledResponse:
        """Check if a specific app is enabled for the tenant.

        Args:
            app_name: App name (e.g., 'github', 'gmail') - case insensitive

        Returns:
            AppEnabledResponse containing enabled status
        """
        response_data = await self._transport.request(
            "GET",
            f"/v1/integrations/apps/{app_name}/enabled",
        )

        return AppEnabledResponse(**response_data)

    async def set_app_enabled(
        self,
        app_name: str,
        *,
        enabled: bool,
    ) -> SetAppEnabledResponse:
        """Enable or disable an app for the tenant.

        Args:
            app_name: App name (e.g., 'github', 'gmail') - case insensitive
            enabled: Whether to enable or disable the app

        Returns:
            SetAppEnabledResponse with updated status
        """
        params = {"enabled": enabled}

        response_data = await self._transport.request(
            "PUT",
            f"/v1/integrations/apps/{app_name}",
            params=params,
        )

        return SetAppEnabledResponse(**response_data)
