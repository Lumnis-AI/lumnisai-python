from enum import Enum
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field

ModelType = Literal["SMART_MODEL", "REASONING_MODEL", "VISION_MODEL", "CHEAP_MODEL", "FAST_MODEL"]


class AgentMode(str, Enum):
    """Agent execution mode options."""
    AUTO = "auto"
    SINGLE_AGENT = "single_agent"
    MULTI_AGENT = "multi_agent"


class AgentConfig(BaseModel):
    """
    Agent configuration for customizing Lumnis API behavior.
    
    This model allows you to control agent behavior, model selection,
    and enable/disable specific features when creating responses.
    
    Example:
        >>> config = AgentConfig(
        ...     orchestrator_model_type="REASONING_MODEL",
        ...     orchestrator_model_name="anthropic:claude-3-7-sonnet-20250219",
        ...     coordinator_model_type="REASONING_MODEL",
        ...     planner_model_type="SMART_MODEL",
        ...     use_cognitive_tools=True,
        ...     enable_task_validation=True,
        ...     generate_comprehensive_output=False
        ... )
        >>> response = client.invoke("Your task", agent_config=config)
    """
    
    # Model Type Selection
    orchestrator_model_type: ModelType = Field(
        default="REASONING_MODEL",
        description="Model type for orchestration tasks"
    )
    planner_model_type: ModelType = Field(
        default="SMART_MODEL",
        description="Model type for planning tasks"
    )
    coordinator_model_type: ModelType = Field(
        default="REASONING_MODEL",
        description="Model type for coordination tasks"
    )
    
    # Optional Model Name Overrides
    orchestrator_model_name: str | None = Field(
        default=None,
        description="Specific model name for orchestrator (e.g., 'anthropic:claude-3-7-sonnet-20250219')"
    )
    planner_model_name: str | None = Field(
        default=None,
        description="Specific model name for planner (e.g., 'openai:gpt-4o', 'anthropic:claude-3-7-sonnet-20250219')"
    )
    coordinator_model_name: str | None = Field(
        default=None,
        description="Specific model name for coordinator (overrides coordinator_model_type)"
    )
    final_response_model_name: str | None = Field(
        default=None,
        description="Model name for final response generation"
    )
    
    # Feature Flags
    use_cognitive_tools: bool = Field(
        default=True,
        description="Enable/disable cognitive reasoning tools"
    )
    enable_task_validation: bool = Field(
        default=True,
        description="Enable/disable subagent task validation"
    )
    generate_comprehensive_output: bool = Field(
        default=False,
        description="Generate detailed final summary/report"
    )
    agent_mode: AgentMode = Field(
        default=AgentMode.AUTO,
        description="Agent execution mode - auto (planner decides), single_agent (one agent), or multi_agent (multiple agents)"
    )
    
    # Skill Filtering
    skill_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of specific skill IDs to use. If provided, only these skills will be retrieved and used by the agent."
    )
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert to API-compatible dictionary, excluding None values.
        
        Returns:
            Dictionary representation suitable for API requests
        """
        return self.model_dump(exclude_none=True, mode="json")
    
    @classmethod
    def fast_execution(cls) -> "AgentConfig":
        """
        Create a configuration optimized for fast execution.
        
        Disables cognitive tools and validation for speed.
        
        Returns:
            AgentConfig configured for fast execution
        """
        return cls(
            coordinator_model_name="openai:gpt-4o-mini",
            use_cognitive_tools=False,
            enable_task_validation=False,
            generate_comprehensive_output=False
        )
    
    @classmethod
    def deep_reasoning(cls) -> "AgentConfig":
        """
        Create a configuration optimized for complex reasoning tasks.
        
        Uses reasoning models with cognitive tools enabled.
        
        Returns:
            AgentConfig configured for deep reasoning
        """
        return cls(
            coordinator_model_name="openai:o3",
            planner_model_type="REASONING_MODEL",
            use_cognitive_tools=True,
            enable_task_validation=True,
            generate_comprehensive_output=False
        )
    
    @classmethod
    def comprehensive_report(cls) -> "AgentConfig":
        """
        Create a configuration for generating detailed reports.
        
        Enables comprehensive output generation.
        
        Returns:
            AgentConfig configured for comprehensive reports
        """
        return cls(
            coordinator_model_type="REASONING_MODEL",
            use_cognitive_tools=True,
            enable_task_validation=True,
            generate_comprehensive_output=True
        )
    
    @classmethod
    def with_skills(cls, skill_ids: List[str], **kwargs) -> "AgentConfig":
        """
        Create a configuration that uses specific skills.
        
        Args:
            skill_ids: List of skill IDs to use
            **kwargs: Additional configuration options
        
        Returns:
            AgentConfig configured to use specific skills
        """
        return cls(skill_ids=skill_ids, **kwargs)

