"""
File management resource for the Lumnis AI SDK.

Provides methods for file upload, search, retrieval, and management operations.
Supports both user-scoped and tenant-scoped files with semantic search capabilities.
"""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO
from uuid import UUID

from ..exceptions import (
    FileAccessDeniedError,
    FileNotFoundError,
    LumnisAIError,
)
from ..models.files import (
    BulkDeleteRequest,
    BulkDeleteResponse,
    BulkUploadResponse,
    ContentType,
    DuplicateHandling,
    FileChunk,
    FileContentResponse,
    FileListResponse,
    FileMetadata,
    FileScope,
    FileScopeUpdateRequest,
    FileSearchRequest,
    FileSearchResponse,
    FileUploadResponse,
    ProcessingStatus,
    ProcessingStatusResponse,
)
from .base import BaseResource


class FilesResource(BaseResource):
    """
    Resource for managing files in the Lumnis AI platform.
    
    Handles file operations including:
    - Uploading files (single and bulk)
    - Searching files semantically
    - Retrieving file metadata and content
    - Managing file access scope
    - Deleting files
    """

    @staticmethod
    def _handle_file_error(error: LumnisAIError) -> None:
        """
        Convert generic HTTP errors to file-specific exceptions.
        
        Args:
            error: The original LumnisAIError
            
        Raises:
            FileNotFoundError: If status code is 404
            FileAccessDeniedError: If status code is 403
            LumnisAIError: Re-raises the original error if not file-specific
        """
        if error.status_code == 404:
            raise FileNotFoundError(
                error.message,
                request_id=error.request_id,
                status_code=error.status_code,
                detail=error.detail,
            ) from error
        elif error.status_code == 403:
            raise FileAccessDeniedError(
                error.message,
                request_id=error.request_id,
                status_code=error.status_code,
                detail=error.detail,
            ) from error
        else:
            raise

    # ========================================================================
    # FILE UPLOAD METHODS
    # ========================================================================

    async def upload(
        self,
        *,
        file_path: str | Path | None = None,
        file_content: BinaryIO | bytes | None = None,
        file_name: str | None = None,
        scope: FileScope = FileScope.TENANT,
        user_id: UUID | str | None = None,
        tags: list[str] | str | None = None,
        duplicate_handling: DuplicateHandling = DuplicateHandling.SUFFIX,
    ) -> FileUploadResponse:
        """
        Upload a file for processing and semantic search.
        
        The file will be processed asynchronously. Use get_processing_status()
        to track the processing progress.
        
        Args:
            file_path: Path to the file to upload
            file_content: File content as bytes or file-like object (alternative to file_path)
            file_name: Name for the file (required if using file_content)
            scope: Access scope (USER or TENANT)
            user_id: User ID (required for user-scoped files)
            tags: Tags for categorization (list or comma-separated string)
            duplicate_handling: Strategy for handling duplicate filenames
            
        Returns:
            FileUploadResponse with file_id and initial status
            
        Raises:
            ValueError: If neither file_path nor file_content is provided,
                       or if user_id is missing for user-scoped files
            FileNotFoundError: If file_path doesn't exist
            
        Example:
            # Upload from file path
            response = await client.files.upload(
                file_path="document.pdf",
                scope=FileScope.USER,
                user_id="user-123",
                tags=["research", "important"]
            )
            
            # Upload from bytes
            with open("document.pdf", "rb") as f:
                response = await client.files.upload(
                    file_content=f.read(),
                    file_name="document.pdf",
                    scope=FileScope.TENANT
                )
        """
        # Validate inputs
        if not file_path and not file_content:
            raise ValueError("Either file_path or file_content must be provided")

        if file_content and not file_name:
            raise ValueError("file_name is required when using file_content")

        if scope == FileScope.USER and not user_id:
            raise ValueError("user_id is required for user-scoped files")

        # Read file content if path is provided
        if file_path:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            file_name = file_name or path.name
            with open(path, "rb") as f:
                file_bytes = f.read()
        else:
            # Use provided content
            if isinstance(file_content, bytes):
                file_bytes = file_content
            else:
                file_bytes = file_content.read()  # type: ignore

        # Process tags
        if isinstance(tags, str):
            tags_list = [t.strip() for t in tags.split(",") if t.strip()]
        else:
            tags_list = tags

        # Convert user_id to string if UUID
        user_id_str = str(user_id) if user_id else None

        # Prepare multipart form data
        files = {"file": (file_name, file_bytes)}
        data = {
            "scope": scope.value,
            "duplicate_handling": duplicate_handling.value,
        }

        if user_id_str:
            data["user_id"] = user_id_str
        if tags_list:
            data["tags"] = ",".join(tags_list)

        # Make request
        response_data = await self._transport.request(
            "POST",
            "/v1/files/upload",
            files=files,
            data=data,
        )

        return FileUploadResponse(**response_data)

    async def bulk_upload(
        self,
        *,
        file_paths: list[str | Path] | None = None,
        file_contents: list[tuple[str, BinaryIO | bytes]] | None = None,
        scope: FileScope = FileScope.TENANT,
        user_id: UUID | str | None = None,
        tags: list[str] | str | None = None,
    ) -> BulkUploadResponse:
        """
        Upload multiple files at once.
        
        All files will be processed asynchronously in the background.
        
        Args:
            file_paths: List of file paths to upload
            file_contents: List of (filename, content) tuples (alternative to file_paths)
            scope: Access scope for all files
            user_id: User ID (required for user-scoped files)
            tags: Tags to apply to all files
            
        Returns:
            BulkUploadResponse with upload results
            
        Example:
            response = await client.files.bulk_upload(
                file_paths=["doc1.pdf", "doc2.txt", "doc3.docx"],
                scope=FileScope.TENANT,
                tags=["batch-upload"]
            )
            print(f"Uploaded: {response.total_uploaded}, Failed: {response.total_failed}")
        """
        if not file_paths and not file_contents:
            raise ValueError("Either file_paths or file_contents must be provided")

        if scope == FileScope.USER and not user_id:
            raise ValueError("user_id is required for user-scoped files")

        # Prepare file data
        files_data = []
        if file_paths:
            for path in file_paths:
                p = Path(path)
                if not p.exists():
                    raise FileNotFoundError(f"File not found: {path}")
                with open(p, "rb") as f:
                    files_data.append(("files", (p.name, f.read())))
        else:
            for file_name, file_content in file_contents:  # type: ignore
                if isinstance(file_content, bytes):
                    files_data.append(("files", (file_name, file_content)))
                else:
                    files_data.append(("files", (file_name, file_content.read())))

        # Process tags
        if isinstance(tags, str):
            tags_list = [t.strip() for t in tags.split(",") if t.strip()]
        else:
            tags_list = tags

        # Convert user_id to string if UUID
        user_id_str = str(user_id) if user_id else None

        # Prepare form data
        data = {"scope": scope.value}
        if user_id_str:
            data["user_id"] = user_id_str
        if tags_list:
            data["tags"] = ",".join(tags_list)

        # Make request
        response_data = await self._transport.request(
            "POST",
            "/v1/files/bulk-upload",
            files=files_data,
            data=data,
        )

        return BulkUploadResponse(**response_data)

    # ========================================================================
    # FILE RETRIEVAL METHODS
    # ========================================================================

    async def get(
        self,
        file_id: UUID | str,
        *,
        user_id: UUID | str | None = None,
    ) -> FileMetadata:
        """
        Get file metadata by ID.
        
        Returns detailed information about a file including processing status,
        size, and access scope.
        
        Args:
            file_id: File ID to retrieve
            user_id: User ID for access validation (required for user-scoped files)
            
        Returns:
            FileMetadata object with complete file information
            
        Raises:
            FileNotFoundError: If the file does not exist
            FileAccessDeniedError: If access to the file is denied
            
        Example:
            metadata = await client.files.get("file-id-123")
            print(f"File: {metadata.file_name}")
            print(f"Status: {metadata.processing_status}")
            print(f"Progress: {metadata.progress_percentage}%")
        """
        params = {}
        if user_id:
            params["user_id"] = str(user_id)

        try:
            response_data = await self._transport.request(
                "GET",
                f"/v1/files/{file_id}",
                params=params,
            )
            return FileMetadata(**response_data)
        except LumnisAIError as e:
            self._handle_file_error(e)

    async def list(
        self,
        *,
        user_id: UUID | str | None = None,
        scope: FileScope | None = None,
        file_type: str | None = None,
        status: ProcessingStatus | None = None,
        tags: list[str] | str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> FileListResponse:
        """
        List files with optional filters and pagination.
        
        Returns a paginated list of files accessible to the user.
        
        Args:
            user_id: Filter by user ID
            scope: Filter by file scope (USER or TENANT)
            file_type: Filter by file extension (e.g., "pdf", "txt")
            status: Filter by processing status
            tags: Filter by tags (list or comma-separated string)
            page: Page number (starts at 1)
            limit: Number of files per page (max 100)
            
        Returns:
            FileListResponse with paginated file list
            
        Example:
            # List all completed PDF files
            response = await client.files.list(
                file_type="pdf",
                status=ProcessingStatus.COMPLETED,
                page=1,
                limit=20
            )
            
            for file in response.files:
                print(f"{file.file_name} - {file.file_size} bytes")
        """
        params = {
            "page": page,
            "limit": min(limit, 100),
        }

        if user_id:
            params["user_id"] = str(user_id)
        if scope:
            params["scope"] = scope.value
        if file_type:
            params["file_type"] = file_type
        if status:
            params["status"] = status.value
        if tags:
            if isinstance(tags, str):
                params["tags"] = tags
            else:
                params["tags"] = ",".join(tags)

        response_data = await self._transport.request(
            "GET",
            "/v1/files/",
            params=params,
        )

        return FileListResponse(**response_data)

    async def get_content(
        self,
        file_id: UUID | str,
        *,
        user_id: UUID | str | None = None,
        content_type: ContentType | None = None,
        start_line: int | None = None,
        end_line: int | None = None,
    ) -> FileContentResponse:
        """
        Get file content.
        
        Retrieves the text content of a file. For text files, can retrieve
        specific line ranges. For multimodal files (audio/video/images),
        returns transcripts or AI-generated summaries.
        
        Args:
            file_id: File ID to retrieve content from
            user_id: User ID for access validation
            content_type: Type of content to retrieve (TEXT, TRANSCRIPT, SUMMARY, etc.)
            start_line: Starting line number (for text files)
            end_line: Ending line number (for text files)
            
        Returns:
            FileContentResponse with file content
            
        Example:
            # Get full text content
            content = await client.files.get_content("file-id-123")
            print(content.text)
            
            # Get specific line range
            content = await client.files.get_content(
                "file-id-123",
                start_line=10,
                end_line=20
            )
        """
        params = {}
        if user_id:
            params["user_id"] = str(user_id)
        if content_type:
            params["content_type"] = content_type.value
        if start_line:
            params["start_line"] = start_line
        if end_line:
            params["end_line"] = end_line

        response_data = await self._transport.request(
            "GET",
            f"/v1/files/{file_id}/content",
            params=params,
        )

        return FileContentResponse(**response_data)

    async def download(
        self,
        file_id: UUID | str,
        *,
        user_id: UUID | str | None = None,
        save_path: str | Path | None = None,
    ) -> bytes | None:
        """
        Download the original file.
        
        For files stored in blob storage, this will fetch the original file.
        For text files, returns the text content.
        
        Args:
            file_id: File ID to download
            user_id: User ID for access validation
            save_path: Optional path to save the file to
            
        Returns:
            File content as bytes if save_path is None, otherwise None
            
        Example:
            # Download to bytes
            content = await client.files.download("file-id-123")
            
            # Download to file
            await client.files.download(
                "file-id-123",
                save_path="downloaded_file.pdf"
            )
        """
        params = {}
        if user_id:
            params["user_id"] = str(user_id)

        response_data = await self._transport.request(
            "GET",
            f"/v1/files/{file_id}/download",
            params=params,
            raw_response=True,
        )

        # If it's a redirect response, follow it
        # Otherwise return the content
        if isinstance(response_data, bytes):
            if save_path:
                path = Path(save_path)
                path.write_bytes(response_data)
                return None
            return response_data

        # For redirects, the transport should handle following them
        return response_data  # type: ignore

    # ========================================================================
    # FILE SEARCH METHODS
    # ========================================================================

    async def search(
        self,
        query: str,
        *,
        user_id: UUID | str | None = None,
        limit: int = 10,
        min_score: float = 0.0,
        file_types: list[str] | None = None,
        tags: list[str] | str | None = None,
    ) -> FileSearchResponse:
        """
        Perform semantic search across files.
        
        Uses vector embeddings to find files containing content similar to the query.
        Returns the most relevant files and their matching chunks.
        
        Args:
            query: Search query text
            user_id: User ID for access filtering
            limit: Maximum number of results to return (max 50)
            min_score: Minimum similarity score threshold (0.0 to 1.0)
            file_types: Filter by file extensions (e.g., ["pdf", "txt"])
            tags: Filter by tags
            
        Returns:
            FileSearchResponse with matching files and chunks
            
        Example:
            # Search for files about machine learning
            results = await client.files.search(
                "machine learning algorithms",
                limit=5,
                min_score=0.7
            )
            
            for result in results.results:
                print(f"File: {result.file.file_name}")
                print(f"Relevance: {result.overall_score:.2f}")
                for chunk in result.chunks:
                    print(f"  Chunk: {chunk.chunk_text[:100]}...")
        """
        # Process tags
        tags_list = None
        if tags:
            if isinstance(tags, str):
                tags_list = [t.strip() for t in tags.split(",") if t.strip()]
            else:
                tags_list = tags

        request_data = FileSearchRequest(
            query=query,
            user_id=UUID(str(user_id)) if user_id else None,
            limit=min(limit, 50),
            min_score=min_score,
            file_types=file_types,
            tags=tags_list,
        )

        response_data = await self._transport.request(
            "POST",
            "/v1/files/search",
            json=request_data.model_dump(exclude_none=True, mode="json"),
        )

        return FileSearchResponse(**response_data)

    # ========================================================================
    # FILE MANAGEMENT METHODS
    # ========================================================================

    async def update_scope(
        self,
        file_id: UUID | str,
        *,
        scope: FileScope,
        user_id: UUID | str | None = None,
    ) -> FileMetadata:
        """
        Change the access scope of a file.
        
        Only the file owner can change the scope. Allows converting between
        user-scoped and tenant-scoped files.
        
        Args:
            file_id: File ID to update
            scope: New access scope
            user_id: User ID performing the update (required)
            
        Returns:
            Updated FileMetadata
            
        Example:
            # Change file from user-scoped to tenant-scoped
            updated_file = await client.files.update_scope(
                "file-id-123",
                scope=FileScope.TENANT,
                user_id="user-123"
            )
        """
        request_data = FileScopeUpdateRequest(
            scope=scope,
            user_id=UUID(user_id) if user_id else None,
        )

        response_data = await self._transport.request(
            "PATCH",
            f"/v1/files/{file_id}/scope",
            json=request_data.model_dump(exclude_none=True, mode="json"),
        )

        return FileMetadata(**response_data)

    async def delete(
        self,
        file_id: UUID | str,
        *,
        user_id: UUID | str | None = None,
        hard_delete: bool = True,
    ) -> dict[str, str]:
        """
        Delete a file.
        
        By default, performs a hard delete (permanently removes file, chunks,
        and blob storage). Can optionally perform a soft delete (marks as deleted).
        
        For user-scoped files, only the owner can delete.
        For tenant-scoped files, any authenticated user can delete.
        
        Args:
            file_id: File ID to delete
            user_id: User ID performing deletion (required for user-scoped files)
            hard_delete: If True, permanently deletes; if False, soft deletes
            
        Returns:
            Dict with deletion confirmation
            
        Example:
            # Hard delete (permanent)
            await client.files.delete("file-id-123")
            
            # Soft delete (mark as deleted)
            await client.files.delete("file-id-123", hard_delete=False)
        """
        params = {"hard_delete": hard_delete}
        if user_id:
            params["user_id"] = str(user_id)

        response_data = await self._transport.request(
            "DELETE",
            f"/v1/files/{file_id}",
            params=params,
        )

        return response_data  # type: ignore

    async def bulk_delete(
        self,
        file_ids: list[UUID | str],
        *,
        user_id: UUID | str | None = None,
        hard_delete: bool = True,
    ) -> BulkDeleteResponse:
        """
        Delete multiple files at once.
        
        Performs deletion for all specified files, returning counts of
        successful and failed deletions.
        
        Args:
            file_ids: List of file IDs to delete
            user_id: User ID performing deletion (required for user-scoped files)
            hard_delete: If True, permanently deletes; if False, soft deletes
            
        Returns:
            BulkDeleteResponse with deletion results
            
        Example:
            result = await client.files.bulk_delete(
                ["file-1", "file-2", "file-3"],
                user_id="user-123"
            )
            print(f"Deleted: {result.deleted_count}, Failed: {result.failed_count}")
        """
        request_data = BulkDeleteRequest(
            file_ids=[UUID(fid) if isinstance(fid, str) else fid for fid in file_ids]
        )

        params = {"hard_delete": hard_delete}
        if user_id:
            params["user_id"] = str(user_id)

        response_data = await self._transport.request(
            "DELETE",
            "/v1/files/bulk",
            json=request_data.model_dump(exclude_none=True, mode="json"),
            params=params,
        )

        return BulkDeleteResponse(**response_data)

    # ========================================================================
    # FILE PROCESSING STATUS METHODS
    # ========================================================================

    async def get_processing_status(
        self,
        file_id: UUID | str,
        *,
        user_id: UUID | str | None = None,
    ) -> ProcessingStatusResponse:
        """
        Get the processing status of a file.
        
        Returns detailed information about the current processing state,
        progress, and any errors that occurred.
        
        Args:
            file_id: File ID to check status for
            user_id: User ID for access validation
            
        Returns:
            ProcessingStatusResponse with status details
            
        Example:
            status = await client.files.get_processing_status("file-id-123")
            print(f"Status: {status.status}")
            print(f"Progress: {status.progress_percentage}%")
            if status.error_message:
                print(f"Error: {status.error_message}")
        """
        params = {}
        if user_id:
            params["user_id"] = str(user_id)

        response_data = await self._transport.request(
            "GET",
            f"/v1/files/{file_id}/status",
            params=params,
        )

        return ProcessingStatusResponse(**response_data)
