from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from typing import Any

from pydantic_ai import AgentRunResultEvent
from pydantic_ai.messages import FunctionToolCallEvent, FunctionToolResultEvent
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.factory import build_main_agent, build_validator_agent
from app.config import Settings, get_settings
from app.db import AsyncSessionLocal
from app.models import AgentEvent, AgentRun, RunStatus
from app.schemas import AgentStepModel, AgentStepState, ValidationOutcome


def _sse(data: dict[str, Any]) -> str:
    return f"data: {json.dumps(data, default=str, ensure_ascii=False)}\n\n"


def _safe_stream_event(event: Any) -> dict[str, Any]:
    if isinstance(event, AgentRunResultEvent):
        out = event.result.output
        text = out if isinstance(out, str) else str(out)
        return {"event_kind": "agent_run_result", "output": text}
    if hasattr(event, "model_dump"):
        try:
            return event.model_dump(mode="json")
        except (TypeError, ValueError):
            return {"event_kind": getattr(event, "event_kind", "unknown"), "repr": repr(event)}
    return {"repr": repr(event)}


def _should_persist_stream_event(event: Any) -> bool:
    return isinstance(
        event,
        (AgentRunResultEvent, FunctionToolCallEvent, FunctionToolResultEvent),
    )


async def _append_event(
    session: AsyncSession,
    run_id: uuid.UUID,
    seq: int,
    kind: str,
    payload: dict[str, Any],
) -> None:
    session.add(AgentEvent(run_id=run_id, seq=seq, kind=kind, payload=payload))
    await session.flush()


async def _append_ui_step(
    session: AsyncSession,
    run_id: uuid.UUID,
    seq_holder: list[int],
    step: AgentStepModel,
) -> str:
    seq_holder[0] += 1
    await _append_event(session, run_id, seq_holder[0], "ui_step", step.model_dump())
    await session.commit()
    return _sse({"kind": "ui_step", "payload": step.model_dump()})


async def run_agent_stream(
    run_id: uuid.UUID,
    settings: Settings | None = None,
) -> AsyncIterator[str]:
    settings = settings or get_settings()
    main_agent = build_main_agent(settings)
    validator = build_validator_agent(settings)

    seq_holder = [0]

    try:
        async with AsyncSessionLocal() as session:
            run = await session.get(AgentRun, run_id)
            if run is None:
                yield _sse({"kind": "error", "payload": {"message": "run not found"}})
                return

            user_message = run.user_message

            async def emit(kind: str, payload: dict[str, Any], *, persist: bool = True) -> str:
                seq_holder[0] += 1
                if persist:
                    await _append_event(session, run_id, seq_holder[0], kind, payload)
                    await session.commit()
                return _sse({"kind": kind, "payload": payload})

            yield await emit(
                "lifecycle",
                {"phase": "run_started", "run_id": str(run_id)},
                persist=True,
            )

            yield await _append_ui_step(
                session,
                run_id,
                seq_holder,
                AgentStepModel(id="analyze", label="요청 분석", state=AgentStepState.done),
            )

            yield await _append_ui_step(
                session,
                run_id,
                seq_holder,
                AgentStepModel(id="execute", label="도구/응답 생성", state=AgentStepState.active),
            )

            feedback = ""
            passed = False
            last_violations: list[str] = []

            for attempt in range(3):
                yield await emit(
                    "attempt",
                    {"index": attempt, "max": 3},
                    persist=True,
                )

                prompt = user_message if not feedback else f"{user_message}\n\n[검증 재시도 안내]\n{feedback}"
                final_text = ""

                async for event in main_agent.run_stream_events(prompt):
                    payload = _safe_stream_event(event)
                    yield _sse({"kind": "agent_event", "payload": {"attempt": attempt, "event": payload}})
                    if _should_persist_stream_event(event):
                        yield await emit("stream", {"attempt": attempt, "event": payload}, persist=True)
                    if isinstance(event, AgentRunResultEvent):
                        out = event.result.output
                        final_text = out if isinstance(out, str) else str(out)

                run.final_output = final_text
                await session.commit()

                yield await _append_ui_step(
                    session,
                    run_id,
                    seq_holder,
                    AgentStepModel(id="execute", label="도구/응답 생성", state=AgentStepState.done),
                )

                yield await _append_ui_step(
                    session,
                    run_id,
                    seq_holder,
                    AgentStepModel(id="validate", label="규칙 검증", state=AgentStepState.active),
                )

                v_prompt = (
                    f"User request:\n{user_message}\n\nAgent answer:\n{final_text}\n\n"
                    f"Attempt: {attempt + 1} / 3"
                )
                v_result = await validator.run(v_prompt)
                vo: ValidationOutcome = v_result.output
                last_violations = list(vo.violations)

                yield await emit("validation", vo.model_dump(), persist=True)

                yield await _append_ui_step(
                    session,
                    run_id,
                    seq_holder,
                    AgentStepModel(
                        id="validate",
                        label="규칙 검증",
                        state=AgentStepState.done if vo.passed else AgentStepState.error,
                    ),
                )

                if vo.passed:
                    passed = True
                    run.status = RunStatus.completed.value
                    run.retry_count = attempt
                    await session.commit()
                    break

                run.retry_count = attempt + 1

                feedback = "; ".join(vo.violations)
                if vo.suggestion:
                    feedback += f"\n제안: {vo.suggestion}"
                await session.commit()

                yield await _append_ui_step(
                    session,
                    run_id,
                    seq_holder,
                    AgentStepModel(id="execute", label="도구/응답 생성", state=AgentStepState.active),
                )

            if not passed:
                run.status = RunStatus.failed.value
                run.error_message = "검증 실패: " + ("; ".join(last_violations) if last_violations else "unknown")
                await session.commit()

            yield await emit(
                "lifecycle",
                {
                    "phase": "run_completed",
                    "status": run.status,
                    "passed_validation": passed,
                },
                persist=True,
            )
            yield _sse({"kind": "done", "payload": {"run_id": str(run_id), "status": run.status}})

    except Exception as exc:  # noqa: BLE001
        async with AsyncSessionLocal() as session:
            run = await session.get(AgentRun, run_id)
            if run is not None:
                run.status = RunStatus.failed.value
                run.error_message = str(exc)
                await session.commit()
        yield _sse({"kind": "error", "payload": {"message": str(exc)}})


async def build_status(session: AsyncSession, run_id: uuid.UUID) -> dict[str, Any] | None:
    run = await session.get(AgentRun, run_id)
    if run is None:
        return None

    res = await session.execute(
        select(AgentEvent).where(AgentEvent.run_id == run_id).order_by(AgentEvent.seq.asc())
    )
    events = res.scalars().all()

    by_step_id: dict[str, dict[str, Any]] = {}
    for ev in events:
        if ev.kind == "ui_step":
            sid = ev.payload.get("id")
            if isinstance(sid, str):
                by_step_id[sid] = ev.payload
    order = ["analyze", "execute", "validate"]
    steps = [by_step_id[i] for i in order if i in by_step_id]

    if not steps:
        steps = _default_steps(run.status)

    return {
        "run_id": run.id,
        "status": run.status,
        "user_message": run.user_message,
        "retry_count": run.retry_count,
        "final_output": run.final_output,
        "error_message": run.error_message,
        "steps": steps,
        "events": [{"seq": e.seq, "kind": e.kind, "payload": e.payload} for e in events[-200:]],
    }


def _default_steps(status: str) -> list[dict[str, Any]]:
    if status == RunStatus.pending.value:
        return [
            AgentStepModel(id="analyze", label="요청 분석", state=AgentStepState.pending).model_dump(),
            AgentStepModel(id="execute", label="도구/응답 생성", state=AgentStepState.pending).model_dump(),
            AgentStepModel(id="validate", label="규칙 검증", state=AgentStepState.pending).model_dump(),
        ]
    if status == RunStatus.running.value:
        return [
            AgentStepModel(id="analyze", label="요청 분석", state=AgentStepState.done).model_dump(),
            AgentStepModel(id="execute", label="도구/응답 생성", state=AgentStepState.active).model_dump(),
            AgentStepModel(id="validate", label="규칙 검증", state=AgentStepState.pending).model_dump(),
        ]
    if status == RunStatus.completed.value:
        return [
            AgentStepModel(id="analyze", label="요청 분석", state=AgentStepState.done).model_dump(),
            AgentStepModel(id="execute", label="도구/응답 생성", state=AgentStepState.done).model_dump(),
            AgentStepModel(id="validate", label="규칙 검증", state=AgentStepState.done).model_dump(),
        ]
    return [
        AgentStepModel(id="analyze", label="요청 분석", state=AgentStepState.done).model_dump(),
        AgentStepModel(id="execute", label="도구/응답 생성", state=AgentStepState.error).model_dump(),
        AgentStepModel(id="validate", label="규칙 검증", state=AgentStepState.error).model_dump(),
    ]
