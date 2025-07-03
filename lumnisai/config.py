
import os
from uuid import UUID

from .constants import CUSTOMER_API_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT


class Config:

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        tenant_id: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        # API key
        self.api_key = api_key or os.environ.get("LUMNISAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Set LUMNISAI_API_KEY environment variable or pass api_key parameter."
            )

        # Base URL - default to customer API
        self.base_url = base_url or os.environ.get("LUMNISAI_BASE_URL", CUSTOMER_API_URL)
        self.base_url = self.base_url.rstrip("/")

        # Tenant ID - optional for customer API (extracted from auth context)
        tenant_id_str = tenant_id or os.environ.get("LUMNISAI_TENANT_ID")
        if tenant_id_str:
            try:
                self.tenant_id = UUID(tenant_id_str)
            except ValueError as e:
                raise ValueError(f"Invalid tenant ID format: {tenant_id_str}") from e
        else:
            # Tenant ID is optional - will be extracted from API key context
            self.tenant_id = None

        # HTTP settings
        self.timeout = timeout
        self.max_retries = max_retries
