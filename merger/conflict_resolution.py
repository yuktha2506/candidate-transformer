from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from canonical.schema import (
    SOURCE_RELIABILITY,
    CanonicalProfile,
    FieldDecision,
    NormalizedRecord,
)
from merger.confidence import field_confidence, overall_confidence
from provenance.provenance import make_merged_provenance, validate_provenance_consistency


SCALAR_FIELDS = ["name", "linkedin", "github", "current_company", "title", "country"]
LIST_FIELDS = {"email": "emails", "phone": "phones", "skills": "skills"}


@dataclass(frozen=True)
class ConflictResult:
    value: Any
    decision: FieldDecision
    winning_source: str | None
    contributing_sources: tuple[str, ...]


def _completeness(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (list, dict)):
        return len(value)
    return len(str(value).strip())


def _sort_key(field: str, record: NormalizedRecord) -> tuple[float, int, str, int]:
    value = record.fields[field].value
    return (
        SOURCE_RELIABILITY[record.source_type],
        _completeness(value),
        record.extracted_at,
        -record.encountered_order,
    )


def resolve_field(field: str, records: list[NormalizedRecord]) -> ConflictResult:
    candidates = [record for record in records if field in record.fields and record.fields[field].value not in (None, [], "")]
    if not candidates:
        decision = FieldDecision(value=None, confidence=0.0)
        return ConflictResult(None, decision, None, ())
    chosen = max(candidates, key=lambda record: _sort_key(field, record))
    value = chosen.fields[field].value
    decision = FieldDecision(
        value=value,
        confidence=field_confidence(field, value, chosen, records),
        provenance=chosen.provenance.get(field),
        source_type=chosen.source_type,
        normalization_success=chosen.fields[field].success,
        encountered_order=chosen.encountered_order,
    )
    return ConflictResult(
        value=value,
        decision=decision,
        winning_source=chosen.source_name,
        contributing_sources=_contributing_sources(candidates),
    )


def choose_field(field: str, records: list[NormalizedRecord]) -> FieldDecision:
    return resolve_field(field, records).decision


def merge_group(records: list[NormalizedRecord]) -> CanonicalProfile:
    resolutions: dict[str, ConflictResult] = {}
    for field in [*SCALAR_FIELDS, *LIST_FIELDS.keys()]:
        resolutions[field] = resolve_field(field, records)

    decisions = {field: result.decision for field, result in resolutions.items()}

    email_values = _ordered_unique_list("email", records)
    phone_values = _ordered_unique_list("phone", records)
    skill_values = _ordered_unique_skills(records)
    resolutions["email"] = _with_value(resolutions["email"], email_values)
    resolutions["phone"] = _with_value(resolutions["phone"], phone_values)
    resolutions["skills"] = _with_value(resolutions["skills"], skill_values)
    confidence_map = {
        canonical_field(field): decision.confidence
        for field, decision in decisions.items()
        if decision.value not in (None, [], "")
    }
    provenance = {
        canonical_field(field): make_merged_provenance(result)
        for field, result in resolutions.items()
        if result.winning_source is not None
    }
    candidate_id = _candidate_id(records, email_values, phone_values, decisions)
    profile = CanonicalProfile(
        candidate_id=candidate_id,
        name=decisions["name"].value,
        emails=email_values,
        phones=phone_values,
        linkedin=decisions["linkedin"].value,
        github=decisions["github"].value,
        current_company=decisions["current_company"].value,
        title=decisions["title"].value,
        country=decisions["country"].value,
        skills=skill_values,
        field_confidence=confidence_map,
        overall_confidence=overall_confidence(confidence_map),
        provenance=provenance,
    )
    canonical_resolutions = {
        canonical_field(field): result for field, result in resolutions.items()
    }
    canonical_values = {
        field: getattr(profile, field) for field in canonical_resolutions
    }
    validate_provenance_consistency(canonical_values, canonical_resolutions)
    return profile


def canonical_field(field: str) -> str:
    return LIST_FIELDS.get(field, field)


def _contributing_sources(records: list[NormalizedRecord]) -> tuple[str, ...]:
    sources: list[str] = []
    for record in sorted(records, key=lambda item: item.encountered_order):
        if record.source_name not in sources:
            sources.append(record.source_name)
    return tuple(sources)


def _with_value(result: ConflictResult, value: Any) -> ConflictResult:
    return ConflictResult(
        value=value,
        decision=result.decision,
        winning_source=result.winning_source,
        contributing_sources=result.contributing_sources,
    )


def _ordered_unique_list(field: str, records: list[NormalizedRecord]) -> list[str]:
    candidates = []
    for record in records:
        normalized = record.fields.get(field)
        if normalized and normalized.value:
            candidates.append((record, str(normalized.value)))
    candidates.sort(key=lambda item: _sort_key(field, item[0]), reverse=True)
    values: list[str] = []
    for _, value in candidates:
        if value not in values:
            values.append(value)
    return values


def _ordered_unique_skills(records: list[NormalizedRecord]) -> list[str]:
    rows: list[tuple[NormalizedRecord, str]] = []
    for record in records:
        normalized = record.fields.get("skills")
        if normalized and isinstance(normalized.value, list):
            rows.extend((record, skill) for skill in normalized.value)
    rows.sort(key=lambda item: _sort_key("skills", item[0]), reverse=True)
    skills: list[str] = []
    for _, skill in rows:
        if skill not in skills:
            skills.append(skill)
    return skills


def _candidate_id(
    records: list[NormalizedRecord],
    emails: list[str],
    phones: list[str],
    decisions: dict[str, FieldDecision],
) -> str:
    if emails:
        key = emails[0]
    elif phones:
        key = phones[0]
    elif decisions["linkedin"].value:
        key = decisions["linkedin"].value
    elif decisions["github"].value:
        key = decisions["github"].value
    elif decisions["name"].value and decisions["current_company"].value:
        key = f"{decisions['name'].value}|{decisions['current_company'].value}"
    else:
        key = f"{records[0].source_name}:{records[0].encountered_order}"
    return hashlib.sha256(str(key).strip().lower().encode("utf-8")).hexdigest()


def merge_records(records: list[NormalizedRecord]) -> list[CanonicalProfile]:
    from merger.identity_resolution import group_records

    return [merge_group(group) for group in group_records(records)]
