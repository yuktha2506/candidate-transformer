from canonical.schema import NormalizedRecord, NormalizedValue
from merger.identity_resolution import group_records, identity_key

def record(fields: dict, order: int = 0) -> NormalizedRecord:
    return NormalizedRecord(
        source_type="recruiter_csv",
        source_name="test.csv",
        encountered_order=order,
        extracted_at="2026-01-01T00:00:00+00:00",
        fields={key: NormalizedValue(value=value, method="test") for key, value in fields.items()},
    )


def test_identity_priority_email_before_phone():
    item = record({"email": "a@example.com", "phone": "+14155552671"})
    assert identity_key(item) == ("email", "a@example.com")


def test_identity_falls_back_to_name_company():
    item = record({"name": "Asha Rao", "current_company": "Eightfold"})
    assert identity_key(item) == ("name_current_company", "asha rao|eightfold")


def test_group_records_merges_duplicate_email():
    groups = group_records([record({"email": "a@example.com"}, 0), record({"email": "a@example.com"}, 1)])
    assert len(groups) == 1
    assert len(groups[0]) == 2

