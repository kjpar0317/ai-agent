# Cursor Plan Mode 기반 AI 에이전트 프로젝트 표준 구조 가이드

> **대상**: Cursor IDE를 활용해 복잡한 프로젝트를 관리하는 프리랜서 개발자  
> **목적**: 에이전트가 길을 잃지 않고 '작은 루프'를 완성하게 만드는 표준 파일 구성 정립  
> **기반**: Cursor 공식 Agent Best Practices (2026.01) + 최신 Changelog 반영  
> **최종 수정**: 2026년 5월 기준

---

> ⚠️ **주요 변경 사항 (구 버전 대비)**
>
> | 구 버전                            | 현재 (2026 기준)                                                              |
> | ---------------------------------- | ----------------------------------------------------------------------------- |
> | `.cursorrules` (단일 파일)         | `.cursor/rules/*.mdc` (스코프별 분리, MDC 포맷) — `.cursorrules`는 deprecated |
> | Plan Mode = 외부 커스텀 워크플로우 | **Plan Mode = Cursor 내장 기능** (`Shift+Tab`)                                |
> | `.agent/skills/` (비공식 관행)     | **Agent Skills = Cursor 공식 기능** (`SKILL.md` + Hooks)                      |
> | 단일 에이전트                      | Background Agents + Parallel Multi-Agent 지원                                 |

---

## 목차

1. [핵심 철학: 왜 이 구조인가?](#1-핵심-철학-왜-이-구조인가)
2. [전체 프로젝트 디렉터리 구조](#2-전체-프로젝트-디렉터리-구조)
3. [각 구성 요소 상세 설명](#3-각-구성-요소-상세-설명)
   - 3-1. `.cursor/plans/` — 에이전트의 기억장치
   - 3-2. `.cursor/rules/` — 에이전트의 헌법 (MDC 포맷)
   - 3-3. `.cursor/hooks.json` — 에이전트 자동화 루프
   - 3-4. Agent Skills (`SKILL.md`) — 에이전트의 동적 도구
   - 3-5. `backend/` — FastAPI + uv 환경
   - 3-6. `frontend/` — React 19 + TanStack 환경
4. [핵심 파일 템플릿 모음](#4-핵심-파일-템플릿-모음)
5. [Plan Mode 실전 워크플로우](#5-plan-mode-실전-워크플로우)
6. [작은 루프 설계 원칙](#6-작은-루프-설계-원칙)
7. [자주 하는 실수와 해결책](#7-자주-하는-실수와-해결책)
8. [빠른 시작 체크리스트](#8-빠른-시작-체크리스트)

---

## 1. 핵심 철학: 왜 이 구조인가?

AI 에이전트는 컨텍스트 창(Context Window)이라는 근본적인 제약이 있습니다. 에이전트는 대화가 길어지거나 세션이 바뀌면 이전 작업을 잊어버립니다. 이 구조는 그 문제를 **파일 시스템으로 해결**합니다.

Cursor 공식 블로그(2026.01)는 이렇게 말합니다:

> _"The most impactful change you can make is planning before coding."_

### 세 가지 핵심 원칙

| 원칙            | 설명                                    | 구현 방법             |
| --------------- | --------------------------------------- | --------------------- |
| **상태 외부화** | 에이전트의 기억을 파일에 저장           | `.cursor/plans/`      |
| **규칙 명문화** | 판단 기준을 스코프별 파일로 관리        | `.cursor/rules/*.mdc` |
| **능력 모듈화** | 반복 작업을 동적으로 로딩 가능한 단위로 | `SKILL.md` + Hooks    |

### Plan → Act → Verify 루프

```
[Plan Mode] Shift+Tab으로 진입
    ↓ 에이전트가 코드베이스 탐색 + 질문
    ↓ Markdown 플랜 파일 생성 (편집 가능)
    ↓ "Save to workspace" → .cursor/plans/ 저장
[Agent Mode] 플랜 기반 실행
    ↓ 단계별 체크박스 완료 처리
    ↓ 테스트 실행 (uv run pytest)
[Verify] 결과 확인 후 플랜 업데이트
    ↓ 새 세션 시작 시 000-PROJECT-INDEX.md 재로드
```

---

## 2. 전체 프로젝트 디렉터리 구조

```
📂 my-project/
│
├── 📂 .cursor/                          # Cursor 에이전트 전용 설정
│   │
│   ├── 📂 plans/                        # ⭐ 에이전트의 기억장치
│   │   ├── 📄 000-PROJECT-INDEX.md      # 모든 계획 파일의 목차 및 상태 요약
│   │   ├── 📄 001-setup.md
│   │   ├── 📄 002-agent-loop.md
│   │   └── 📄 TEMPLATE-plan.md          # 새 계획 작성 시 복사할 템플릿
│   │
│   ├── 📂 rules/                        # ⭐ 에이전트 규칙 (구 .cursorrules 대체)
│   │   ├── 📄 core.mdc                  # 전역 규칙 (alwaysApply: true)
│   │   ├── 📄 backend.mdc               # Python/FastAPI 규칙 (glob: backend/**)
│   │   ├── 📄 frontend.mdc              # React/TS 규칙 (glob: frontend/**)
│   │   └── 📄 git.mdc                   # Git 워크플로우 규칙
│   │
│   ├── 📄 hooks.json                    # ⭐ 에이전트 자동화 훅 (Stop Hook 등)
│   └── 📄 scratchpad.md                 # 에이전트 반복 루프용 임시 메모
│
├── 📂 .agent/                           # Agent Skills 정의
│   └── 📂 skills/
│       ├── 📂 stock-fetcher/
│       │   ├── 📄 SKILL.md              # 스킬 실행 지침
│       │   └── 📂 scripts/
│       │       └── 📄 fetch_prices.py
│       └── 📂 _template/
│           ├── 📄 SKILL.md
│           └── 📂 scripts/
│               └── 📄 main.py
│
├── 📂 backend/                          # FastAPI 기반 백엔드
│   ├── 📂 app/
│   │   ├── 📄 main.py
│   │   ├── 📂 api/v1/
│   │   ├── 📂 core/
│   │   │   ├── 📄 config.py
│   │   │   └── 📄 deps.py
│   │   ├── 📂 models/
│   │   └── 📂 services/
│   ├── 📂 tests/
│   ├── 📄 pyproject.toml                # uv 환경의 심장
│   ├── 📄 uv.lock
│   └── 📄 .python-version               # 예: 3.12
│
├── 📂 frontend/                         # React 19 + TanStack
│   ├── 📂 src/
│   │   ├── 📂 components/
│   │   ├── 📂 routes/
│   │   ├── 📂 stores/
│   │   └── 📄 main.tsx
│   ├── 📄 package.json
│   ├── 📄 tsconfig.json
│   └── 📄 vite.config.ts
│
├── 📂 docs/
│   └── 📄 architecture.md
│
├── 📄 .env.example
├── 📄 .gitignore
├── 📄 docker-compose.yml
└── 📄 README.md
```

---

## 3. 각 구성 요소 상세 설명

### 3-1. `.cursor/plans/` — 에이전트의 기억장치

Plan Mode의 핵심입니다. **Cursor 공식 기능**으로, `Shift+Tab`을 누르면 에이전트가 자동으로 코드베이스를 탐색하고 플랜을 생성합니다.

#### Plan Mode 동작 방식

```
Shift+Tab 입력
    → 에이전트가 관련 파일 자동 탐색 (grep + semantic search)
    → 요구사항 관련 질문 (clarifying questions)
    → Markdown 플랜 생성 (파일 경로 + 코드 참조 포함)
    → 인라인 Mermaid 다이어그램 자동 생성 (v2.2+)
    → "Save to workspace" 클릭 시 .cursor/plans/에 저장
    → 특정 TODO만 선택해 새 에이전트에게 전달 가능 (v2.2+)
```

> **팁**: 특정 할 일(TODO)만 선택해서 별도 에이전트에게 전달하는 기능이 v2.2에 추가되었습니다. 플랜에서 일부 단계를 골라 병렬 에이전트로 실행할 수 있습니다.

#### 파일 네이밍 규칙

| 패턴                   | 의미                 | 예시                |
| ---------------------- | -------------------- | ------------------- |
| `000-PROJECT-INDEX.md` | 전체 인덱스 (고정)   | —                   |
| `0XX-이름.md`          | 인프라/설정 계획     | `001-setup.md`      |
| `1XX-이름.md`          | 백엔드 기능 계획     | `101-user-auth.md`  |
| `2XX-이름.md`          | 프런트엔드 기능 계획 | `201-dashboard.md`  |
| `3XX-이름.md`          | 에이전트 루프 계획   | `301-stock-loop.md` |

#### 계획 파일 상태값

```
🔴 NOT_STARTED   - 아직 시작 안 함
🟡 IN_PROGRESS   - 현재 진행 중
🟢 COMPLETED     - 완료
⚫ BLOCKED        - 다른 작업에 막힘 (이유 기록)
🔵 REVIEW        - 검토 필요
```

---

### 3-2. `.cursor/rules/` — 에이전트의 헌법 (MDC 포맷)

> ⚠️ **`.cursorrules`는 deprecated입니다.** 2025년 이후 `.cursor/rules/*.mdc` 파일로 이전하세요.
> Cursor에서 `Cmd+Shift+P` → `"New Cursor Rule"` 로 생성할 수 있습니다.

#### MDC 파일 구조

```
---
description: 이 규칙이 언제 적용되는지 설명
globs:
  - backend/**/*.py
alwaysApply: false
---

# 규칙 내용
```

#### 규칙 적용 우선순위

| 타입                                | 저장 위치               | 적용 방식                   |
| ----------------------------------- | ----------------------- | --------------------------- |
| User Rules                          | Cursor Settings > Rules | 모든 프로젝트에 전역 적용   |
| Project Rules (`alwaysApply: true`) | `.cursor/rules/*.mdc`   | 항상 포함                   |
| Project Rules (glob 패턴)           | `.cursor/rules/*.mdc`   | 해당 파일 열릴 때 자동 포함 |
| Manual Rules                        | `.cursor/rules/*.mdc`   | `@ruleName`으로 명시적 호출 |

#### 규칙 파일 분리 전략

```
.cursor/rules/
├── core.mdc        # alwaysApply: true — 전역 필수 규칙 (세션 시작 절차 등)
├── backend.mdc     # globs: backend/**  — Python/uv/FastAPI 규칙
├── frontend.mdc    # globs: frontend/** — React/TypeScript 규칙
└── git.mdc         # 커밋 메시지, PR 규칙 (수동 @git으로 호출)
```

**좋은 규칙의 조건**:

- **구체적**: "좋은 코드 짜기" ❌ → "함수 하나당 50줄 이하로 제한" ✅
- **명령 포인터 포함**: 자세한 내용 대신 참조할 파일 경로를 명시
- **에이전트가 반복 실수할 때만 추가**: 처음부터 과도한 규칙은 역효과

> **공식 팁**: 에이전트가 같은 실수를 반복할 때 규칙을 추가하세요. 처음부터 모든 것을 규칙화하지 마세요.

---

### 3-3. `.cursor/hooks.json` — 에이전트 자동화 루프

**Hooks**는 에이전트 액션 전후에 스크립트를 자동 실행하는 기능입니다. 가장 강력한 패턴은 **Stop Hook**으로, 에이전트가 완료되면 자동으로 다음 반복을 지시합니다.

```json
{
  "version": 1,
  "hooks": {
    "stop": [{ "command": "bun run .cursor/hooks/grind.ts" }]
  }
}
```

`.cursor/hooks/grind.ts` 예시 (테스트 통과할 때까지 반복):

```typescript
import { readFileSync, existsSync } from "fs";

interface StopHookInput {
  conversation_id: string;
  status: "completed" | "aborted" | "error";
  loop_count: number;
}

const input: StopHookInput = await Bun.stdin.json();
const MAX_ITERATIONS = 5;

if (input.status !== "completed" || input.loop_count >= MAX_ITERATIONS) {
  console.log(JSON.stringify({}));
  process.exit(0);
}

const scratchpad = existsSync(".cursor/scratchpad.md")
  ? readFileSync(".cursor/scratchpad.md", "utf-8")
  : "";

if (scratchpad.includes("DONE")) {
  console.log(JSON.stringify({}));
} else {
  console.log(
    JSON.stringify({
      followup_message: `[Iteration ${input.loop_count + 1}/${MAX_ITERATIONS}] Continue working. Update .cursor/scratchpad.md with DONE when complete.`,
    }),
  );
}
```

> **활용 예시**: 모든 테스트 통과할 때까지 반복 / UI가 디자인 목업과 일치할 때까지 반복 / 목표 달성이 검증 가능한 모든 작업

---

### 3-4. Agent Skills (`SKILL.md`) — 에이전트의 동적 도구

**Skills**는 Rules와 달리 **동적으로 로딩**됩니다. 에이전트가 관련성을 판단해 필요할 때만 불러옵니다. 컨텍스트 창을 깨끗하게 유지하면서 전문 능력을 제공하는 방식입니다.

Skills에 포함 가능한 내용:

- **Custom commands**: `/`로 호출하는 재사용 가능한 워크플로우
- **Hooks**: 에이전트 액션 전후 실행 스크립트
- **Domain knowledge**: 특정 작업에 대한 전문 지침

> ⚠️ **2026년 5월 기준**: Agent Skills는 Nightly 채널에서 사용 가능합니다. Cursor Settings > Beta > Update Channel: Nightly 설정 필요.

---

### 3-5. `backend/` — FastAPI + uv 환경

```toml
# pyproject.toml 예시
[project]
name = "my-project-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic>=2.7.0",
    "httpx>=0.27.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.2.0",
    "ruff>=0.4.0",
    "mypy>=1.10.0",
]
```

에이전트에게 줄 지시문 (rules에 포함):

> "새 라이브러리가 필요하면 `uv add 패키지명`을 먼저 실행한 후 코드를 짜. `pip install` 금지."

---

### 3-6. `frontend/` — React 19 + TanStack 환경

상태 관리는 **Jotai**, 라우팅은 **TanStack Router**, 서버 상태는 **TanStack Query**로 통일합니다.

---

## 4. 핵심 파일 템플릿 모음

### 4-1. `.cursor/rules/core.mdc` — 전역 규칙

```markdown
---
description: 모든 세션에서 항상 적용되는 핵심 규칙
alwaysApply: true
---

# 세션 시작 필수 절차

새 작업을 시작하기 전, 반드시 `.cursor/plans/000-PROJECT-INDEX.md`를 먼저 읽는다.
관련 계획 파일을 확인하고 현재 Status를 파악한 후 작업을 시작한다.

# 계획 업데이트 규칙

- 작업 완료 후 반드시 해당 계획 파일의 Status와 Completed Steps를 업데이트한다.
- 예상치 못한 문제 발생 시 계획 파일의 Blockers 섹션에 기록한다.

# 코드 공통 규칙

- 새 파일을 만들기 전, 해당 기능의 계획 파일이 `.cursor/plans/`에 있는지 확인한다.
- 함수 하나의 길이는 50줄을 넘기지 않는다.
- 매직 넘버는 상수로 추출한다.

# 커맨드 참조

- 백엔드 실행: `cd backend && uv run uvicorn app.main:app --reload`
- 프런트엔드 실행: `cd frontend && npm run dev`
- 테스트: `cd backend && uv run pytest`
- 린트: `cd backend && uv run ruff check .`
```

### 4-2. `.cursor/rules/backend.mdc` — 백엔드 규칙

```markdown
---
description: Python/FastAPI 백엔드 파일 작업 시 자동 적용
globs:
  - backend/**/*.py
  - backend/pyproject.toml
alwaysApply: false
---

# 백엔드 규칙

- 패키지 관리는 반드시 `uv`를 사용한다. `pip install` 금지.
  새 패키지 추가: `uv add 패키지명`
- 타입 힌트를 모든 함수에 추가한다.
- Pydantic v2 문법을 사용한다. (v1 호환 레거시 문법 금지)
- API 라우터는 `backend/app/api/v1/`에 위치한다.
- 비즈니스 로직은 `backend/app/services/`로 분리한다.
- 예시 컴포넌트 구조: `backend/app/api/v1/users.py` 참조
```

### 4-3. `.cursor/rules/frontend.mdc` — 프런트엔드 규칙

```markdown
---
description: React/TypeScript 프런트엔드 파일 작업 시 자동 적용
globs:
  - frontend/src/**/*.tsx
  - frontend/src/**/*.ts
alwaysApply: false
---

# 프런트엔드 규칙

- 상태 관리는 Jotai만 사용한다. (Zustand, Redux 혼용 금지)
- 라우팅은 TanStack Router, 서버 상태는 TanStack Query 사용.
- React 19의 최신 훅을 우선 사용한다.
- `any` 타입 사용 금지.
- 컴포넌트 파일은 `PascalCase.tsx`로 명명한다.
- 예시 컴포넌트 구조: `frontend/src/components/Button.tsx` 참조
```

### 4-4. `.cursor/rules/git.mdc` — Git 규칙

```markdown
---
description: Git 커밋, PR 작업 시 @git으로 수동 호출
alwaysApply: false
---

# Git 규칙

- 커밋 메시지 형식: `type(scope): 한국어 설명`
  예: `feat(auth): 소셜 로그인 추가`, `fix(api): 타임아웃 처리 수정`
- `.env` 파일은 절대 커밋하지 않는다.
- PR 생성 절차:
  1. `git diff`로 변경사항 확인
  2. 명확한 커밋 메시지 작성
  3. 현재 브랜치에 push
  4. `gh pr create`로 PR 오픈
```

---

### 4-5. `000-PROJECT-INDEX.md` 템플릿

````markdown
# 프로젝트 인덱스

> 에이전트는 새 세션 시작 시 이 파일을 가장 먼저 읽어야 합니다.

## 프로젝트 개요

- **프로젝트명**: [이름]
- **목적**: [한 줄 설명]
- **기술 스택**: FastAPI / React 19 / Jotai / TanStack / uv
- **최종 업데이트**: YYYY-MM-DD

---

## 전체 계획 현황

| 파일                    | 제목               | Status         | 마지막 작업 |
| ----------------------- | ------------------ | -------------- | ----------- |
| `001-setup.md`          | 초기 환경 설정     | 🟢 COMPLETED   | 2026-01-15  |
| `002-agent-loop.md`     | 에이전트 루프 설계 | 🟡 IN_PROGRESS | 2026-01-20  |
| `003-stock-analysis.md` | 주가 분석 기능     | 🔴 NOT_STARTED | —           |

---

## 현재 최우선 작업

**지금 당장 해야 할 것**: `002-agent-loop.md`의 Step 3 (API 엔드포인트 연결)

**다음 작업**: `003-stock-analysis.md` 시작

---

## 알려진 이슈

- [ ] `backend/app/services/loop.py`의 타임아웃 처리 미완성
- [ ] 프런트엔드 에러 바운더리 없음

---

## 환경 설정 요약

```bash
# 백엔드 실행
cd backend && uv run uvicorn app.main:app --reload

# 프런트엔드 실행
cd frontend && npm run dev

# 테스트 실행
cd backend && uv run pytest
```
````

---

### 4-6. `TEMPLATE-plan.md` (개별 계획 파일 템플릿)

````markdown
# [NNN] [기능명] 계획서

> **Status**: 🔴 NOT_STARTED  
> **생성일**: YYYY-MM-DD  
> **관련 Skills**: `.agent/skills/[스킬명]/`

---

## 목표

이 기능이 완성되었을 때 달성되어야 할 것을 한 문장으로:

> "[구체적인 완료 조건]"

---

## 아키텍처 설계

```mermaid
graph LR
    A[사용자 요청] --> B[FastAPI 엔드포인트]
    B --> C[서비스 레이어]
    C --> D[에이전트 스킬 실행]
    D --> E[결과 반환]
```

> Plan Mode에서 에이전트가 자동으로 Mermaid 다이어그램을 생성합니다 (v2.2+).

---

## 구현 단계 (체크리스트)

### Phase 1: 기반 작업

- [ ] Step 1: [구체적인 작업 내용]
  - 결과물: `파일 경로`
- [ ] Step 2: [구체적인 작업 내용]
  - 결과물: `파일 경로`

### Phase 2: 핵심 구현

- [ ] Step 3: [구체적인 작업 내용]
- [ ] Step 4: [구체적인 작업 내용]

### Phase 3: 검증 및 마무리

- [ ] Step 5: `uv run pytest tests/test_[기능명].py` 통과
- [ ] Step 6: `000-PROJECT-INDEX.md` 업데이트

---

## 완료된 작업 로그

| 날짜 | Step | 결과 | 비고 |
| ---- | ---- | ---- | ---- |
| —    | —    | —    | —    |

---

## 블로커 (Blockers)

현재 막혀 있는 문제:

- (없음)

---

## 참고 자료

- 관련 문서:
- 참고 코드:
````

---

### 4-7. `SKILL.md` 템플릿 (`.agent/skills/_template/`)

````markdown
---
name: [스킬 이름]
version: 1.0.0
trigger: "[이런 상황에서 이 스킬을 사용한다]"
---

# [스킬 이름] 스킬

## 개요

이 스킬이 하는 일을 한 문장으로 설명합니다.

## 사용 조건 (When to Use)

- [조건 1]
- [조건 2]

## 실행 방법

```bash
uv run .agent/skills/[스킬명]/scripts/main.py \
  --input [값] \
  --output [경로]
```

## 입력 파라미터

| 파라미터    | 타입 | 필수 | 설명           |
| ----------- | ---- | ---- | -------------- |
| `--input`   | str  | ✅   | 입력값         |
| `--output`  | str  | ✅   | 출력 파일 경로 |
| `--verbose` | bool | ❌   | 상세 로그 출력 |

## 출력 형식

```json
{
  "status": "success",
  "output_file": "data/result.csv",
  "rows_processed": 30,
  "timestamp": "2026-01-20T10:30:00"
}
```

## 실패 시 처리

에러 발생 시 `.cursor/plans/` 관련 계획 파일의 Blockers 섹션에 기록한다.

## 의존성

```toml
# pyproject.toml에 추가 필요한 패키지
"yfinance>=0.2.40",
"pandas>=2.2.0",
```
````

---

## 5. Plan Mode 실전 워크플로우

### 새 기능 추가 시 (표준 절차)

```
1. [Plan Mode] Shift+Tab 입력 → 기능 설명
   에이전트가 질문하면 답변 → 플랜 검토 및 편집
   "Save to workspace" 클릭 → .cursor/plans/003-stock-analysis.md 저장

   ↓

2. [Plan Mode] 인덱스 업데이트
   프롬프트: "방금 저장한 003-stock-analysis.md를
   000-PROJECT-INDEX.md의 테이블에 추가해줘."

   ↓

3. [Agent Mode] Phase 1 실행
   프롬프트: "003-stock-analysis.md의 Phase 1을 실행해.
   완료된 Step마다 계획 파일의 체크박스를 체크해줘."
   (또는 Plan Mode에서 해당 TODO만 선택해 새 에이전트로 전달)

   ↓

4. [검증] 테스트 실행
   프롬프트: "작업이 끝났으면 `uv run pytest`를 실행하고
   결과를 003-stock-analysis.md의 완료 로그에 기록해줘."

   ↓

5. [Plan Mode] 다음 Phase 또는 완료 처리
   Status 업데이트 → 000-PROJECT-INDEX.md 갱신
```

### 중단 후 재개 시 (컨텍스트 복구)

```
프롬프트:
"오늘 다시 작업을 시작하려고 해.
`.cursor/plans/000-PROJECT-INDEX.md`를 읽고,
현재 어떤 상태인지 요약해줘.
지금 당장 해야 할 작업이 뭔지 알려줘."
```

### 병렬 에이전트 활용 (Background Agents)

```
복잡한 플랜의 독립적인 단계들은 Plan Mode에서
각 TODO를 선택 → "Send to new agent"로 병렬 실행 가능.

완료 후 Cursor가 자동으로 최적 결과를 추천해줌 (Multi-agent judging, v2.2+).
```

### @Past Chats 활용 (새 세션에서 이전 작업 참조)

```
새 세션에서 컨텍스트가 필요할 때:
프롬프트: "@Past Chats [지난 세션에서 다룬 기능명] 참조해서
지금 작업 이어서 해줘."

→ 이전 대화 전체를 복붙하는 것보다 훨씬 효율적
```

---

## 6. 작은 루프 설계 원칙

에이전트가 길을 잃는 가장 큰 원인은 **작업 단위가 너무 크기 때문**입니다. 또한 대화가 길어지면 에이전트의 집중력이 흐려집니다.

### 새 대화를 시작해야 할 때

| 새 대화 시작              | 대화 유지                        |
| ------------------------- | -------------------------------- |
| 다른 기능/태스크로 이동   | 같은 기능 반복 개선              |
| 에이전트가 같은 실수 반복 | 방금 만든 것 디버깅              |
| 한 논리 단위 작업 완료    | 에이전트가 방금 작성한 코드 수정 |

### 좋은 루프의 기준

| 기준            | 설명                                         |
| --------------- | -------------------------------------------- |
| **단일 결과물** | 루프 하나가 끝나면 명확한 파일 하나가 생성됨 |
| **20분 이내**   | 한 루프가 20분을 넘지 않도록 쪼갬            |
| **검증 가능**   | `uv run pytest` 또는 직접 실행으로 즉시 확인 |
| **독립적**      | 이전 루프의 실패와 무관하게 실행 가능        |

### 루프 분해 예시

```
❌ 나쁜 예: "주식 분석 대시보드를 만들어줘"
→ 에이전트가 길을 잃을 가능성 매우 높음

✅ 좋은 예 (루프 분해):
Loop 1: "yfinance로 AAPL 30일치 데이터를 가져오는
         fetch_prices.py를 만들고 실행해봐"
         → 결과물: data/AAPL_prices.csv

Loop 2: "fetch_prices.py 출력을 받아 이동평균을 계산하는
         analyze.py를 만들어줘"
         → 결과물: data/AAPL_analysis.csv

Loop 3: "analyze.py 결과를 FastAPI /api/v1/analysis로
         서빙하는 엔드포인트를 추가해줘"
         → 결과물: backend/app/api/v1/analysis.py

Loop 4: "React에서 /api/v1/analysis를 호출해 차트로
         보여주는 컴포넌트를 만들어줘"
         → 결과물: frontend/src/components/AnalysisChart.tsx
```

---

## 7. 자주 하는 실수와 해결책

### 실수 1: `.cursorrules` 계속 사용하기

```
❌ 프로젝트 루트에 .cursorrules 파일 사용
✅ .cursor/rules/*.mdc 파일로 이전
   Cmd+Shift+P → "New Cursor Rule" 사용
```

### 실수 2: 규칙 파일을 하나로 몰아넣기

```
❌ core.mdc 하나에 모든 규칙 (1000줄)
✅ 파일 타입/디렉터리 기준으로 분리
   → 각 규칙 파일은 짧고 명확하게
```

### 실수 3: 계획 파일 없이 바로 코드 작성

```
❌ "주가 크롤러 만들어줘"
✅ Shift+Tab → 플랜 생성 → 검토 → 저장 → 실행
```

### 실수 4: 너무 긴 대화 지속하기

```
증상: 에이전트가 이전에 만든 코드와 충돌하는 코드 생성
해결: 한 논리 단위 완료 시 새 대화 시작
     → 이전 작업 참조는 @Past Chats 사용
```

### 실수 5: uv 환경 무시

```
❌ "pip install yfinance 해줘"
✅ "pyproject.toml에 yfinance를 추가하고 uv sync 실행해줘"
   (또는 backend.mdc 규칙에 명시해두면 에이전트가 자동으로 따름)
```

### 실수 6: 에러 발생 시 맥락 없이 재시도

```
에러 발생 시 프롬프트:
"이 에러를 `.cursor/plans/[해당 계획].md`의 Blockers에
기록하고, 원인을 분석해서 해결 방법을 제시해줘."
```

---

## 8. 빠른 시작 체크리스트

```bash
# 1. 디렉터리 구조 생성
mkdir -p .cursor/plans .cursor/rules .agent/skills/_template backend/app frontend/src

# 2. Python 환경 초기화
cd backend
uv init --python 3.12
uv add fastapi uvicorn pydantic

# 3. 핵심 파일 생성
touch .cursor/rules/core.mdc
touch .cursor/rules/backend.mdc
touch .cursor/rules/frontend.mdc
touch .cursor/rules/git.mdc
touch .cursor/plans/000-PROJECT-INDEX.md
touch .cursor/plans/TEMPLATE-plan.md
touch .agent/skills/_template/SKILL.md
echo '{"version": 1, "hooks": {}}' > .cursor/hooks.json
echo "3.12" > backend/.python-version
```

**설정 체크리스트**:

- [ ] `.cursor/rules/core.mdc` 작성 (`alwaysApply: true`, 세션 시작 절차 포함)
- [ ] `.cursor/rules/backend.mdc` 작성 (`globs: backend/**`)
- [ ] `.cursor/rules/frontend.mdc` 작성 (`globs: frontend/src/**`)
- [ ] `.cursor/rules/git.mdc` 작성 (수동 호출용)
- [ ] `000-PROJECT-INDEX.md` 작성 (섹션 4-5 템플릿 사용)
- [ ] `TEMPLATE-plan.md` 저장 (섹션 4-6 템플릿 사용)
- [ ] `_template/SKILL.md` 저장 (섹션 4-7 템플릿 사용)
- [ ] `pyproject.toml`에 기본 의존성 추가
- [ ] `.gitignore`에 `.env`, `__pycache__/`, `.venv/` 추가
- [ ] `001-setup.md` 작성 후 환경 설정 완료 표시
- [ ] (선택) Nightly 채널 설정 시 `.cursor/hooks.json` 구성

---

> **기억하세요**: Plan Mode는 이제 Cursor에 내장된 기능입니다. `Shift+Tab` 하나로 에이전트가 코드베이스를 스스로 탐색하고 플랜을 세웁니다. 이 구조의 역할은 그 플랜을 **저장하고, 규칙으로 일관성을 유지하고, Skills로 능력을 확장**하는 것입니다.

# 참고 사이트

https://cursor.com/ko/blog/agent-best-practices
https://cursor.com/ko/changelog/2-2
