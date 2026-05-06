# Cursor Plan Mode 기반 AI 에이전트 프로젝트 표준 구조 가이드

> **대상**: Cursor IDE를 활용해 복잡한 프로젝트를 관리하는 프리랜서 개발자  
> **목적**: 에이전트가 길을 잃지 않고 '작은 루프'를 완성하게 만드는 표준 파일 구성 정립  
> **기반**: BMAD-METHOD + Antigravity Skills 설계 원칙  
> **최종 수정**: 2026년 기준

---

## 목차

1. [핵심 철학: 왜 이 구조인가?](#1-핵심-철학-왜-이-구조인가)
2. [전체 프로젝트 디렉터리 구조](#2-전체-프로젝트-디렉터리-구조)
3. [각 구성 요소 상세 설명](#3-각-구성-요소-상세-설명)
   - 3-1. `.cursor/plans/` — 에이전트의 기억장치
   - 3-2. `.cursorrules` — 에이전트의 헌법
   - 3-3. `.agent/skills/` — 에이전트의 도구 상자
   - 3-4. `backend/` — FastAPI + uv 환경
   - 3-5. `frontend/` — React 19 + TanStack 환경
4. [핵심 파일 템플릿 모음](#4-핵심-파일-템플릿-모음)
5. [Plan Mode 실전 워크플로우](#5-plan-mode-실전-워크플로우)
6. [작은 루프 설계 원칙](#6-작은-루프-설계-원칙)
7. [자주 하는 실수와 해결책](#7-자주-하는-실수와-해결책)
8. [빠른 시작 체크리스트](#8-빠른-시작-체크리스트)

---

## 1. 핵심 철학: 왜 이 구조인가?

AI 에이전트는 컨텍스트 창(Context Window)이라는 근본적인 제약이 있습니다. 에이전트는 대화가 길어지거나 세션이 바뀌면 이전 작업을 잊어버립니다. 이 구조는 그 문제를 **파일 시스템으로 해결**합니다.

### 세 가지 핵심 원칙

| 원칙            | 설명                             | 구현 방법        |
| --------------- | -------------------------------- | ---------------- |
| **상태 외부화** | 에이전트의 기억을 파일에 저장    | `.cursor/plans/` |
| **규칙 명문화** | 판단 기준을 코드처럼 관리        | `.cursorrules`   |
| **액션 모듈화** | 반복 작업을 재사용 가능한 단위로 | `.agent/skills/` |

### BMAD-METHOD란?

- **B**uild: 먼저 계획을 만든다
- **M**easure: 실행 후 결과를 측정한다
- **A**djust: 계획서에 결과를 업데이트한다
- **D**eploy: 검증된 루프를 배포한다

---

## 2. 전체 프로젝트 디렉터리 구조

```
📂 my-project/
│
├── 📂 .cursor/                          # Cursor 에이전트 전용 설정
│   ├── 📂 plans/                        # ⭐ 에이전트의 기억장치 (가장 중요)
│   │   ├── 📄 000-PROJECT-INDEX.md      # 모든 계획 파일의 목차 및 상태 요약
│   │   ├── 📄 001-setup.md              # 초기 환경 설정 계획
│   │   ├── 📄 002-agent-loop.md         # 에이전트 루프 핵심 기능 설계
│   │   ├── 📄 003-stock-analysis.md     # 기능별 세부 계획 (예시)
│   │   └── 📄 TEMPLATE-plan.md          # 새 계획 작성 시 복사할 템플릿
│   │
│   └── 📄 .cursorrules                  # 에이전트 전역 행동 규칙
│
├── 📂 .agent/                           # 에이전트 능력(Skills) 정의
│   └── 📂 skills/
│       ├── 📂 code-analyzer/            # 코드 분석 스킬
│       │   ├── 📄 SKILL.md              # 스킬 실행 지침
│       │   └── 📂 scripts/
│       │       ├── 📄 analyze.py
│       │       └── 📄 report.py
│       ├── 📂 stock-fetcher/            # 주가 데이터 스킬
│       │   ├── 📄 SKILL.md
│       │   └── 📂 scripts/
│       │       └── 📄 fetch_prices.py
│       └── 📂 _template/               # 새 스킬 생성 시 복사할 템플릿
│           ├── 📄 SKILL.md
│           └── 📂 scripts/
│               └── 📄 main.py
│
├── 📂 backend/                          # FastAPI 기반 백엔드
│   ├── 📂 app/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py                   # FastAPI 진입점
│   │   ├── 📂 api/                      # 라우터 모음
│   │   │   └── 📄 v1/
│   │   ├── 📂 core/                     # 설정, 의존성
│   │   │   ├── 📄 config.py
│   │   │   └── 📄 deps.py
│   │   ├── 📂 models/                   # Pydantic 모델
│   │   └── 📂 services/                 # 비즈니스 로직
│   ├── 📂 tests/
│   ├── 📄 pyproject.toml                # ⭐ uv 환경의 심장
│   ├── 📄 uv.lock                       # 의존성 잠금 파일 (git 추적)
│   └── 📄 .python-version               # Python 버전 명시 (예: 3.12)
│
├── 📂 frontend/                         # React 19 + TanStack 기반 프런트엔드
│   ├── 📂 src/
│   │   ├── 📂 components/
│   │   ├── 📂 routes/                   # TanStack Router 라우트
│   │   ├── 📂 stores/                   # Jotai 상태 관리
│   │   ├── 📂 hooks/
│   │   └── 📄 main.tsx
│   ├── 📄 package.json
│   ├── 📄 tsconfig.json
│   └── 📄 vite.config.ts
│
├── 📂 docs/                             # 프로젝트 문서
│   └── 📄 architecture.md
│
├── 📄 .env.example                      # 환경 변수 예시 (절대 .env 자체는 커밋 금지)
├── 📄 .gitignore
├── 📄 docker-compose.yml                # 로컬 개발 환경 (DB 등)
└── 📄 README.md
```

---

## 3. 각 구성 요소 상세 설명

### 3-1. `.cursor/plans/` — 에이전트의 기억장치

Plan Mode의 핵심입니다. **에이전트가 다음 번 이 프로젝트를 열었을 때 "어디까지 했지?"를 파악하는 유일한 수단**입니다.

#### 작동 원리

```
세션 시작 → 에이전트가 000-PROJECT-INDEX.md 읽음
          → 관련 계획 파일 읽음
          → 현재 상태(Status) 확인
          → 다음 단계(Next Step) 실행
          → 완료 후 계획 파일 업데이트
          → 세션 종료
```

#### 파일 네이밍 규칙

| 패턴                   | 의미                 | 예시                |
| ---------------------- | -------------------- | ------------------- |
| `000-PROJECT-INDEX.md` | 전체 인덱스 (고정)   | —                   |
| `0XX-이름.md`          | 인프라/설정 계획     | `001-setup.md`      |
| `1XX-이름.md`          | 백엔드 기능 계획     | `101-user-auth.md`  |
| `2XX-이름.md`          | 프런트엔드 기능 계획 | `201-dashboard.md`  |
| `3XX-이름.md`          | 에이전트 루프 계획   | `301-stock-loop.md` |

#### 계획 파일 상태값 (Status)

```
🔴 NOT_STARTED   - 아직 시작 안 함
🟡 IN_PROGRESS   - 현재 진행 중
🟢 COMPLETED     - 완료
⚫ BLOCKED        - 다른 작업에 막힘 (이유 기록)
🔵 REVIEW        - 검토 필요
```

---

### 3-2. `.cursorrules` — 에이전트의 헌법

프로젝트 전체에서 에이전트가 **절대 어기면 안 되는 규칙**입니다. 새 세션이 시작될 때마다 자동으로 로드됩니다.

#### 좋은 규칙의 조건

1. **구체적**: "좋은 코드 짜기" (❌) → "함수 하나당 50줄 이하로 제한" (✅)
2. **검증 가능**: 에이전트 스스로 지켰는지 확인할 수 있어야 함
3. **이유 포함**: 규칙의 근거를 함께 적으면 에이전트가 더 잘 따름

---

### 3-3. `.agent/skills/` — 에이전트의 도구 상자

에이전트가 실제로 실행할 **액션을 모듈화**한 곳입니다.

#### SKILL.md 역할

에이전트에게 "이런 상황이 오면 이 스크립트를 실행해"라고 알려주는 매뉴얼입니다.

```yaml
# SKILL.md 예시 구조
trigger: "주가 데이터가 필요할 때"
command: "uv run scripts/fetch_prices.py --ticker {TICKER} --days {DAYS}"
output: "data/{TICKER}_{DATE}.csv"
next_step: "분석 결과를 .cursor/plans/에 업데이트"
```

#### 스킬 설계 원칙

- 스킬 하나 = 명확한 입력 + 명확한 출력
- 실패 시 에러 메시지가 계획 파일에 기록되어야 함
- `uv run`으로 독립 실행 가능해야 함

---

### 3-4. `backend/` — FastAPI + uv 환경

#### pyproject.toml이 핵심인 이유

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

**Cursor에게 줄 지시문:**

> "이 `pyproject.toml`에 정의된 가상 환경을 기준으로 코드를 작성해. 새 라이브러리가 필요하면 `uv add 패키지명`을 먼저 실행한 후 코드를 짜."

---

### 3-5. `frontend/` — React 19 + TanStack 환경

상태 관리는 **Jotai**, 라우팅은 **TanStack Router**, 서버 상태는 **TanStack Query**로 통일합니다.

---

## 4. 핵심 파일 템플릿 모음

### 4-1. `.cursorrules` 템플릿

```markdown
# 프로젝트 전역 규칙 (에이전트 필독)

## 0. 세션 시작 필수 절차

- 새 작업을 시작하기 전, 반드시 `.cursor/plans/000-PROJECT-INDEX.md`를 먼저 읽는다.
- 관련 계획 파일을 확인하고 현재 Status를 파악한 후 작업을 시작한다.

## 1. 코드 작성 규칙

### 공통

- 새 파일을 만들기 전, 해당 기능의 계획 파일이 `.cursor/plans/`에 있는지 확인한다.
- 함수 하나의 길이는 50줄을 넘기지 않는다.
- 매직 넘버는 상수로 추출한다.

### 백엔드 (Python)

- 패키지 관리는 반드시 `uv`를 사용한다. (`pip install` 금지)
- 타입 힌트를 모든 함수에 추가한다.
- Pydantic v2 문법을 사용한다. (v1 호환 레거시 문법 금지)

### 프런트엔드 (TypeScript/React)

- 상태 관리는 Jotai만 사용한다. (Zustand, Redux 혼용 금지)
- React 19의 최신 훅을 우선 사용한다.
- `any` 타입 사용을 금지한다.
- 컴포넌트 파일은 `PascalCase.tsx`로 명명한다.

## 2. Git 규칙

- 커밋 메시지 형식: `type(scope): 한국어 설명` (예: `feat(auth): 소셜 로그인 추가`)
- `.env` 파일은 절대 커밋하지 않는다.

## 3. 계획 업데이트 규칙

- 작업 완료 후 반드시 해당 계획 파일의 Status와 Completed Steps를 업데이트한다.
- 예상치 못한 문제 발생 시 계획 파일의 Blockers 섹션에 기록한다.

## 4. 스크립트 실행 규칙

- Python 스크립트는 항상 `uv run scripts/...` 형태로 실행한다.
- 테스트는 `uv run pytest` 로 실행한다.
```

---

### 4-2. `000-PROJECT-INDEX.md` 템플릿

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

- [ ] `backend/app/services/loop.py`의 타임아웃 처리 미완성 (담당: 에이전트)
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

````

---

### 4-3. `TEMPLATE-plan.md` (개별 계획 파일 템플릿)

```markdown
# [NNN] [기능명] 계획서

> **Status**: 🔴 NOT_STARTED
> **생성일**: YYYY-MM-DD
> **관련 스킬**: `.agent/skills/[스킬명]/`

---

## 목표

이 기능이 완성되었을 때 달성되어야 할 것을 한 문장으로:
> "[구체적인 완료 조건]"

---

## 아키텍처 설계

````

[시스템 구성도 또는 데이터 흐름도를 텍스트로]

예:
사용자 요청 → FastAPI 엔드포인트 → 서비스 레이어 → 에이전트 스킬 실행 → 결과 반환

```

---

## 구현 단계 (체크리스트)

### Phase 1: 기반 작업
- [ ] Step 1: [구체적인 작업 내용]
  - 예상 시간: X분
  - 결과물: `파일 경로`
- [ ] Step 2: [구체적인 작업 내용]
  - 예상 시간: X분
  - 결과물: `파일 경로`

### Phase 2: 핵심 구현
- [ ] Step 3: [구체적인 작업 내용]
- [ ] Step 4: [구체적인 작업 내용]

### Phase 3: 검증 및 마무리
- [ ] Step 5: `uv run pytest tests/test_[기능명].py` 통과
- [ ] Step 6: 000-PROJECT-INDEX.md 업데이트

---

## 완료된 작업 로그

| 날짜 | Step | 결과 | 비고 |
|------|------|------|------|
| — | — | — | — |

---

## 블로커 (Blockers)

현재 막혀 있는 문제:
- (없음)

---

## 참고 자료

- 관련 문서:
- 참고 코드:
```

---

### 4-4. `SKILL.md` 템플릿 (`.agent/skills/_template/`)

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
# 기본 실행
uv run .agent/skills/[스킬명]/scripts/main.py --input [값] --output [경로]

# 예시
uv run .agent/skills/stock-fetcher/scripts/fetch_prices.py \
  --ticker AAPL \
  --days 30 \
  --output data/AAPL_prices.csv
```
````

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

- 에러 발생 시 `.cursor/plans/` 관련 계획 파일의 Blockers 섹션에 기록한다.
- 에러 코드와 스택 트레이스를 함께 기록한다.

## 의존성

```toml
# 이 스킬 실행에 필요한 추가 패키지 (pyproject.toml에 추가 필요 시)
"yfinance>=0.2.40",
"pandas>=2.2.0",
```

```

---

## 5. Plan Mode 실전 워크플로우

### 새 기능 추가 시 (표준 절차)

```

1. [Plan Mode] 계획 파일 작성
   프롬프트: "주식 분석 기능을 추가하려고 해.
   `.cursor/plans/003-stock-analysis.md`를
   TEMPLATE-plan.md를 참고해서 작성해줘.
   아키텍처 설계와 Phase별 구현 단계를 포함해."

   ↓

2. [Plan Mode] 인덱스 업데이트
   프롬프트: "방금 만든 003-stock-analysis.md를
   000-PROJECT-INDEX.md의 테이블에 추가해줘."

   ↓

3. [Act Mode] Phase 1 실행
   프롬프트: "003-stock-analysis.md의 Phase 1을 실행해.
   완료된 Step마다 계획 파일의 체크박스를 체크해줘."

   ↓

4. [검증] 테스트 실행
   프롬프트: "작업이 끝났으면 `uv run pytest`를 실행하고
   결과를 003-stock-analysis.md의 완료 로그에 기록해줘."

   ↓

5. [Plan Mode] 다음 Phase 또는 완료 처리
   Status를 적절히 업데이트하고 000-PROJECT-INDEX.md 갱신

```

### 중단 후 재개 시 (컨텍스트 복구 절차)

```

프롬프트 예시:
"오늘 다시 작업을 시작하려고 해.
`.cursor/plans/000-PROJECT-INDEX.md`를 읽고,
현재 어떤 상태인지 요약해줘.
그리고 지금 당장 해야 할 작업이 뭔지 알려줘."

```

---

## 6. 작은 루프 설계 원칙

에이전트가 길을 잃는 가장 큰 원인은 **작업 단위가 너무 크기 때문**입니다.

### 좋은 루프의 기준

| 기준 | 설명 |
|------|------|
| **단일 결과물** | 루프 하나가 끝나면 명확한 파일 하나가 생성됨 |
| **20분 이내** | 한 루프가 20분을 넘지 않도록 쪼갬 |
| **검증 가능** | `uv run`으로 결과를 즉시 확인할 수 있음 |
| **독립적** | 이전 루프의 실패와 무관하게 실행 가능 |

### 루프 분해 예시

```

❌ 나쁜 예: "주식 분석 대시보드를 만들어줘"
→ 에이전트가 길을 잃을 가능성 매우 높음

✅ 좋은 예 (루프 분해):
Loop 1: "yfinance로 AAPL 30일치 데이터를 가져오는
fetch_prices.py를 만들고 실행해봐"
Loop 2: "fetch_prices.py 출력을 받아 이동평균을 계산하는
analyze.py를 만들어줘"
Loop 3: "analyze.py 결과를 FastAPI /api/v1/analysis로
서빙하는 엔드포인트를 추가해줘"
Loop 4: "React에서 /api/v1/analysis를 호출해 차트로
보여주는 컴포넌트를 만들어줘"

```

---

## 7. 자주 하는 실수와 해결책

### 실수 1: 계획 파일 없이 바로 코드 작성

```

❌ "주가 크롤러 만들어줘"
✅ "`.cursor/plans/003-stock-analysis.md` 계획서를 먼저
만들고, Phase 1부터 시작해줘"

```

### 실수 2: 너무 큰 컨텍스트에서 작업

- 증상: 에이전트가 이전에 만든 코드와 충돌하는 코드를 생성
- 해결: 루프를 더 작게 쪼개고, 각 루프 시작 시 관련 파일만 명시적으로 참조

### 실수 3: 계획 파일 업데이트 생략

```

모든 작업 완료 프롬프트에 반드시 추가:
"...작업이 끝나면 관련 계획 파일의 Status와 완료 로그를 업데이트해줘."

```

### 실수 4: uv 환경 무시

```

❌ "pip install yfinance 해줘"
✅ "pyproject.toml에 yfinance를 추가하고 uv sync 실행해줘"

```

### 실수 5: 에러 발생 시 맥락 없이 재시도

```

에러 발생 시 프롬프트:
"이 에러를 `.cursor/plans/[해당 계획].md`의 Blockers에
기록하고, 원인을 분석해서 해결 방법을 제시해줘."

````

---

## 8. 빠른 시작 체크리스트

새 프로젝트 시작 시 순서대로 따라하기:

```bash
# 1. 디렉터리 구조 생성
mkdir -p .cursor/plans .agent/skills/_template backend/app frontend/src

# 2. Python 환경 초기화
cd backend
uv init --python 3.12
uv add fastapi uvicorn pydantic

# 3. 핵심 파일 생성
touch .cursor/.cursorrules
touch .cursor/plans/000-PROJECT-INDEX.md
touch .cursor/plans/TEMPLATE-plan.md
touch .agent/skills/_template/SKILL.md
````

- [ ] `.cursorrules` 작성 (섹션 4-1 템플릿 사용)
- [ ] `000-PROJECT-INDEX.md` 작성 (섹션 4-2 템플릿 사용)
- [ ] `TEMPLATE-plan.md` 저장 (섹션 4-3 템플릿 사용)
- [ ] `_template/SKILL.md` 저장 (섹션 4-4 템플릿 사용)
- [ ] `pyproject.toml`에 기본 의존성 추가
- [ ] `.python-version` 파일 생성 (`echo "3.12" > .python-version`)
- [ ] `001-setup.md` 작성 후 환경 설정 완료 표시
- [ ] `.gitignore`에 `.env`, `__pycache__/`, `.venv/` 추가

---

> **기억하세요**: 이 구조의 핵심은 에이전트를 믿지 않는 것이 아니라, 에이전트가 최선의 성과를 낼 수 있도록 **명확한 컨텍스트를 제공**하는 것입니다. 파일로 관리되는 계획은 여러분과 에이전트 모두를 위한 공유 기억 장치입니다.
