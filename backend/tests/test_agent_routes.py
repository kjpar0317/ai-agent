from __future__ import annotations

import json
import uuid

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def test_agent_status_not_found(client: TestClient) -> None:
    rid = uuid.uuid4()
    r = client.get(f"/agent/status/{rid}")
    assert r.status_code == 404


def test_agent_run_stream_and_status(client: TestClient) -> None:
    run_id: uuid.UUID | None = None
    with client.stream("POST", "/agent/run", json={"message": "테스트 요청"}) as stream:
        assert stream.status_code == 200
        for raw in stream.iter_lines():
            if not raw or not raw.startswith("data:"):
                continue
            payload = json.loads(raw.removeprefix("data:").strip())
            if payload.get("kind") == "lifecycle" and payload.get("payload", {}).get("phase") == "run_started":
                run_id = uuid.UUID(payload["payload"]["run_id"])
            if payload.get("kind") == "done":
                break

    assert run_id is not None
    st = client.get(f"/agent/status/{run_id}")
    assert st.status_code == 200
    body = st.json()
    assert body["run_id"] == str(run_id)
    assert body["status"] in ("completed", "failed", "running")
    assert "steps" in body and len(body["steps"]) >= 1
