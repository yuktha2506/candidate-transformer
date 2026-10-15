from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from normalizers.country import normalize_country
from normalizers.email import normalize_email
from normalizers.phone import normalize_phone


class OutputProfile(BaseModel):
    model_config = ConfigDict(extra="allow")

    candidate_id: str | None = None
    name: str | None = None
    primary_email: str | None = None
    emails: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    linkedin: str | None = None
    github: str | None = None
    current_company: str | None = None
    title: str | None = None
    country: str | None = None
    skills: list[str] = Field(default_factory=list)
    field_confidence: dict[str, float] | None = None
    overall_confidence: float | None = None
    provenance: dict[str, Any] | None = None

    @field_validator("primary_email")
    @classmethod
    def validate_primary_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_email(value).value

    @field_validator("emails")
    @classmethod
    def validate_emails(cls, values: list[str]) -> list[str]:
        return [email for email in (normalize_email(value).value for value in values) if email]

    @field_validator("phones")
    @classmethod
    def validate_phones(cls, values: list[str]) -> list[str]:
        return [phone for phone in (normalize_phone(value).value for value in values) if phone]

    @field_validator("country")
    @classmethod
    def validate_country(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_country(value).value


def validate_output(profile: dict[str, Any]) -> dict[str, Any]:
    try:
        # Projection owns field selection. Validation must not add defaults for
        # fields the runtime config did not request.
        return OutputProfile(**profile).model_dump(mode="json", exclude_unset=True)
    except ValidationError:
        # Projection configs may rename fields beyond the default schema. Preserve
        # deterministic output while removing values that fail known validators.
        cleaned = dict(profile)
        if "primary_email" in cleaned and normalize_email(cleaned["primary_email"]).value is None:
            cleaned["primary_email"] = None
        if "phones" in cleaned and isinstance(cleaned["phones"], list):
            cleaned["phones"] = [phone for phone in (normalize_phone(v).value for v in cleaned["phones"]) if phone]
        if "country" in cleaned and normalize_country(cleaned["country"]).value is None:
            cleaned["country"] = None
        return cleaned


def validate_outputs(profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [validate_output(profile) for profile in profiles]
