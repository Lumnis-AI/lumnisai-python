
from datetime import datetime
from uuid import UUID

from ..models import (
    ApiKeyModeRequest,
    ApiKeyModeResponse,
    ExternalApiKeyResponse,
    StoreApiKeyRequest,
)
from ..types import ApiKeyMode, ApiProvider
from .base import BaseResource


class ExternalApiKeysResource(BaseResource):

    async def create(
        self,
        *,
        provider: str | ApiProvider,
        api_key: str,
        key_name: str | None = None,
        expires_at: datetime | None = None,
    ) -> ExternalApiKeyResponse:
        """Create/store an external API key (alias for store)."""
        return await self.store(
            provider=provider,
            api_key=api_key,
            key_name=key_name,
            expires_at=expires_at
        )

    async def store(
        self,
        *,
        provider: str | ApiProvider,
        api_key: str,
        key_name: str | None = None,
        expires_at: datetime | None = None,
    ) -> ExternalApiKeyResponse:
        request_data = StoreApiKeyRequest(
            provider=provider.value if isinstance(provider, ApiProvider) else provider,
            api_key=api_key,
            key_name=key_name,
            expires_at=expires_at,
        )

        response_data = await self._transport.request(
            "POST",
            "/v1/external-api-keys",
            json=request_data.model_dump(exclude_none=True, mode="json"),
        )

        return ExternalApiKeyResponse(**response_data)

    async def list(self) -> list[ExternalApiKeyResponse]:
        response_data = await self._transport.request(
            "GET",
            "/v1/external-api-keys",
        )

        return [ExternalApiKeyResponse(**item) for item in response_data]

    async def get(
        self,
        key_id: str | UUID,
    ) -> ExternalApiKeyResponse:
        response_data = await self._transport.request(
            "GET",
            f"/v1/external-api-keys/{key_id}",
        )

        return ExternalApiKeyResponse(**response_data)

    async def delete(
        self,
        provider: str | ApiProvider,
        *,
        key_name: str | None = None,
    ) -> dict[str, str]:
        params = {}
        if key_name:
            params["key_name"] = key_name

        provider_str = provider.value if isinstance(provider, ApiProvider) else provider

        response_data = await self._transport.request(
            "DELETE",
            f"/v1/external-api-keys/{provider_str}",
            params=params,
        )

        return response_data

    async def get_mode(self) -> ApiKeyModeResponse:
        response_data = await self._transport.request(
            "GET",
            "/v1/external-api-keys/mode",
        )

        return ApiKeyModeResponse(**response_data)

    async def set_mode(
        self,
        mode: str | ApiKeyMode,
    ) -> ApiKeyModeResponse:
        request_data = ApiKeyModeRequest(
            mode=mode.value if isinstance(mode, ApiKeyMode) else mode
        )

        response_data = await self._transport.request(
            "PATCH",
            "/v1/external-api-keys/mode",
            json=request_data.model_dump(),
        )

        return ApiKeyModeResponse(**response_data)
