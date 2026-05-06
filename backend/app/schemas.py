from __future__ import annotations

import uuid
from enum import Enum

from pydantic import BaseModel, Field


class RunStatusEnum(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class AgentStepState(str, Enum):
    pending = "pending"
    active = "active"
    done = "done"
    error = "error"


class AgentStepModel(BaseModel):
    id: str
    label: str
    state: AgentStepState = AgentStepState.pending


class AgentRunRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=32_000)


class AgentEventPublic(BaseModel):
    seq: int
    kind: str
    payload: dict


class AgentStatusResponse(BaseModel):
    run_id: uuid.UUID
    status: RunStatusEnum
    user_message: str
    retry_count: int
    final_output: str | None = None
    error_message: str | None = None
    steps: list[AgentStepModel] = Field(default_factory=list)
    events: list[AgentEventPublic] = Field(default_factory=list)


class ValidationOutcome(BaseModel):
    passed: bool
    violations: list[str] = Field(default_factory=list)
    suggestion: str | None = None
