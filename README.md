# AI Agent (React 19 + FastAPI)

자율 에이전트 **Small Loop** 골격: FastAPI에서 PydanticAI 에이전트가 도구를 호출하고, SSE로 이벤트를 흘리며, `rules.md` 기준 검증 에이전트가 최대 3회까지 재시도합니다. 프런트엔드는 Vite + React 19 + TanStack Query + Jotai로 상태를 폴링·스트림 반영합니다.

## 현재 상태

- 기준: `.cursor/plans/ai-agent-setup.md` 동기화본과 일치
- 목적: 계획 대비 실제 구현 완료 범위를 한 번에 확인

### 완료된 항목

#### 1) 백엔드 에이전트 코어 (Small Loop)
- `backend/main.py`에 FastAPI 앱/라이프사이클/CORS/`/agent` 라우트 연결 완료
- `backend/app/agent/factory.py`에서 Azure OpenAI + TestModel 폴백 기반 Agent 구성 완료
- `backend/app/tools.py`에 `search_news`(stub), `run_python_analysis`(제한 샌드박스) 구현 완료
- `backend/app/routers/agent.py`에 `GET /agent/status/{run_id}`, `POST /agent/run`(SSE) 구현 완료
- `backend/app/models.py`, `backend/app/db.py`에 `agent_runs`, `agent_events` 스키마 및 async DB 연결 완료

#### 2) 프런트엔드 에이전틱 UI
- `frontend`에 React 19 + Vite + TanStack Query v5 + Jotai 스캐폴딩 완료
- `frontend/src/hooks/useAgent.ts`에 상태 폴링 + POST SSE 스트림 파싱/캐시 동기화 완료
- `frontend/src/components/AgentSteppers.tsx`에 단계 시각화 및 React 19 ref-props 패턴 반영 완료
- `frontend/src/components/AgentStatusUsePanel.tsx`에 Suspense + Query 기반 상태 패널 구현 완료

#### 3) 검증 루프 (Self-Correction)
- `backend/app/agent/factory.py`에 Validator 에이전트 추가 완료
- `backend/app/agent/service.py`에 검증 실패 시 최대 3회 재시도 로직 구현 완료
- `rules.md` 기반 검증 체크리스트 반영 완료

#### 4) 모듈 스킬/문서화
- `.agent/skills/assistant-core/SKILL.md`, `.agent/skills/tools-usage/SKILL.md` 모듈화 완료
- `backend/README.md`, `frontend/.env.example` 포함 실행/환경 문서 정리 완료

### 검증 결과
- 백엔드: `pytest` 스모크 테스트 통과
- 프런트엔드: `npm run build` 통과

### 환경 변수 체크리스트
- Backend: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`(옵션), `DATABASE_URL`
- Frontend: `VITE_API_BASE_URL` (비우면 Vite 프록시 사용)

## 구조

- [backend/](backend/) — FastAPI, PydanticAI(Azure OpenAI 또는 TestModel), SQLAlchemy(async), `GET /agent/status/{run_id}`, `POST /agent/run`(SSE)
- [frontend/](frontend/) — React 19, TanStack Query v5, Jotai, `src/hooks/useAgent.ts`, `AgentSteppers`
- [.agent/skills/](.agent/skills/) — 런타임에 합쳐지는 모듈 스킬(SKILL.md)
- [rules.md](rules.md) — 검증 에이전트 기준

## 빠른 시작

### 1) 백엔드

```bash
cd backend
python -m pip install -e ".[dev]"
set DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/aiagent
set AZURE_OPENAI_ENDPOINT=https://YOUR.resource.openai.azure.com/
set AZURE_OPENAI_API_KEY=...
set AZURE_OPENAI_DEPLOYMENT=YOUR_DEPLOYMENT
python -m uvicorn main:app --reload --port 8000
```

Azure 변수를 생략하면 **TestModel**만으로도 API·SSE·검증 루프를 로컬에서 돌려볼 수 있습니다. DB를 주지 않으면 기본은 메모리 SQLite(개발용)입니다.

### 2) 프런트엔드

```bash
cd frontend
npm install
npm run dev
```

[frontend/.env.example](frontend/.env.example)의 `VITE_API_BASE_URL`을 비우면 `vite.config.ts`의 프록시가 `/agent`를 `http://127.0.0.1:8000`으로 넘깁니다.

## BMAD-METHOD v6

방법론 CLI·`_bmad/` 설치는 필수는 아닙니다. 계획·산출물은 `.cursor/plans/` 등 기존 워크플로에 두고, 앱 에이전트 지침만 `.agent/skills/`에 모듈화합니다.
