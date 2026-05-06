# AI Agent Setup 동기화본

## 상태
- 기준: 현재 워크스페이스 구현 상태와 동기화됨
- 목적: 계획 대비 실제 구현 결과를 빠르게 확인

## 완료된 항목

### 1) 백엔드 에이전트 코어 (Small Loop)
- `backend/main.py`에 FastAPI 앱/라이프사이클/CORS/`/agent` 라우트 연결 완료
- PydanticAI 에이전트 팩토리 구현 완료:
  - `backend/app/agent/factory.py`
  - Azure OpenAI 설정 시 실모델, 미설정 시 `TestModel` 폴백
- 도구 구현 완료:
  - `backend/app/tools.py`
  - `search_news`(stub), `run_python_analysis`(제한 샌드박스)
- API 구현 완료:
  - `GET /agent/status/{run_id}`
  - `POST /agent/run` (SSE 스트리밍)
  - 파일: `backend/app/routers/agent.py`
- DB 스키마 구현 완료:
  - `agent_runs`, `agent_events`
  - 파일: `backend/app/models.py`, `backend/app/db.py`

### 2) 프런트엔드 에이전틱 UI
- React 19 + Vite + TanStack Query v5 + Jotai 스캐폴딩 완료
  - `frontend/package.json`, `frontend/src/main.tsx`
- 커스텀 훅 구현 완료:
  - `frontend/src/hooks/useAgent.ts`
  - 상태 폴링(`refetchInterval`) + POST SSE 스트림 파싱/동기화
- Agent 단계 시각화 컴포넌트 완료:
  - `frontend/src/components/AgentSteppers.tsx`
  - `ref`를 props로 전달하는 React 19 패턴 반영
- 상태 패널 완료:
  - `frontend/src/components/AgentStatusUsePanel.tsx`
  - Suspense + Query 경계 반영

### 3) 검증 루프 (Self-Correction)
- Validator 에이전트 추가 완료:
  - `backend/app/agent/factory.py` (`ValidationOutcome` 기반)
- 최대 3회 재시도 로직 완료:
  - `backend/app/agent/service.py`
  - 검증 실패 시 피드백을 반영해 재실행, 초과 시 실패 처리
- 검증 기준 파일 완료:
  - `rules.md`

### 4) 모듈 스킬/문서화
- 스킬 모듈화 완료:
  - `.agent/skills/assistant-core/SKILL.md`
  - `.agent/skills/tools-usage/SKILL.md`
- 문서 갱신 완료:
  - `README.md` (루트)
  - `backend/README.md`
  - `frontend/.env.example`

## 검증 결과
- 백엔드 테스트: `backend/tests/test_agent_routes.py` 통과
- 프런트 빌드: `npm run build` 통과

## 환경 변수 체크리스트
- Backend:
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_DEPLOYMENT`
  - `AZURE_OPENAI_API_VERSION` (옵션, 기본값 존재)
  - `DATABASE_URL`
- Frontend:
  - `VITE_API_BASE_URL` (옵션; 비우면 Vite 프록시 사용)

## 다음 권장 작업
- PostgreSQL 실환경 연결 후 마이그레이션(Alembic) 도입
- 프런트 훅(`useAgent.ts`)에 대한 Vitest 단위 테스트 추가
- SSE 이벤트 스키마 고정(타입 강화) 및 이벤트 재생 UX 개선
