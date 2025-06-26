from typing import Optional, Union
from urllib.parse import quote
from uuid import UUID

from ..models.user import User, UserCreate, UsersListResponse, UserUpdate
from .base import BaseResource


class UsersResource(BaseResource):

    async def create(
        self,
        *,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        user_data = UserCreate(
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        response_data = await self._transport.request(
            "POST",
            "/v1/users",
            json=user_data.model_dump(exclude_none=True),
        )

        return User(**response_data)

    async def get(
        self,
        user_identifier: Union[str, UUID],
    ) -> User:
        # URL encode the identifier if it's an email
        if isinstance(user_identifier, str) and "@" in user_identifier:
            user_identifier = quote(user_identifier, safe="")

        response_data = await self._transport.request(
            "GET",
            f"/v1/users/{user_identifier}",
        )

        return User(**response_data)

    async def update(
        self,
        user_identifier: Union[str, UUID],
        *,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        # URL encode the identifier if it's an email
        if isinstance(user_identifier, str) and "@" in user_identifier:
            user_identifier = quote(user_identifier, safe="")

        update_data = UserUpdate(
            first_name=first_name,
            last_name=last_name,
        )

        response_data = await self._transport.request(
            "PUT",
            f"/v1/users/{user_identifier}",
            json=update_data.model_dump(exclude_none=True),
        )

        return User(**response_data)

    async def delete(
        self,
        user_identifier: Union[str, UUID],
    ) -> None:
        # URL encode the identifier if it's an email
        if isinstance(user_identifier, str) and "@" in user_identifier:
            user_identifier = quote(user_identifier, safe="")

        await self._transport.request(
            "DELETE",
            f"/v1/users/{user_identifier}",
        )

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> UsersListResponse:
        response_data = await self._transport.request(
            "GET",
            "/v1/users",
            params={"page": page, "page_size": min(page_size, 100)},
        )

        return UsersListResponse(**response_data)
