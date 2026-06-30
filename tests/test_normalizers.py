from normalizers.email import normalize_email
from normalizers.phone import normalize_phone
from normalizers.skills import normalize_skill, normalize_skills


def test_phone_normalization_to_e164():
    result = normalize_phone("(415) 555-2671", default_region="US")
    assert result.value == "+14155552671"
    assert result.success is True


def test_invalid_phone_becomes_null():
    result = normalize_phone("not-a-number")
    assert result.value is None
    assert result.success is False


def test_email_normalization():
    result = normalize_email("  USER@Example.COM ")
    assert result.value == "user@example.com"


def test_invalid_email_becomes_null():
    result = normalize_email("bad-email")
    assert result.value is None


def test_skill_normalization_known_and_unknown():
    assert normalize_skill("JS").value == "JavaScript"
    assert normalize_skill("ReactJS").value == "React"
    assert normalize_skill("Py").value == "Python"
    assert normalize_skill("Rust").value == "Rust"


def test_skill_list_deduplicates_deterministically():
    result = normalize_skills("JS, Javascript, Py, Unknown")
    assert result.value == ["JavaScript", "Python", "Unknown"]

