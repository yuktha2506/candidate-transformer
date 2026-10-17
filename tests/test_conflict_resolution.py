from canonical.schema import NormalizedRecord, NormalizedValue
from merger.conflict_resolution import choose_field, merge_group

def record(source_type: str, value: str, order: int = 0) -> NormalizedRecord:
    return NormalizedRecord(
        source_type=source_type,
        source_name=f"{source_type}.input",
        encountered_order=order,
        extracted_at=f"2026-01-0{order + 1}T00:00:00+00:00",
        fields={"current_company": NormalizedValue(value=value, method="test")},
    )


def test_highest_reliability_wins_conflict():
    decision = choose_field("current_company", [record("github", "OldCo"), record("resume_pdf", "NewCo")])
    assert decision.value == "NewCo"


def test_tie_uses_most_complete_value():
    decision = choose_field(
        "current_company",
        [record("ats_json", "ABC", 0), record("ats_json", "Alphabet Company", 1)],
    )
    assert decision.value == "Alphabet Company"


def test_merge_group_confidence_caps_at_one():
    source = NormalizedRecord(
        source_type="resume_pdf",
        source_name="resume.pdf",
        encountered_order=0,
        extracted_at="2026-01-01T00:00:00+00:00",
        fields={
            "email": NormalizedValue(value="a@example.com", method="test"),
            "name": NormalizedValue(value="Asha Rao", method="test"),
        },
    )
    profile = merge_group([source])
    assert profile.emails == ["a@example.com"]
    assert profile.field_confidence["emails"] == 0.95

