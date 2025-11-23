"""Skills resource implementation."""

from typing import Optional
from uuid import UUID

from .base import BaseResource
from ..models.skills import (
    SkillGuideline,
    SkillGuidelineCreate,
    SkillGuidelineListResponse,
    SkillGuidelineUpdate,
)


class SkillsResource(BaseResource):
    """Resource for managing skill guidelines."""

    async def create(
        self,
        *,
        skill_data: SkillGuidelineCreate,
        user_id: Optional[str | UUID] = None,
    ) -> SkillGuideline:
        """Create a new skill guideline.
        
        Args:
            skill_data: The skill guideline data to create
            user_id: Optional user ID for skill ownership
            
        Returns:
            The created skill guideline
        """
        params = {}
        if user_id:
            params["user_id"] = str(user_id)
            
        response = await self._client._request(
            method="POST",
            url=f"{self._client._config.base_url}/v1/skills",
            json=skill_data.model_dump(exclude_none=True),
            params=params,
        )
        return SkillGuideline.model_validate(response)

    async def list(
        self,
        *,
        category: Optional[str] = None,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 50,
    ) -> SkillGuidelineListResponse:
        """List skill guidelines with optional filtering.
        
        Args:
            category: Filter by skill category
            is_active: Filter by active status (default: True)
            page: Page number (default: 1)
            page_size: Items per page (default: 50)
            
        Returns:
            List of skill guidelines with pagination info
        """
        params = {
            "page": page,
            "page_size": page_size,
        }
        if category:
            params["category"] = category
        if is_active is not None:
            params["is_active"] = is_active
            
        response = await self._client._request(
            method="GET",
            url=f"{self._client._config.base_url}/v1/skills",
            params=params,
        )
        return SkillGuidelineListResponse.model_validate(response)

    async def get(self, skill_id: str | UUID) -> SkillGuideline:
        """Get a skill guideline by ID.
        
        Args:
            skill_id: The skill ID to retrieve
            
        Returns:
            The skill guideline
        """
        response = await self._client._request(
            method="GET",
            url=f"{self._client._config.base_url}/v1/skills/{skill_id}",
        )
        return SkillGuideline.model_validate(response)

    async def update(
        self,
        skill_id: str | UUID,
        *,
        updates: SkillGuidelineUpdate,
    ) -> SkillGuideline:
        """Update a skill guideline.
        
        Args:
            skill_id: The skill ID to update
            updates: The updates to apply
            
        Returns:
            The updated skill guideline
        """
        response = await self._client._request(
            method="PUT",
            url=f"{self._client._config.base_url}/v1/skills/{skill_id}",
            json=updates.model_dump(exclude_none=True),
        )
        return SkillGuideline.model_validate(response)

    async def delete(self, skill_id: str | UUID) -> None:
        """Delete a skill guideline.
        
        Args:
            skill_id: The skill ID to delete
        """
        await self._client._request(
            method="DELETE",
            url=f"{self._client._config.base_url}/v1/skills/{skill_id}",
        )