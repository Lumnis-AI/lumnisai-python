
import asyncio
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
from uuid import UUID

from ..constants import DEFAULT_LIMIT, MAX_LIMIT, MAX_LONG_POLL_RETRIES
from ..exceptions import LocalFileNotSupported
from ..models import (
    CancelResponse,
    CreateResponseRequest,
    CreateResponseResponse,
    Message,
    ResponseObject,
)
from .base import BaseResource


class ResponsesResource(BaseResource):

    def _validate_file_reference(self, file_ref: str) -> None:
        # Allow artifact IDs first (before any other checks)
        if file_ref.startswith("artifact_"):
            return  # Always allow artifact IDs, even with slashes
        
        # Parse as URL to check if it's a local file path
        parsed = urlparse(file_ref)
        
        # Define allowed URI schemes for remote files
        allowed_schemes = {
            'http', 'https',        # Web URLs
            's3', 'gs', 'gcs',      # Cloud storage
            'file',                 # Explicit file URIs (allowed for compatibility)
            'ftp', 'ftps',          # FTP
            'blob',                 # Azure blob storage
            'data',                 # Data URIs
        }
        
        # Allow valid URI schemes
        if parsed.scheme:
            if parsed.scheme.lower() in allowed_schemes:
                # Additional validation for specific schemes
                if parsed.scheme.lower() == 'file':
                    # file:// URIs are technically allowed but discouraged
                    pass
                elif parsed.scheme.lower() in ('http', 'https'):
                    # Basic hostname validation for HTTP(S)
                    if not parsed.netloc:
                        raise LocalFileNotSupported(file_ref)
                return
            else:
                # Unknown scheme - might be local or invalid
                raise LocalFileNotSupported(file_ref)
        
        # No scheme - check for local file path indicators
        is_local_path = (
            # Unix absolute paths
            file_ref.startswith("/") or
            # Unix relative paths  
            file_ref.startswith("./") or
            file_ref.startswith("../") or
            # Windows paths (drive letters)
            (len(file_ref) >= 2 and file_ref[1] == ":" and file_ref[0].isalpha()) or
            # Windows UNC paths
            file_ref.startswith("\\\\") or
            # Common filename patterns (basic heuristic)
            (len(file_ref.split("/")) == 1 and "." in file_ref and not file_ref.startswith("artifact_"))
        )
        
        if is_local_path:
            raise LocalFileNotSupported(file_ref)

    async def create(
        self,
        *,
        messages: List[Union[Dict[str, str], Message]],
        user_id: Optional[Union[str, UUID]] = None,
        thread_id: Optional[Union[str, UUID]] = None,
        files: Optional[List[Union[str, Dict[str, Any]]]] = None,
        idempotency_key: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> CreateResponseResponse:
        # Validate files if provided - check for local file paths vs artifact IDs/URIs
        if files:
            for file in files:
                if isinstance(file, str):
                    self._validate_file_reference(file)

        # Convert messages to proper format
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                formatted_messages.append(Message(**msg))
            else:
                formatted_messages.append(msg)

        # Build request payload - Pydantic handles UUID conversion automatically
        request_data = CreateResponseRequest(
            messages=formatted_messages,
            user_id=user_id,
            thread_id=thread_id,
            files=files,
            options=options or {},
        )

        # Make request
        response_data = await self._transport.request(
            "POST",
            "/v1/responses",
            json=request_data.model_dump(exclude_none=True, mode="json"),
            idempotency_key=idempotency_key,
        )

        return CreateResponseResponse(**response_data)

    async def get(
        self,
        response_id: Union[str, UUID],
        *,
        wait: Optional[int] = None,
    ) -> ResponseObject:
        # Build query params
        params = {}
        if wait is not None:
            params["wait"] = wait

        # Make request
        response_data = await self._transport.request(
            "GET",
            f"/v1/responses/{response_id}",
            params=params,
        )

        # Handle long-polling retries
        if wait and response_data.get("status") in ("queued", "in_progress"):
            # The API should handle long-polling, but we can retry if needed
            max_retries = MAX_LONG_POLL_RETRIES
            for _ in range(max_retries):
                await asyncio.sleep(1)
                response_data = await self._transport.request(
                    "GET",
                    f"/v1/responses/{response_id}",
                    params={"wait": min(wait, 30)},
                )
                if response_data.get("status") not in ("queued", "in_progress"):
                    break

        return ResponseObject(**response_data)

    async def cancel(
        self,
        response_id: Union[str, UUID],
    ) -> CancelResponse:
        response_data = await self._transport.request(
            "POST",
            f"/v1/responses/{response_id}/cancel",
        )

        return CancelResponse(**response_data)

    async def list_artifacts(
        self,
        response_id: Union[str, UUID],
        *,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> Dict[str, Any]:
        response_data = await self._transport.request(
            "GET",
            f"/v1/responses/{response_id}/artifacts",
            params={"limit": limit, "offset": offset},
        )

        return response_data