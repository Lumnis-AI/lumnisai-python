
import builtins
from uuid import UUID

from ..models import (
    ResponseObject,
    ThreadListResponse,
    ThreadObject,
    UpdateThreadRequest,
)
from .base import BaseResource


class ThreadsResource(BaseResource):

    async def list(
        self,
        *,
        user_id: str | UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ThreadListResponse:
        params = {"limit": limit, "offset": offset}
        if user_id:
            params["user_id"] = str(user_id)

        response_data = await self._transport.request(
            "GET",
            "/v1/threads",
            params=params,
        )

        return ThreadListResponse(**response_data)

    async def get(
        self,
        thread_id: str | UUID,
    ) -> ThreadObject:
        response_data = await self._transport.request(
            "GET",
            f"/v1/threads/{thread_id}",
        )

        return ThreadObject(**response_data)

    async def get_responses(
        self,
        thread_id: str | UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> builtins.list[ResponseObject]:
        response_data = await self._transport.request(
            "GET",
            f"/v1/threads/{thread_id}/responses",
            params={"limit": limit, "offset": offset},
        )

        return [ResponseObject(**item) for item in response_data]

    async def update(
        self,
        thread_id: str | UUID,
        *,
        title: str | None = None,
    ) -> ThreadObject:
        request_data = UpdateThreadRequest(title=title)

        response_data = await self._transport.request(
            "PATCH",
            f"/v1/threads/{thread_id}",
            json=request_data.model_dump(exclude_none=True),
        )

        return ThreadObject(**response_data)
