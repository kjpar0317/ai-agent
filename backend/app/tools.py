from __future__ import annotations

import math
import re
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SearchHit(BaseModel):
    title: str
    url: str
    summary: str


class SearchNewsResult(BaseModel):
    query: str
    hits: list[SearchHit] = Field(default_factory=list)
    note: str = Field(
        default="Stub 검색: 외부 뉴스 API가 연결되지 않았습니다. 데모용 더미 결과입니다."
    )


def search_news(query: str) -> SearchNewsResult:
    """뉴스 검색 (스텁). 프로덕션에서는 허용된 뉴스 API로 교체하세요."""
    q = query.strip()
    slug = re.sub(r"\W+", "-", q.lower())[:40] or "news"
    return SearchNewsResult(
        query=q,
        hits=[
            SearchHit(
                title=f"[stub] {q} 관련 헤드라인",
                url=f"https://example.invalid/news/{slug}",
                summary="이 문장은 스텁 응답입니다. 실제 기사가 아닙니다.",
            )
        ],
    )


class PythonAnalysisResult(BaseModel):
    ok: bool
    stdout: str
    stderr: str
    note: str


def run_python_analysis(code: str) -> PythonAnalysisResult:
    """수치·통계 위주의 안전한 미니 분석 (exec 금지, 제한된 builtins만)."""
    safe_globals = {
        "__builtins__": {
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "len": len,
            "round": round,
            "sorted": sorted,
            "enumerate": enumerate,
            "zip": zip,
            "print": lambda *a, **k: None,
            "math": math,
        },
        "datetime": datetime,
        "timezone": timezone,
    }
    stdout_lines: list[str] = []
    local_ns: dict[str, object] = {}

    def _capture_print(*args: object, **kwargs: object) -> None:
        stdout_lines.append(" ".join(str(a) for a in args))

    safe_globals["__builtins__"]["print"] = _capture_print  # type: ignore[index]

    try:
        exec(code, safe_globals, local_ns)  # noqa: S102 — sandboxed namespace only
    except Exception as exc:  # noqa: BLE001
        return PythonAnalysisResult(
            ok=False,
            stdout="",
            stderr=str(exc),
            note="샌드박스 실행 실패. math·기본 내장만 사용 가능합니다.",
        )
    return PythonAnalysisResult(
        ok=True,
        stdout="\n".join(stdout_lines).strip(),
        stderr="",
        note="제한된 샌드박스에서만 실행되었습니다. 임의 파일·네트워크는 불가합니다.",
    )
