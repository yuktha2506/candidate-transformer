from __future__ import annotations

import phonenumbers

from canonical.schema import NormalizedValue


def normalize_phone(value: object, default_region: str = "US") -> NormalizedValue:
    if value is None:
        return NormalizedValue(value=None, success=False, method="missing phone")
    raw = str(value).strip()
    if not raw:
        return NormalizedValue(value=None, success=False, method="empty phone")
    try:
        parsed = phonenumbers.parse(raw, default_region)
    except phonenumbers.NumberParseException:
        return NormalizedValue(value=None, success=False, method="phonenumbers parse failure")
    if not phonenumbers.is_valid_number(parsed):
        return NormalizedValue(value=None, success=False, method="invalid phone")
    return NormalizedValue(
        value=phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
        method="E.164 normalization",
    )

