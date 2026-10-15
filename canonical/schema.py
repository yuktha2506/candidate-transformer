from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


SourceType = Literal["recruiter_csv", "ats_json", "resume_pdf", "github"]


SOURCE_RELIABILITY: dict[SourceType, float] = {
    "resume_pdf": 0.95,
    "recruiter_csv": 0.90,
    "ats_json": 0.88,
    "github": 0.75,
}


class ProvenanceEntry(BaseModel):
    field: str
    source: str
    method: str


class MergedProvenance(BaseModel):
    winning_source: str
    contributing_sources: list[str] = Field(default_factory=list)
    method: str = "normalization + merge"


class RawRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_type: SourceType
    source_name: str
    encountered_order: int
    extracted_at: str
    fields: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, ProvenanceEntry] = Field(default_factory=dict)


class NormalizedValue(BaseModel):
    value: Any = None
    success: bool = True
    method: str


class NormalizedRecord(BaseModel):
    source_type: SourceType
    source_name: str
    encountered_order: int
    extracted_at: str
    fields: dict[str, NormalizedValue] = Field(default_factory=dict)
    provenance: dict[str, ProvenanceEntry] = Field(default_factory=dict)


class FieldDecision(BaseModel):
    value: Any = None
    confidence: float = 0.0
    provenance: ProvenanceEntry | None = None
    source_type: SourceType | None = None
    normalization_success: bool = True
    encountered_order: int = 0


class CanonicalProfile(BaseModel):
    candidate_id: str
    name: str | None = None
    emails: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    linkedin: str | None = None
    github: str | None = None
    current_company: str | None = None
    title: str | None = None
    country: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    field_confidence: dict[str, float] = Field(default_factory=dict)
    overall_confidence: float = 0.0
    provenance: dict[str, MergedProvenance] = Field(default_factory=dict)
