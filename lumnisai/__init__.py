
import logging
from importlib.metadata import PackageNotFoundError, version

from .async_client import AsyncClient
from .client import Client
from .exceptions import (
    AuthenticationError,
    ErrorCode,
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
    # Enums
    "ApiKeyMode",
    "ApiProvider",
    # Clients
    "AsyncClient",
    # Exceptions
    "AuthenticationError",
    "Client",
    "ErrorCode",
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
