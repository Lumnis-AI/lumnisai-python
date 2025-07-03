
import re
from enum import Enum
from typing import Any


class ErrorCode(Enum):

    # Transport errors
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT = "TIMEOUT"
    CONNECTION_ERROR = "CONNECTION_ERROR"

    # Authentication errors
    INVALID_API_KEY = "INVALID_API_KEY"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # Validation errors
    MISSING_USER_ID = "MISSING_USER_ID"
    TENANT_SCOPE_USER_ID_CONFLICT = "TENANT_SCOPE_USER_ID_CONFLICT"
    INVALID_SCOPE = "INVALID_SCOPE"
    LOCAL_FILE_NOT_SUPPORTED = "LOCAL_FILE_NOT_SUPPORTED"
    INVALID_PARAMETERS = "INVALID_PARAMETERS"

    # Resource errors
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Not implemented
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"

    # Unknown/generic
    UNKNOWN = "UNKNOWN"


class LumnisAIError(Exception):

    def __init__(
        self,
        message: str,
        *,
        code: ErrorCode | None = None,
        request_id: str | None = None,
        status_code: int | None = None,
        detail: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code or ErrorCode.UNKNOWN
        self.request_id = request_id
        self.status_code = status_code
        self.detail = self._sanitize_detail(detail or {})

    def _sanitize_detail(self, detail: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(detail, dict):
            return {}

        sanitized = {}
        sensitive_keys = {
            'api_key', 'token', 'password', 'secret', 'key', 'authorization',
            'x-api-key', 'bearer', 'auth'
        }

        for key, value in detail.items():
            key_lower = str(key).lower()

            # Skip sensitive keys entirely
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                continue

            # Recursively sanitize nested dicts
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_detail(value)
            elif isinstance(value, str):
                # Sanitize string values that might contain tokens
                sanitized[key] = self._sanitize_string(value)
            elif isinstance(value, list):
                # Sanitize list items
                sanitized[key] = [
                    self._sanitize_detail(item) if isinstance(item, dict)
                    else self._sanitize_string(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_string(self, text: str) -> str:
        if not isinstance(text, str):
            return text

        # Pattern for common token formats
        patterns = [
            r'sk-[a-zA-Z0-9\-_]{20,}',  # API keys starting with sk-
            r'Bearer\s+[a-zA-Z0-9\-_\.]{20,}',  # Bearer tokens
            r'[a-zA-Z0-9\-_]{32,}',  # Long alphanumeric strings (potential tokens)
        ]

        sanitized = text
        for pattern in patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)

        return sanitized


class TransportError(LumnisAIError):

    def __init__(
        self,
        message: str,
        *,
        code: ErrorCode | None = None,
        **kwargs,
    ):
        super().__init__(message, code=code or ErrorCode.NETWORK_ERROR, **kwargs)


class ValidationError(LumnisAIError):

    def __init__(
        self,
        message: str,
        *,
        code: ErrorCode | None = None,
        **kwargs,
    ):
        super().__init__(message, code=code or ErrorCode.INVALID_PARAMETERS, **kwargs)


class RateLimitError(LumnisAIError):

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after: int | None = None,
        **kwargs,
    ):
        super().__init__(message, code=ErrorCode.RATE_LIMIT_EXCEEDED, **kwargs)
        self.retry_after = retry_after


class AuthenticationError(LumnisAIError):

    def __init__(
        self,
        message: str,
        *,
        code: ErrorCode | None = None,
        **kwargs,
    ):
        super().__init__(message, code=code or ErrorCode.UNAUTHORIZED, **kwargs)


class NotFoundError(LumnisAIError):

    def __init__(
        self,
        message: str,
        **kwargs,
    ):
        super().__init__(message, code=ErrorCode.NOT_FOUND, **kwargs)


class MissingUserId(ValidationError):

    def __init__(self):
        super().__init__(
            "user_id is required when scope is USER. Either provide user_id or use scope=TENANT",
            code=ErrorCode.MISSING_USER_ID
        )


class TenantScopeUserIdConflict(ValidationError):

    def __init__(self):
        super().__init__(
            "user_id must not be provided when scope is TENANT",
            code=ErrorCode.TENANT_SCOPE_USER_ID_CONFLICT
        )


class NotImplementedYetError(LumnisAIError):

    def __init__(
        self,
        message: str = "This feature is not yet implemented",
        **kwargs,
    ):
        super().__init__(message, code=ErrorCode.NOT_IMPLEMENTED, **kwargs)


class LocalFileNotSupported(ValidationError):

    def __init__(self, file_path: str):
        super().__init__(
            f"Local file paths are not supported yet: {file_path}. "
            "Please wait for the artifact upload API or use artifact IDs.",
            code=ErrorCode.LOCAL_FILE_NOT_SUPPORTED
        )
