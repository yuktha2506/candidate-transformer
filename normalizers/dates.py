from __future__ import annotations

from dateutil import parser

from canonical.schema import NormalizedValue


def normalize_month(value: object) -> NormalizedValue:
    if value is None:
        return NormalizedValue(value=None, success=False, method="missing date")
    text = str(value).strip()
    if not text:
        return NormalizedValue(value=None, success=False, method="empty date")
    try:
        parsed = parser.parse(text, default=parser.parse("1900-01-01"))
    except (ValueError, OverflowError):
        return NormalizedValue(value=None, success=False, method="date parse failure")
    return NormalizedValue(value=f"{parsed.year:04d}-{parsed.month:02d}", method="YYYY-MM date normalization")

