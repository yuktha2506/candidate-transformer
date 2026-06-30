from __future__ import annotations

from pathlib import Path

from canonical.schema import SourceType


def detect_source_type(path: Path, explicit: SourceType | None = None) -> SourceType | None:
    if explicit is not None:
        return explicit
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "recruiter_csv"
    if suffix == ".pdf":
        return "resume_pdf"
    if suffix == ".json":
        lowered = path.name.lower()
        return "github" if "github" in lowered else "ats_json"
    return None

