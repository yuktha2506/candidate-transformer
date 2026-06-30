from canonical.schema import CanonicalProfile
from projection.projector import project_profile


def test_projection_selects_and_renames_fields():
    profile = CanonicalProfile(
        candidate_id="abc",
        name="Asha Rao",
        emails=["ASHA@EXAMPLE.COM"],
        country="India",
    )
    result = project_profile(
        profile,
        {
            "include_confidence": False,
            "include_provenance": False,
            "missing_value_policy": "null",
            "fields": [
                {"path": "primary_email", "from": "emails[0]", "normalize_as": "email"},
                {"path": "country_code", "from": "country", "normalize_as": "country"},
            ],
        },
    )
    assert result == {"primary_email": "asha@example.com", "country_code": "IN"}


def test_projection_omit_missing_values():
    profile = CanonicalProfile(candidate_id="abc")
    result = project_profile(
        profile,
        {
            "include_confidence": False,
            "include_provenance": False,
            "missing_value_policy": "omit",
            "fields": [{"path": "primary_email", "from": "emails[0]"}],
        },
    )
    assert result == {}

