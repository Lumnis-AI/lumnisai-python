
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
from .types import ApiKeyMode, ApiProvider, Scope

# Package version
try:
    __version__ = version("lumnisai")
except PackageNotFoundError:
    __version__ = "0.1.0b0"

# Configure logging
logging.getLogger("lumnisai").addHandler(logging.NullHandler())

# Public API
__all__ = [
    # Clients
    "Client",
    "AsyncClient",
    # Enums
    "Scope",
    "ApiProvider",
    "ApiKeyMode",
    # Exceptions
    "LumnisAIError",
    "ErrorCode",
    "TransportError",
    "ValidationError",
    "RateLimitError",
    "AuthenticationError",
    "NotFoundError",
    "MissingUserId",
    "TenantScopeUserIdConflict",
    "NotImplementedYetError",
    "LocalFileNotSupported",
    # Version
    "__version__",
]