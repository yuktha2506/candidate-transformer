from __future__ import annotations
from canonical.schema import NormalizedValue

def normalize_name(value: object) -> NormalizedValue:
    if value is None:
        return NormalizedValue(value=None, success=False, method="missing name")
    text = str(value).strip()
    if not text:
        return NormalizedValue(value=None, success=False, method="empty name")
    return NormalizedValue(value=" ".join(part.capitalize() for part in text.split()), method="title case")

