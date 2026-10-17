from __future__ import annotations
import re
from pathlib import Path
import pdfplumber
from canonical.schema import RawRecord
from extractors.common import build_raw_record


EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:\+\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,5}\d{2,4}")
LINKEDIN_RE = re.compile(r"https?://(?:www\.)?linkedin\.com/[^\s)]+", re.IGNORECASE)
GITHUB_RE = re.compile(r"https?://(?:www\.)?github\.com/[^\s)]+", re.IGNORECASE)
SKILLS_RE = re.compile(r"skills?\s*[:\-]\s*(.+)", re.IGNORECASE)


def _text_from_pdf(path: Path) -> str | None:
    try:
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
    except (FileNotFoundError, OSError, Exception):
        return None
    text = "\n".join(pages).strip()
    return text or None


def _first_nonempty_line(text: str) -> str | None:
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned:
            return cleaned
    return None


def _extract_skills(text: str) -> list[str]:
    for line in text.splitlines():
        match = SKILLS_RE.search(line)
        if match:
            return [part.strip() for part in re.split(r"[,;|]", match.group(1)) if part.strip()]
    return []


def extract_resume_pdf(path: Path, start_order: int = 0) -> list[RawRecord]:
    text = _text_from_pdf(path)
    if text is None:
        return []
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    linkedin = LINKEDIN_RE.search(text)
    github = GITHUB_RE.search(text)
    fields = {
        "name": _first_nonempty_line(text),
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
        "skills": _extract_skills(text),
        "resume_text": text,
    }
    return [
        build_raw_record(
            source_type="resume_pdf",
            path=path,
            encountered_order=start_order,
            fields=fields,
            method="regex extraction",
        )
    ]

