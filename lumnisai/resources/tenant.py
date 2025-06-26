
from ..models import TenantInfo
from .base import BaseResource


class TenantResource(BaseResource):

    async def get(self) -> TenantInfo:
        if self.tenant_id:
            # Use tenant-specific endpoint when tenant_id is available
            path = f"/v1/tenants/{self.tenant_id}"
        else:
            # Use tenant context from API key authentication
            path = "/v1/tenant"

        response_data = await self._transport.request("GET", path)
        return TenantInfo(**response_data)
