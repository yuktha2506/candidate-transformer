from __future__ import annotations
from typing import Any

from canonical.schema import NormalizedRecord, NormalizedValue, RawRecord
from normalizers.country import normalize_country
from normalizers.dates import normalize_month
from normalizers.email import normalize_email
from normalizers.name import normalize_name
from normalizers.phone import normalize_phone
from normalizers.skills import normalize_skills


def normalize_record(record: RawRecord, default_region: str = "US") -> NormalizedRecord:
    normalized: dict[str, NormalizedValue] = {}
    for field, value in record.fields.items():
        normalized[field] = normalize_field(field, value, default_region=default_region)
    return NormalizedRecord(
        source_type=record.source_type,
        source_name=record.source_name,
        encountered_order=record.encountered_order,
        extracted_at=record.extracted_at,
        fields=normalized,
        provenance=record.provenance,
    )


def normalize_field(field: str, value: Any, default_region: str = "US") -> NormalizedValue:
    if field == "name":
        return normalize_name(value)
    if field == "email":
        return normalize_email(value)
    if field == "phone":
        return normalize_phone(value, default_region=default_region)
    if field == "country":
        return normalize_country(value)
    if field == "skills":
        return normalize_skills(value)
    if field.endswith("_date") or field in {"start", "end", "start_date", "end_date"}:
        return normalize_month(value)
    if value is None or value == "":
        return NormalizedValue(value=None, success=False, method=f"missing {field}")
    return NormalizedValue(value=value, method="pass-through normalization")

