
from typing import TYPE_CHECKING, TypeVar
from uuid import UUID

if TYPE_CHECKING:
    from .._transport import HTTPTransport

T = TypeVar("T", bound="BaseResource")


class BaseResource:

    def __init__(self, transport: "HTTPTransport", *, tenant_id: UUID | None = None):
        self._transport = transport
        self._tenant_id = tenant_id

    @property
    def tenant_id(self) -> UUID | None:
        return self._tenant_id
