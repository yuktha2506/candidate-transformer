from __future__ import annotations
from canonical.schema import SOURCE_RELIABILITY, NormalizedRecord

FIELD_WEIGHTS = {
    "name": 1.0,
    "email": 1.5,
    "phone": 1.3,
    "linkedin": 0.8,
    "github": 0.8,
    "current_company": 1.0,
    "title": 0.7,
    "country": 0.7,
    "skills": 1.0,
}


def cross_source_agreement(field: str, value: object, records: list[NormalizedRecord]) -> float:
    if value is None:
        return 1.0
    matches = 0
    source_types: set[str] = set()
    for record in records:
        candidate = record.fields.get(field)
        if candidate and candidate.value == value:
            matches += 1
            source_types.add(record.source_type)
    return 1.1 if matches > 1 and len(source_types) > 1 else 1.0


def field_confidence(
    field: str,
    value: object,
    chosen_record: NormalizedRecord,
    records: list[NormalizedRecord],
) -> float:
    source_reliability = SOURCE_RELIABILITY[chosen_record.source_type]
    normalized = chosen_record.fields[field]
    normalization_success = 1.0 if normalized.success else 0.7
    agreement = cross_source_agreement(field, value, records)
    return min(1.0, round(source_reliability * normalization_success * agreement, 4))


def overall_confidence(field_confidence_map: dict[str, float]) -> float:
    numerator = 0.0
    denominator = 0.0
    for field, confidence in field_confidence_map.items():
        weight = FIELD_WEIGHTS.get(field, 0.5)
        numerator += confidence * weight
        denominator += weight
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)

