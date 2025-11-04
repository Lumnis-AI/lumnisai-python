from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID
import json

from pydantic import BaseModel, ConfigDict, Field

from .agent_config import AgentConfig
from .model_preferences import ModelOverrides


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
    
    def __str__(self):
        return f"{self.role.upper()} Message: \n {self.content}"

class ProgressEntry(BaseModel):
    ts: datetime = Field(description="Timestamp")
    state: str = Field(description="Current state (e.g. 'processing', 'completed', 'failed')")
    message: str
    output_text: str | None = None
    tool_calls: list[dict[str, Any]] | None = None

    def __str__(self):
        pe_str = f"{self.ts.isoformat()} - {self.state.upper()} {self.message}"
        if self.tool_calls:
            for tool_call in self.tool_calls:
                pe_str += f"\nTool Call: {json.dumps(tool_call, indent=4)}"
        return pe_str

class ArtifactPart(BaseModel):
    kind: str
    text: str
    metadata: dict[str, Any] | None = Field(default_factory=dict)

class Artifact(BaseModel):
    artifactId: str
    name: str
    description: str
    parts: list[ArtifactPart]
    metadata: dict[str, Any] = Field(default_factory=dict)
    extensions: list[Any] = Field(default_factory=list)

class CreateResponseRequest(BaseModel):
    thread_id: UUID | None = Field(None, description="Optional thread ID for conversation continuity")
    messages: list[Message] = Field(..., min_length=1, description="Input messages")
    user_id: str | None = Field(None, description="Optional user ID for tracking")
    response_format: dict[str, Any] | None = Field(None, description="JSON Schema to structure the response output")
    response_format_instructions: str | None = Field(None, description="Additional instructions for how to format the structured response")
    model_overrides: ModelOverrides | None = Field(None, description="Runtime model overrides for this request")
    agent_config: AgentConfig | None = Field(None, description="Agent configuration for customizing agent behavior")

class ResponseObject(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat(), Decimal: lambda v: float(v), UUID: lambda v: str(v)})
    response_id: UUID
    thread_id: UUID
    tenant_id: UUID
    user_id: UUID | None = None
    status: Literal["queued", "in_progress", "succeeded", "failed", "cancelled"]
    progress: list[ProgressEntry] = Field(default_factory=list)

    input_messages: list[Message] | None = None

    output_text: str | None = None  # Main content field from API
    structured_response: dict[str, Any] | None = None  # Structured output that conforms to the provided JSON Schema
    artifacts: list[Artifact] | None = None  # New artifacts field
    error: dict[str, Any] | None = None
    options: dict[str, Any] | None = None  # Request options used for this response

    # Response title (generated after plan creation)
    response_title: str | None = None  # Human-readable title for the response

    # Timestamps
    created_at: datetime
    completed_at: datetime | None = None

    @property
    def content(self) -> str | None:
        return self.output_text
    
    def __str__(self):
        return f"Response ID: {self.response_id}\nThread ID: {self.thread_id}\nStatus: {self.status}\nCreated At: {self.created_at}\nCompleted At: {self.completed_at}"

    @property
    def plan(self) -> str | None:
        """Extract the plan from the progress entries."""
        if len(self.progress) < 2:
            return None
        
        progress_entry = self.progress[1]
        if progress_entry.tool_calls is None or len(progress_entry.tool_calls) == 0:
            return None
        
        tool_call = progress_entry.tool_calls[0]
        if tool_call.get('output_text') is None:
            return None
        
        return tool_call['output_text']
    
    @property
    def sub_agent_executions(self) -> list[dict[str, Any]]:
        """Extract sub-agent executions from the progress entries."""
        return [sa_execution for sa_execution in self.progress if sa_execution.tool_calls and 'name' in sa_execution.tool_calls[-1] and sa_execution.tool_calls[-1]['name'] == "FINAL_RESPONSE"]

class CancelResponse(BaseModel):
    status: Literal["cancelled"]
    message: str


class CreateResponseResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)})

    response_id: UUID
    thread_id: UUID
    status: Literal["queued", "in_progress", "succeeded", "failed", "cancelled"]
    tenant_id: UUID
    created_at: datetime


class ResponseListResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat(), UUID: lambda v: str(v)})
    
    responses: list[ResponseObject]
    total: int
    limit: int
    offset: int


