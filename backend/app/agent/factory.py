from __future__ import annotations

from openai import AsyncAzureOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.config import Settings
from app.schemas import ValidationOutcome
from app.skills import load_rules_text, load_skills_markdown
from app.tools import run_python_analysis, search_news


def build_main_model(settings: Settings):
    if settings.azure_openai_api_key and settings.azure_openai_endpoint and settings.azure_openai_deployment:
        client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
            api_key=settings.azure_openai_api_key,
        )
        return OpenAIChatModel(
            settings.azure_openai_deployment,
            provider=OpenAIProvider(openai_client=client),
        )
    return TestModel(
        custom_output_text=(
            "# 요약\n"
            "스텁 모델 응답입니다.\n\n"
            "## 근거\n"
            "외부 LLM 키가 없어 TestModel이 생성했습니다.\n\n"
            "## 다음 단계\n"
            "Azure OpenAI 환경 변수를 설정하면 실제 추론이 동작합니다."
        ),
    )


def build_validator_model(settings: Settings):
    if settings.azure_openai_api_key and settings.azure_openai_endpoint and settings.azure_openai_deployment:
        client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
            api_key=settings.azure_openai_api_key,
        )
        return OpenAIChatModel(
            settings.azure_openai_deployment,
            provider=OpenAIProvider(openai_client=client),
        )
    return TestModel(
        custom_output_args={"passed": True, "violations": [], "suggestion": None},
    )


def build_main_agent(settings: Settings) -> Agent[None, str]:
    skills_md = load_skills_markdown(settings.resolved_skills_dir())
    system_chunks: list[str] = [
        "당신은 도구를 사용할 수 있는 자율 에이전트입니다.",
        "사용자가 한국어로 물으면 한국어로 간결히 답하세요.",
        "가능하면 search_news / run_python_analysis 도구를 활용하세요.",
    ]
    if skills_md:
        system_chunks.append("### 저장된 스킬\n" + skills_md)
    return Agent(
        build_main_model(settings),
        system_prompt="\n\n".join(system_chunks),
        tools=[search_news, run_python_analysis],
        output_type=str,
        end_strategy="exhaustive",
    )


def build_validator_agent(settings: Settings) -> Agent[None, ValidationOutcome]:
    rules = load_rules_text(settings.resolved_rules_path())
    rules_block = rules if rules else "(검증 규칙 파일이 비어 있음 — 비어 있지 않은 답변과 섹션 구조만 확인)"
    system_prompt = (
        "당신은 검증자입니다. 아래 검증 규칙 기준으로 에이전트 최종 답안이 규칙을 만족하는지 판단하고 "
        "ValidationOutcome 스키마에 맞게만 출력하세요.\n\n"
        f"### 검증 규칙\n{rules_block}"
    )
    return Agent(
        build_validator_model(settings),
        output_type=ValidationOutcome,
        system_prompt=system_prompt,
    )
