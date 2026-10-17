from __future__ import annotations
from canonical.schema import NormalizedValue

SKILL_MAP = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "java script": "JavaScript",
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "py": "Python",
    "python": "Python",
}


def normalize_skill(value: object) -> NormalizedValue:
    if value is None:
        return NormalizedValue(value=None, success=False, method="missing skill")
    skill = str(value).strip()
    if not skill:
        return NormalizedValue(value=None, success=False, method="empty skill")
    return NormalizedValue(value=SKILL_MAP.get(skill.lower(), skill), method="canonical skill mapping")


def normalize_skills(values: object) -> NormalizedValue:
    if values is None:
        return NormalizedValue(value=[], success=False, method="missing skills")
    items = values
    if isinstance(values, str):
        items = [part.strip() for part in values.replace(";", ",").split(",")]
    if not isinstance(items, list):
        return NormalizedValue(value=[], success=False, method="unsupported skills shape")
    normalized: list[str] = []
    for item in items:
        result = normalize_skill(item)
        if result.value and result.value not in normalized:
            normalized.append(result.value)
    return NormalizedValue(value=normalized, method="canonical skill list mapping")

