from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.service import build_status, run_agent_stream
from app.db import AsyncSessionLocal, get_db
from app.models import AgentRun, RunStatus
from app.schemas import AgentEventPublic, AgentRunRequest, AgentStatusResponse, AgentStepModel, RunStatusEnum

router = APIRouter()


@router.get("/status/{run_id}", response_model=AgentStatusResponse)
async def get_agent_status(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> AgentStatusResponse:
    raw = await build_status(db, run_id)
    if raw is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="run not found")
    return AgentStatusResponse(
        run_id=raw["run_id"],
        status=RunStatusEnum(raw["status"]),
        user_message=raw["user_message"],
        retry_count=raw["retry_count"],
        final_output=raw["final_output"],
        error_message=raw["error_message"],
        steps=[AgentStepModel.model_validate(s) for s in raw["steps"]],
        events=[AgentEventPublic.model_validate(e) for e in raw["events"]],
    )


@router.post("/run")
async def post_agent_run(body: AgentRunRequest) -> StreamingResponse:
    async with AsyncSessionLocal() as session:
        run = AgentRun(status=RunStatus.running.value, user_message=body.message)
        session.add(run)
        await session.commit()
        await session.refresh(run)
        run_id = run.id

    return StreamingResponse(
        run_agent_stream(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
