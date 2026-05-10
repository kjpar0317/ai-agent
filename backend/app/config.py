from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_repo_root() -> Path:
    # backend/app/config.py -> parents[2] == repository root
    return Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    azure_openai_endpoint: str | None = Field(default=None, alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str | None = Field(default=None, alias="AZURE_OPENAI_API_KEY")
    azure_openai_deployment: str | None = Field(default=None, alias="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_version: str = Field(
        default="2024-08-01-preview",
        alias="AZURE_OPENAI_API_VERSION",
    )

    database_url: str = Field(
        default="sqlite+aiosqlite:///:memory:",
        alias="DATABASE_URL",
    )

    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"],
        alias="CORS_ORIGINS",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> list[str]:
        if value is None:
            return ["http://localhost:5173", "http://127.0.0.1:5173"]
        if isinstance(value, str):
            parts = [p.strip() for p in value.split(",") if p.strip()]
            return parts or ["http://localhost:5173", "http://127.0.0.1:5173"]
        if isinstance(value, list):
            return [str(x) for x in value]
        raise TypeError("cors_origins must be a comma-separated string or a list of strings")

    repo_root: Path = Field(default_factory=_default_repo_root)

    skills_dir: Path | None = Field(default=None, alias="AGENT_SKILLS_DIR")
    rules_path: Path | None = Field(default=None, alias="AGENT_RULES_PATH")

    def resolved_skills_dir(self) -> Path:
        return self.skills_dir or (self.repo_root / ".cursor" / "skills")

    def resolved_rules_path(self) -> Path:
        return self.rules_path or (
            self.repo_root / ".cursor" / "rules" / "agent-output-validation.mdc"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
