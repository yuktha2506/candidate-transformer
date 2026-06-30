from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from canonical.schema import RawRecord, SourceType
from provenance.provenance import make_provenance


FIELD_ALIASES = {
    "full_name": "name",
    "candidate_name": "name",
    "email_address": "email",
    "primary_email": "email",
    "phone_number": "phone",
    "mobile": "phone",
    "linkedin_url": "linkedin",
    "github_url": "github",
    "company": "current_company",
    "current_employer": "current_company",
    "job_title": "title",
    "job_role": "title",
    "current_title": "title",
    "position": "title",
    "role": "title",
    "location_country": "country",
}


def source_timestamp(path: Path) -> str:
    try:
        timestamp = path.stat().st_mtime
    except OSError:
        timestamp = 0
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def canonical_key(key: str) -> str:
    cleaned = key.strip().lower().replace(" ", "_").replace("-", "_")
    return FIELD_ALIASES.get(cleaned, cleaned)


def compact_fields(data: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for key, value in data.items():
        canonical = canonical_key(str(key))
        if value == "":
            fields[canonical] = None
        else:
            fields[canonical] = value
    return fields


def build_raw_record(
    source_type: SourceType,
    path: Path,
    encountered_order: int,
    fields: dict[str, Any],
    method: str,
) -> RawRecord:
    compacted = compact_fields(fields)
    return RawRecord(
        source_type=source_type,
        source_name=path.name,
        encountered_order=encountered_order,
        extracted_at=source_timestamp(path),
        fields=compacted,
        provenance={
            field: make_provenance(field=field, source=path.name, method=method)
            for field in compacted
        },
    )
