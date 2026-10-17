from __future__ import annotations
import hashlib
import json

from canonical.schema import NormalizedRecord, NormalizedValue, ProvenanceEntry
from canonical.validator import validate_output
from extractors.github_parser import extract_github_json
from merger.conflict_resolution import merge_records
from projection.projector import project_profile


def record(
    source_type: str,
    source_name: str,
    order: int,
    fields: dict[str, object],
) -> NormalizedRecord:
    return NormalizedRecord(
        source_type=source_type,
        source_name=source_name,
        encountered_order=order,
        extracted_at=f"2026-01-0{order + 1}T00:00:00+00:00",
        fields={
            field: NormalizedValue(value=value, method="test normalization")
            for field, value in fields.items()
        },
        provenance={
            field: ProvenanceEntry(field=field, source=source_name, method="test extraction")
            for field in fields
        },
    )


def candidate_records() -> list[NormalizedRecord]:
    return [
        record(
            "recruiter_csv",
            "recruiter.csv",
            0,
            {
                "name": "Asha Rao",
                "email": "asha@example.com",
                "linkedin": "https://www.linkedin.com/in/asharao",
                "title": "Backend Engineer",
                "skills": ["JavaScript", "Python"],
            },
        ),
        record(
            "ats_json",
            "ats.json",
            1,
            {
                "name": "Asha Rao",
                "email": "asha@example.com",
                "phone": "+14155552671",
                "current_company": "Eightfold AI",
                "title": "Senior Backend Engineer",
            },
        ),
        record(
            "github",
            "github.json",
            2,
            {
                "name": "Asha Rao",
                "email": "asha@example.com",
                "github": "https://github.com/asharao",
                "current_company": "Eightfold",
                "country": "IN",
                "skills": ["Python", "React"],
            },
        ),
    ]


def test_multi_source_merge_populates_required_fields():
    profile = merge_records(candidate_records())[0]

    assert profile.emails == ["asha@example.com"]
    assert profile.phones == ["+14155552671"]
    assert profile.github == "https://github.com/asharao"
    assert profile.current_company == "Eightfold AI"
    assert profile.title == "Backend Engineer"
    assert profile.country == "IN"
    assert profile.candidate_id == hashlib.sha256(b"asha@example.com").hexdigest()


def test_merge_provenance_tracks_winner_and_contributors():
    profile = merge_records(candidate_records())[0]

    assert profile.provenance["current_company"].winning_source == "ats.json"
    assert profile.provenance["current_company"].contributing_sources == ["ats.json", "github.json"]
    assert profile.provenance["phones"].winning_source == "ats.json"
    assert profile.provenance["phones"].contributing_sources == ["ats.json"]
    assert profile.provenance["github"].winning_source == "github.json"
    assert profile.provenance["github"].contributing_sources == ["github.json"]
    assert profile.provenance["linkedin"].winning_source == "recruiter.csv"
    assert profile.provenance["skills"].winning_source == "recruiter.csv"
    assert profile.provenance["skills"].contributing_sources == ["recruiter.csv", "github.json"]


def test_provenance_uses_selected_record_not_extractor_metadata():
    records = candidate_records()
    records[1].provenance["current_company"] = ProvenanceEntry(
        field="current_company",
        source="recruiter.csv",
        method="incorrect upstream metadata",
    )
    records[1].provenance["phone"] = ProvenanceEntry(
        field="phone",
        source="recruiter.csv",
        method="incorrect upstream metadata",
    )

    profile = merge_records(records)[0]

    assert profile.provenance["current_company"].winning_source == "ats.json"
    assert profile.provenance["phones"].winning_source == "ats.json"


def test_every_populated_field_has_consistent_provenance():
    profile = merge_records(candidate_records())[0]
    fields = [
        "name",
        "emails",
        "phones",
        "current_company",
        "github",
        "linkedin",
        "skills",
        "title",
        "country",
    ]

    for field in fields:
        assert getattr(profile, field) not in (None, [], "")
        provenance = profile.provenance[field]
        assert provenance.winning_source in provenance.contributing_sources
        assert provenance.contributing_sources


def test_merge_is_deterministic():
    records = candidate_records()
    first = merge_records(records)[0].model_dump(mode="json")
    second = merge_records(list(reversed(records)))[0].model_dump(mode="json")
    assert first == second


def test_github_html_url_is_extracted(tmp_path):
    path = tmp_path / "github.json"
    path.write_text(
        json.dumps(
            {
                "name": "Asha Rao",
                "email": "asha@example.com",
                "html_url": "https://github.com/asharao",
            }
        ),
        encoding="utf-8",
    )

    extracted = extract_github_json(path)
    assert extracted[0].fields["github"] == "https://github.com/asharao"


def test_projection_and_validation_preserve_requested_arrays_only():
    profile = merge_records(candidate_records())[0]
    projected = project_profile(
        profile,
        {
            "include_confidence": False,
            "include_provenance": False,
            "missing_value_policy": "null",
            "fields": [
                {"path": "candidate_id", "from": "candidate_id"},
                {"path": "full_name", "from": "name"},
                {"path": "primary_email", "from": "emails[0]"},
                {"path": "emails", "from": "emails"},
                {"path": "phones", "from": "phones"},
            ],
        },
    )
    validated = validate_output(projected)

    assert validated["emails"] == ["asha@example.com"]
    assert validated["phones"] == ["+14155552671"]
    assert validated["primary_email"] == validated["emails"][0]
    assert "name" not in validated
