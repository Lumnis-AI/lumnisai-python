
import logging
from importlib.metadata import PackageNotFoundError, version

from .async_client import AsyncClient
from .client import Client
from .exceptions import (
    AuthenticationError,
    ErrorCode,
    FileAccessDeniedError,
    FileNotFoundError,
    FileOperationError,
    LocalFileNotSupported,
    LumnisAIError,
    MissingUserId,
    NotFoundError,
    NotImplementedYetError,
    RateLimitError,
    TenantScopeUserIdConflict,
    TransportError,
    ValidationError,
)
from .models import (
    AgentConfig,
    AnthropicModels,
    ContentType,
    DeepSeekModels,
    DuplicateHandling,
    FileChunk,
    FileMetadata,
    FileScope,
    FileSearchResult,
    FileSearchResponse,
    GoogleModels,
    Models,
    OpenAIModels,
    ProcessingStatus,
)
from .types import ApiKeyMode, ApiProvider, ModelProvider, ModelType, Scope
from .utils import ProgressTracker, display_progress, format_progress_entry

# Package version
try:
    __version__ = version("lumnisai")
except PackageNotFoundError:
    __version__ = "0.1.0b0"

# Configure logging
logging.getLogger("lumnisai").addHandler(logging.NullHandler())

# Public API
__all__ = [
    # Agent configuration
    "AgentConfig",
    "AnthropicModels",
    "DeepSeekModels",
    # Enums
    "ApiKeyMode",
    "ApiProvider",
    # Clients
    "AsyncClient",
    "Client",
    # File enums and models
    "ContentType",
    "DuplicateHandling",
    "FileChunk",
    "FileMetadata",
    "FileScope",
    "FileSearchResult",
    "FileSearchResponse",
    "GoogleModels",
    "Models",
    "OpenAIModels",
    "ProcessingStatus",
    # Exceptions
    "AuthenticationError",
    "ErrorCode",
    "FileAccessDeniedError",
    "FileNotFoundError",
    "FileOperationError",
    "LocalFileNotSupported",
    "LumnisAIError",
    "MissingUserId",
    "ModelProvider",
    "ModelType",
    "NotFoundError",
    "NotImplementedYetError",
    "RateLimitError",
    "Scope",
    "TenantScopeUserIdConflict",
    "TransportError",
    "ValidationError",
    # Utils
    "ProgressTracker",
    "display_progress",
    "format_progress_entry",
    # Version
    "__version__",
]
