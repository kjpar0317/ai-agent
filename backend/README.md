# Backend (FastAPI + PydanticAI)

## 실행

```bash
cd backend
python -m pip install -e .
python -m uvicorn main:app --reload --port 8000
```

## 환경 변수

| 변수 | 설명 |
|------|------|
| `AZURE_OPENAI_ENDPOINT` | Azure 리소스 엔드포인트 |
| `AZURE_OPENAI_API_KEY` | API 키 |
| `AZURE_OPENAI_DEPLOYMENT` | 배포(모델) 이름 |
| `AZURE_OPENAI_API_VERSION` | 기본 `2024-08-01-preview` |
| `DATABASE_URL` | 예: `postgresql+asyncpg://user:pass@localhost:5432/aiagent` |
| `CORS_ORIGINS` | 쉼표 구분, 예: `http://localhost:5173` |

키가 없으면 **TestModel**로 동작해 CI·로컬 스모크에 사용할 수 있습니다.

## 테스트

```bash
cd backend
python -m pytest tests -v
```
