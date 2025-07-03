from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..types import ModelProvider, ModelType


class ModelPreference(BaseModel):
    """Represents a model preference configuration."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)})

    tenant_id: UUID
    model_type: ModelType
    provider: ModelProvider
    model_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def __str__(self):
        status = "✓ Active" if self.is_active else "✗ Inactive"
        return f"Model Preference:\n  Type: {self.model_type.value}\n  Provider: {self.provider.value}\n  Model: {self.model_name}\n  Status: {status}\n  Updated: {self.updated_at}"


class ModelPreferenceCreate(BaseModel):
    """Request model for creating/updating a model preference."""

    provider: str | ModelProvider
    model_name: str
    model_type: str | ModelType | None = None

    def __str__(self):
        provider_str = self.provider.value if hasattr(self.provider, 'value') else str(self.provider)
        return f"Model Preference Request:\n  Provider: {provider_str}\n  Model: {self.model_name}"


class ModelPreferencesResponse(BaseModel):
    """Response model for getting model preferences."""

    model_config = ConfigDict(json_encoders={UUID: lambda v: str(v)})

    tenant_id: UUID
    preferences: list[ModelPreference]
    defaults_applied: list[ModelType] = Field(default_factory=list)

    def __str__(self):
        header = f"Model Preferences (Tenant: {self.tenant_id}):"
        if not self.preferences:
            return f"{header}\n  No preferences configured"

        prefs_by_type = {}
        for pref in self.preferences:
            prefs_by_type[pref.model_type] = pref

        pref_lines = []
        for model_type in ModelType:
            if model_type in prefs_by_type:
                pref = prefs_by_type[model_type]
                status = "✓" if pref.is_active else "✗"
                pref_lines.append(f"{model_type.value}: {pref.provider.value}:{pref.model_name} {status}")
            elif model_type in self.defaults_applied:
                pref_lines.append(f"{model_type.value}: (using default)")

        prefs_str = "\n  ".join(pref_lines)
        result = f"{header}\n  {prefs_str}"

        if self.defaults_applied:
            result += f"\n\nDefaults applied for: {', '.join([mt.value for mt in self.defaults_applied])}"

        return result


class UpdateModelPreferencesRequest(BaseModel):
    """Request model for updating multiple model preferences."""

    preferences: dict[str, ModelPreferenceCreate]

    def __str__(self):
        header = "Update Model Preferences Request:"
        if not self.preferences:
            return f"{header}\n  No preferences to update"

        pref_lines = []
        for model_type, pref in self.preferences.items():
            provider_str = pref.provider.value if hasattr(pref.provider, 'value') else str(pref.provider)
            pref_lines.append(f"{model_type}: {provider_str}:{pref.model_name}")

        prefs_str = "\n  ".join(pref_lines)
        return f"{header}\n  {prefs_str}"


class ModelAvailability(BaseModel):
    """Model availability check result."""

    model_type: ModelType = Field(description="The type of model (CHEAP_MODEL, FAST_MODEL, etc.)")
    provider: str | ModelProvider
    model_name: str
    is_available: bool
    reason: str | None = None
    requires_api_key: bool

    def __str__(self):
        provider_str = self.provider.value if hasattr(self.provider, 'value') else str(self.provider)
        status = "✓ Available" if self.is_available else "✗ Unavailable"
        api_key = " (API key required)" if self.requires_api_key else ""

        parts = [
            f"Type: {self.model_type.value}",
            f"Model: {provider_str}:{self.model_name}",
            f"Status: {status}{api_key}"
        ]

        if not self.is_available and self.reason:
            parts.append(f"Reason: {self.reason}")

        return "Model Availability:\n  " + "\n  ".join(parts)


class ModelOverrides(BaseModel):
    """Runtime model overrides for response creation."""

    cheap_model: str | None = Field(None, description="Override for cheap model (format: provider:model_name)")
    fast_model: str | None = Field(None, description="Override for fast model (format: provider:model_name)")
    smart_model: str | None = Field(None, description="Override for smart model (format: provider:model_name)")
    reasoning_model: str | None = Field(None, description="Override for reasoning model (format: provider:model_name)")
    vision_model: str | None = Field(None, description="Override for vision model (format: provider:model_name)")

    def __str__(self):
        header = "Model Overrides:"
        overrides = []

        if self.cheap_model:
            overrides.append(f"Cheap Model: {self.cheap_model}")
        if self.fast_model:
            overrides.append(f"Fast Model: {self.fast_model}")
        if self.smart_model:
            overrides.append(f"Smart Model: {self.smart_model}")
        if self.reasoning_model:
            overrides.append(f"Reasoning Model: {self.reasoning_model}")
        if self.vision_model:
            overrides.append(f"Vision Model: {self.vision_model}")

        if not overrides:
            return f"{header}\n  No overrides specified"

        return f"{header}\n  " + "\n  ".join(overrides)


class SupportedModelsResponse(BaseModel):
    """Response model for getting supported models."""

    # Maps model type to list of supported models in "provider:model_name" format
    supported_models: dict[ModelType, list[str]] = Field(
        alias=None,  # The response is the dict itself, not nested
        default_factory=dict
    )

    class Config:
        extra = "allow"  # Allow additional fields

    def __init__(self, **data):
        # If the data contains model types directly, wrap them
        if "supported_models" not in data and any(key in ModelType.__members__ for key in data):
            super().__init__(supported_models=data)
        else:
            super().__init__(**data)

    def __str__(self):
        header = "Supported Models:"
        if not self.supported_models:
            return f"{header}\n  No models available"

        model_lines = []
        for model_type, models in self.supported_models.items():
            if models:
                model_lines.append(f"{model_type.value} ({len(models)}):")
                for model in models:
                    model_lines.append(f"  • {model}")
            else:
                model_lines.append(f"{model_type.value}: No models available")

        models_str = "\n  ".join(model_lines)
        total_models = sum(len(models) for models in self.supported_models.values())
        return f"{header}\n  {models_str}\n\nTotal models: {total_models}"

    @property
    def cheap_models(self) -> list[str]:
        return self.supported_models.get(ModelType.CHEAP_MODEL, [])

    @property
    def fast_models(self) -> list[str]:
        return self.supported_models.get(ModelType.FAST_MODEL, [])

    @property
    def smart_models(self) -> list[str]:
        return self.supported_models.get(ModelType.SMART_MODEL, [])

    @property
    def reasoning_models(self) -> list[str]:
        return self.supported_models.get(ModelType.REASONING_MODEL, [])

    @property
    def vision_models(self) -> list[str]:
        return self.supported_models.get(ModelType.VISION_MODEL, [])
