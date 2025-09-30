"""
File management models for the Lumnis AI SDK.

This module provides data models for file operations including upload,
search, retrieval, and management.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# ENUMS
# ============================================================================


class ProcessingStatus(str, Enum):
    """
    Status of file processing operations.
    
    Files progress through different processing stages:
    - PENDING: Queued for processing
    - PARSING: Extracting content from file
    - EMBEDDING: Generating vector embeddings
    - COMPLETED: Successfully processed
    - PARTIAL_SUCCESS: Completed with some errors
    - ERROR: Processing failed
    """

    PENDING = "pending"
    PARSING = "parsing"
    EMBEDDING = "embedding"
    COMPLETED = "completed"
    PARTIAL_SUCCESS = "partial_success"
    ERROR = "error"


class FileScope(str, Enum):
    """
    Access scope for files.
    
    - USER: File is accessible only to the user who uploaded it
    - TENANT: File is accessible to all users within the tenant
    """

    USER = "user"
    TENANT = "tenant"


class ContentType(str, Enum):
    """
    Type of content representation stored for a file.
    
    - TEXT: Direct text extraction from file
    - TRANSCRIPT: Transcription from audio/video
    - SUMMARY: AI-generated summary
    - STRUCTURED: Structured data (e.g., from spreadsheets)
    """

    TEXT = "text"
    TRANSCRIPT = "transcript"
    SUMMARY = "summary"
    STRUCTURED = "structured"


class DuplicateHandling(str, Enum):
    """
    Strategy for handling duplicate filenames during upload.
    
    - ERROR: Raise an error if duplicate exists
    - SKIP: Skip upload if duplicate exists
    - REPLACE: Replace the existing file
    - SUFFIX: Add numeric suffix (e.g., file_(1).txt)
    """

    ERROR = "error"
    SKIP = "skip"
    REPLACE = "replace"
    SUFFIX = "suffix"


# ============================================================================
# REQUEST MODELS
# ============================================================================


class FileUploadRequest(BaseModel):
    """
    Parameters for file upload operation.
    
    Note: The actual file content is sent as multipart/form-data,
    this model represents additional parameters.
    """

    scope: FileScope = Field(..., description="Access scope for the uploaded file")
    user_id: UUID | None = Field(None, description="User ID (required for user-scoped files)")
    tags: list[str] | None = Field(None, description="Tags for categorizing the file")
    duplicate_handling: DuplicateHandling = Field(
        default=DuplicateHandling.SUFFIX,
        description="Strategy for handling duplicate filenames",
    )

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate and clean tag values."""
        if v:
            cleaned_tags = []
            for tag in v:
                tag = tag.strip().lower()
                if not tag:
                    continue
                if len(tag) > 50:
                    raise ValueError(f"Tag too long (max 50 chars): {tag}")
                cleaned_tags.append(tag)

            if len(cleaned_tags) > 10:
                raise ValueError("Too many tags (max 10)")

            return cleaned_tags if cleaned_tags else None
        return None


class FileSearchRequest(BaseModel):
    """Parameters for semantic file search."""

    query: str = Field(..., min_length=1, description="Search query text")
    limit: int | None = Field(default=10, ge=1, le=50, description="Maximum number of results")
    min_score: float | None = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score threshold",
    )
    file_types: list[str] | None = Field(None, description="Filter by file extensions")
    tags: list[str] | None = Field(None, description="Filter by tags")
    user_id: UUID | None = Field(None, description="User ID for access filtering")


class BulkDeleteRequest(BaseModel):
    """Parameters for bulk file deletion."""

    file_ids: list[UUID] = Field(..., min_length=1, description="List of file IDs to delete")


class FileScopeUpdateRequest(BaseModel):
    """Parameters for updating file access scope."""

    scope: FileScope = Field(..., description="New access scope for the file")
    user_id: UUID | None = Field(None, description="User ID performing the update")


class FileContentRequest(BaseModel):
    """Parameters for retrieving specific file content."""

    content_type: ContentType | None = Field(None, description="Type of content to retrieve")
    start_line: int | None = Field(None, ge=1, description="Starting line number")
    end_line: int | None = Field(None, ge=1, description="Ending line number")

    @field_validator("end_line")
    @classmethod
    def validate_line_range(cls, v: int | None, info) -> int | None:
        """Ensure end_line is greater than start_line."""
        if v and info.data.get("start_line"):
            if v < info.data["start_line"]:
                raise ValueError("end_line must be greater than or equal to start_line")
        return v


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class FileMetadata(BaseModel):
    """
    Complete metadata for a file.
    
    Contains information about the file, its processing status,
    and access control details.
    """

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)})

    id: UUID
    tenant_id: UUID
    user_id: UUID | None
    file_name: str
    original_file_name: str
    file_type: str
    mime_type: str
    file_size: int
    file_scope: FileScope
    blob_url: str | None
    processing_status: ProcessingStatus
    error_message: str | None
    total_chunks: int
    chunks_embedded: int
    tags: list[str] | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @property
    def progress_percentage(self) -> float:
        """Calculate processing progress as a percentage."""
        if self.total_chunks == 0:
            return 0.0 if self.chunks_embedded == 0 else 100.0
        return min((self.chunks_embedded / self.total_chunks) * 100, 100.0)


class FileUploadResponse(BaseModel):
    """Response after successful file upload."""

    file_id: UUID
    file_name: str
    status: ProcessingStatus
    message: str = "File uploaded successfully"


class FileContentResponse(BaseModel):
    """Response containing file content."""

    file_id: UUID
    content_type: ContentType
    text: str
    metadata: dict[str, Any] | None = None
    start_line: int | None = None
    end_line: int | None = None
    total_lines: int | None = None


class FileChunk(BaseModel):
    """
    A single chunk of a file with optional similarity score.
    
    Represents a segment of a file that has been processed
    and embedded for semantic search.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    chunk_index: int
    chunk_text: str
    start_line: int | None
    end_line: int | None
    token_count: int | None
    metadata: dict[str, Any] | None
    similarity_score: float | None = Field(None, description="Similarity score from search")

    def __str__(self) -> str:
        """Format chunk for display."""
        lines = []
        score_str = f"{self.similarity_score:.3f}" if self.similarity_score else "N/A"
        lines.append(f"Chunk {self.chunk_index} (Score: {score_str})")
        if self.start_line and self.end_line:
            lines.append(f"Lines: {self.start_line}-{self.end_line}")
        lines.append(f"Content: {self.chunk_text}")
        if self.metadata:
            lines.append("--------------------------------")
            lines.append("Metadata:")
            for key, value in self.metadata.items():
                lines.append(f"  {key}={value}")
        return "\n".join(lines)


class FileSearchResult(BaseModel):
    """
    Search result containing a file and its matching chunks.
    
    Returned when performing semantic search across files.
    """

    file: FileMetadata
    chunks: list[FileChunk]
    overall_score: float = Field(..., description="Overall relevance score")

    def __str__(self) -> str:
        """Format search result for display."""
        lines = [
            f"File: {self.file.file_name}",
            f"ID: {self.file.id}",
            f"Type: {self.file.file_type}",
            f"Score: {self.overall_score:.3f}",
        ]

        if self.chunks:
            lines.append(f"\nMatching chunks ({len(self.chunks)}):")
            for chunk in self.chunks[:3]:  # Show top 3 chunks
                lines.append(str(chunk))

        return "\n".join(lines)


class FileSearchResponse(BaseModel):
    """Response from file search endpoint."""

    results: list[FileSearchResult]
    total_count: int
    query: str
    processing_time_ms: int | None = None


class ProcessingStatusResponse(BaseModel):
    """Response containing file processing status."""

    status: ProcessingStatus
    progress_percentage: float
    chunks_embedded: int
    total_chunks: int
    estimated_time_remaining_seconds: int | None
    error_message: str | None
    jobs: list[dict[str, Any]] | None = Field(None, description="Processing job details")


class FileListResponse(BaseModel):
    """Response for listing files with pagination."""

    files: list[FileMetadata]
    total_count: int
    page: int
    limit: int
    has_more: bool


class FileStatisticsResponse(BaseModel):
    """Aggregated statistics about files."""

    total_files: int
    total_size_bytes: int
    files_by_type: dict[str, int]
    files_by_status: dict[str, int]
    files_by_scope: dict[str, int]
    average_file_size_bytes: float
    average_processing_time_seconds: float | None
    storage_usage_percentage: float | None


class BulkUploadResponse(BaseModel):
    """Response from bulk file upload operation."""

    uploaded: list[FileUploadResponse]
    failed: list[dict[str, Any]]
    total_uploaded: int
    total_failed: int


class BulkDeleteResponse(BaseModel):
    """Response from bulk file deletion operation."""

    deleted_count: int
    failed_count: int
    message: str
    hard_delete: bool
    total_requested: int
