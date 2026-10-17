from __future__ import annotations
from email_validator import EmailNotValidError, validate_email
from canonical.schema import NormalizedValue


def normalize_email(value: object) -> NormalizedValue:
    if value is None:
        return NormalizedValue(value=None, success=False, method="missing email")
    email = str(value).strip().lower()
    if not email:
        return NormalizedValue(value=None, success=False, method="empty email")
    try:
        validated = validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return NormalizedValue(value=None, success=False, method="email-validator rejection")
    return NormalizedValue(value=validated.normalized, method="trim lower validate")

