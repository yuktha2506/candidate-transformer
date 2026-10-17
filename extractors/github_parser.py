from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from canonical.schema import RawRecord
from extractors.common import build_raw_record


def _github_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": payload.get("name"),
        "email": payload.get("email"),
        "github": payload.get("html_url") or payload.get("github"),
        "current_company": payload.get("company"),
        "country": payload.get("location_country") or payload.get("country"),
        "skills": payload.get("skills") or payload.get("languages"),
        "title": payload.get("bio"),
    }


def extract_github_json(path: Path, start_order: int = 0) -> list[RawRecord]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    if not isinstance(payload, dict):
        return []
    return [
        build_raw_record(
            source_type="github",
            path=path,
            encountered_order=start_order,
            fields=_github_fields(payload),
            method="GitHub JSON field extraction",
        )
    ]

