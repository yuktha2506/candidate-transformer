from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from canonical.schema import RawRecord
from extractors.common import build_raw_record

def _flatten_candidate(data: dict[str, Any]) -> dict[str, Any]:
    flattened = dict(data)
    contact = flattened.pop("contact", None)
    if isinstance(contact, dict):
        flattened.update(contact)
    profile = flattened.pop("profile", None)
    if isinstance(profile, dict):
        flattened.update(profile)
    return flattened


def extract_ats_json(path: Path, start_order: int = 0) -> list[RawRecord]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    candidates = payload if isinstance(payload, list) else payload.get("candidates", payload)
    if isinstance(candidates, dict):
        candidates = [candidates]
    if not isinstance(candidates, list):
        return []
    records: list[RawRecord] = []
    for offset, item in enumerate(candidates):
        if not isinstance(item, dict):
            continue
        records.append(
            build_raw_record(
                source_type="ats_json",
                path=path,
                encountered_order=start_order + offset,
                fields=_flatten_candidate(item),
                method="JSON field extraction",
            )
        )
    return records

