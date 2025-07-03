
from ..models import (
    ModelPreferenceCreate,
    ModelPreferencesResponse,
    UpdateModelPreferencesRequest,
)
from ..types import ModelType
from .base import BaseResource


class ModelPreferencesResource(BaseResource):
    """Resource for managing model preferences."""

    async def list(
        self,
        *,
        include_defaults: bool = True
    ) -> ModelPreferencesResponse:
        """
        List model preferences for the tenant.

        Args:
            include_defaults: Whether to include system defaults for unconfigured model types

        Returns:
            ModelPreferencesResponse with preferences and defaults applied
        """
        params = {"include_defaults": include_defaults}

        response_data = await self._transport.request(
            "GET",
            "/v1/model-preferences",
            params=params,
        )

        return ModelPreferencesResponse(**response_data)

    async def update_bulk(
        self,
        preferences: dict[str | ModelType, ModelPreferenceCreate | dict[str, str]]
    ) -> ModelPreferencesResponse:
        """
        Update multiple model preferences at once.

        Args:
            preferences: Dict mapping model types to preference configurations

        Returns:
            ModelPreferencesResponse with updated preferences
        """
        # Convert keys to strings and values to ModelPreferenceCreate if needed
        typed_preferences = {}
        for key, value in preferences.items():
            # Convert key to string (either from string or ModelType enum)
            model_type_str = key if isinstance(key, str) else key.value

            # Convert value to ModelPreferenceCreate if it's a dict
            if isinstance(value, dict):
                # Add the model_type to the value since the API currently requires it
                value_with_type = value.copy()
                value_with_type['model_type'] = model_type_str
                preference = ModelPreferenceCreate(**value_with_type)
            else:
                preference = value
                # Ensure model_type is set if not already
                if not hasattr(preference, 'model_type') or preference.model_type is None:
                    preference.model_type = model_type_str

            typed_preferences[model_type_str] = preference

        request_data = UpdateModelPreferencesRequest(preferences=typed_preferences)

        response_data = await self._transport.request(
            "PUT",
            "/v1/model-preferences",
            json=request_data.model_dump(mode="json"),
        )

        return ModelPreferencesResponse(**response_data)



