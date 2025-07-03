
import asyncio
import logging
import time
from decimal import Decimal, getcontext
from typing import Any
from urllib.parse import urljoin

import httpx
from httpx import Response

from ..constants import (
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    TENANT_WARNING_BUCKET_CAPACITY,
    TENANT_WARNING_BUCKET_REFILL_RATE,
)
from ..exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    TransportError,
    ValidationError,
)

logger = logging.getLogger("lumnisai.transport")


class TokenBucket:

    def __init__(self, tokens: int, refill_per_minute: int):
        # Set decimal precision for high-accuracy token accounting
        getcontext().prec = 28

        self.capacity = Decimal(tokens)
        self.tokens = Decimal(tokens)  # Use Decimal for precise accounting
        self.refill_per_minute = Decimal(refill_per_minute)
        self.last_refill = Decimal(str(time.time()))
        self._lock = asyncio.Lock()

    async def consume(self, tokens: int = 1) -> bool:
        async with self._lock:
            # Refill tokens based on time passed using high-precision decimal arithmetic
            now = Decimal(str(time.time()))
            elapsed = now - self.last_refill
            refill = (elapsed / Decimal('60')) * self.refill_per_minute

            # Keep tokens as Decimal for precise accounting, but cap at capacity
            self.tokens = min(self.capacity, self.tokens + refill)
            self.last_refill = now

            # Try to consume (convert int parameter to Decimal for comparison)
            tokens_decimal = Decimal(tokens)
            if self.tokens >= tokens_decimal:
                self.tokens -= tokens_decimal
                return True
            return False


class HTTPTransport:

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        # Token bucket for tenant scope warnings
        self.tenant_warning_bucket = TokenBucket(
            TENANT_WARNING_BUCKET_CAPACITY,
            TENANT_WARNING_BUCKET_REFILL_RATE
        )

        # HTTP client with optimized connection pool
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0
            ),
            http2=True,  # Enable HTTP/2 for better performance
            headers={
                "User-Agent": "lumnisai-python/0.1.0b0",
                "Content-Type": "application/json",
            },
        )

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _prepare_request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        url = urljoin(self.base_url, path)

        request_headers = {
            "X-API-Key": self.api_key,
        }
        if headers:
            request_headers.update(headers)

        # Log request (with auth headers redacted)
        log_headers = {k: v if k != "X-API-Key" else "[REDACTED]"
                      for k, v in request_headers.items()}
        logger.debug(f"{method} {url}", extra={"headers": log_headers})

        return {
            "method": method,
            "url": url,
            "headers": request_headers,
            **kwargs,
        }

    async def _handle_response(self, response: Response) -> Any:
        request_id = response.headers.get("X-Request-ID")

        # Success
        if 200 <= response.status_code < 300:
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            return response.text

        # Parse error detail
        detail = {}
        try:
            if response.headers.get("content-type", "").startswith("application/json"):
                detail = response.json()
        except (ValueError, TypeError) as e:
            logger.debug(f"Failed to parse error response as JSON: {e}")
            detail = {"raw": response.text}

        # Map status codes to exceptions
        if response.status_code == 401:
            raise AuthenticationError(
                "Invalid or missing API key",
                request_id=request_id,
                status_code=401,
                detail=detail,
            )
        elif response.status_code == 403:
            raise AuthenticationError(
                "Forbidden - insufficient permissions",
                request_id=request_id,
                status_code=403,
                detail=detail,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                "Resource not found",
                request_id=request_id,
                status_code=404,
                detail=detail,
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                request_id=request_id,
                status_code=429,
                detail=detail,
                retry_after=int(retry_after) if retry_after else None,
            )
        elif 400 <= response.status_code < 500:
            error_msg = detail.get("error", {}).get("message", "Validation error")
            raise ValidationError(
                error_msg,
                request_id=request_id,
                status_code=response.status_code,
                detail=detail,
            )
        else:
            raise TransportError(
                f"Server error: {response.status_code}",
                request_id=request_id,
                status_code=response.status_code,
                detail=detail,
            )

    async def request(
        self,
        method: str,
        path: str,
        *,
        idempotency_key: str | None = None,
        **kwargs,
    ) -> Any:
        # Add idempotency key if provided
        headers = kwargs.pop("headers", {})
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        # Prepare request
        request_params = self._prepare_request(
            method, path, headers=headers, **kwargs
        )

        # Determine if request is idempotent
        is_idempotent = method in ("GET", "HEAD", "OPTIONS") or idempotency_key is not None
        max_attempts = self.max_retries + 1 if is_idempotent else 1

        last_error = None
        first_server_error = None  # Track first 5xx error separately

        for attempt in range(max_attempts):
            try:
                response = await self.client.request(**request_params)
                return await self._handle_response(response)

            except (httpx.NetworkError, httpx.TimeoutException) as e:
                last_error = TransportError(
                    f"Network error: {e!s}",
                    status_code=None,
                )

            except TransportError as e:
                # Track first server error with status code info
                if e.status_code and e.status_code >= 500:
                    if first_server_error is None:
                        first_server_error = e
                    last_error = e
                else:
                    # Don't retry non-5xx errors
                    raise

            except Exception as e:
                # Don't retry other exceptions - log and re-raise
                logger.debug(f"Non-retryable exception during request: {type(e).__name__}: {e}")
                raise

            # Calculate backoff
            if attempt < max_attempts - 1:
                backoff = self.backoff_factor * (2 ** attempt)
                logger.debug(f"Retrying request (attempt {attempt + 1}/{max_attempts}) after {backoff}s")
                await asyncio.sleep(backoff)

        # All retries failed - prefer first server error with status code over network errors
        raise first_server_error or last_error or TransportError("Request failed after all retries")

    async def warmup(self):
        try:
            await self.request("GET", "/v1/health", timeout=5.0)
        except Exception:
            pass  # Ignore warmup failures

    async def warn_tenant_scope(self):
        if await self.tenant_warning_bucket.consume():
            logging.getLogger("lumnisai.scoping").warning(
                "Using TENANT scope bypasses user isolation. "
                "Ensure this is intentional and follows security best practices."
            )
