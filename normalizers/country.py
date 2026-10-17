from __future__ import annotations
import pycountry
from canonical.schema import NormalizedValue


def normalize_country(value: object) -> NormalizedValue:
    if value is None:
        return NormalizedValue(value=None, success=False, method="missing country")
    country = str(value).strip()
    if not country:
        return NormalizedValue(value=None, success=False, method="empty country")
    if len(country) == 2:
        match = pycountry.countries.get(alpha_2=country.upper())
        if match:
            return NormalizedValue(value=match.alpha_2, method="ISO alpha-2 country")
    try:
        match = pycountry.countries.lookup(country)
    except LookupError:
        return NormalizedValue(value=None, success=False, method="unknown country")
    return NormalizedValue(value=match.alpha_2, method="country lookup")

