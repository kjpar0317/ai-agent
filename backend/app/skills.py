from __future__ import annotations

from pathlib import Path


def _skill_excluded_from_app_runtime(text: str) -> bool:
    """SKILL.md 프론트매터에 app-runtime: false이면 FastAPI 에이전트에는 주입하지 않는다."""
    stripped = text.lstrip("\ufeff")
    if not stripped.startswith("---"):
        return False
    lines = stripped.splitlines()
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, _, val = line.partition(":")
        if key.strip().lower() == "app-runtime" and val.strip().lower() in ("false", "no", "0"):
            return True
    return False


def load_skills_markdown(skills_dir: Path) -> str:
    """각 스킬 디렉터리의 SKILL.md만 합친다. Cursor 전용 스킬은 app-runtime: false로 제외한다."""
    if not skills_dir.is_dir():
        return ""
    chunks: list[str] = []
    for path in sorted(skills_dir.rglob("SKILL.md")):
        text = path.read_text(encoding="utf-8")
        if _skill_excluded_from_app_runtime(text):
            continue
        rel = path.relative_to(skills_dir).as_posix()
        chunks.append(f"### Skill: {rel}\n{text.strip()}")
    return "\n\n".join(chunks).strip()


def _strip_cursor_rule_frontmatter(raw: str) -> str:
    """`.cursor/rules/*.mdc` 상단 YAML 프론트매터를 제거해 본문만 반환한다."""
    text = raw.strip()
    if not text.startswith("---"):
        return raw.strip()
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return raw.strip()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1 :]).strip()
    return raw.strip()


def load_rules_text(rules_path: Path) -> str:
    if not rules_path.is_file():
        return ""
    raw = rules_path.read_text(encoding="utf-8").strip()
    if rules_path.suffix.lower() == ".mdc":
        return _strip_cursor_rule_frontmatter(raw)
    return raw
