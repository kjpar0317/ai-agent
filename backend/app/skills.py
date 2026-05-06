from __future__ import annotations

from pathlib import Path


def load_skills_markdown(skills_dir: Path) -> str:
    if not skills_dir.is_dir():
        return ""
    chunks: list[str] = []
    for path in sorted(skills_dir.rglob("*.md")):
        rel = path.relative_to(skills_dir).as_posix()
        text = path.read_text(encoding="utf-8")
        chunks.append(f"### Skill: {rel}\n{text.strip()}")
    return "\n\n".join(chunks).strip()


def load_rules_text(rules_path: Path) -> str:
    if not rules_path.is_file():
        return ""
    return rules_path.read_text(encoding="utf-8").strip()
