# Multi-Source Candidate Data Transformer

Production-quality Python 3.11 implementation of a deterministic candidate data transformer. It merges messy candidate data from recruiter CSV, ATS JSON, resume PDF, and GitHub JSON into canonical candidate profiles with provenance and confidence.

## Installation

```bash
cd D:\candidate_transformer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Dependencies

- pydantic
- pandas
- json
- pathlib
- pdfplumber
- phonenumbers
- email-validator
- pycountry
- python-dateutil

## Folder Structure

```text
candidate_transformer/
  main.py
  cli.py
  config/
  canonical/
  extractors/
  normalizers/
  merger/
  projection/
  provenance/
  tests/
  sample_inputs/
```

## Run

```bash
python main.py --csv sample_inputs/recruiter.csv --ats sample_inputs/ats.json --github sample_inputs/github.json
```
```bash
python main.py --csv sample_inputs/recruiter.csv --ats sample_inputs/ats.json --resume sample_inputs/resume.pdf --github sample_inputs/github.json --config config/custom_config.json
```
With a resume:

```bash
python main.py --csv sample_inputs/recruiter.csv --resume sample_inputs/resume.pdf --github sample_inputs/github.json --config config/custom_config.json
```

The default output file is `candidate_profile.json`.

## Design Explanation

The pipeline is split into the required stages:

1. Source detection and extraction modules read source-specific data into `RawRecord`.
2. Normalizers convert names, emails, phones, dates, countries, and skills without inventing values.
3. Identity resolution groups records by email, phone, LinkedIn, GitHub, then name plus current company.
4. Conflict resolution chooses values by source reliability, completeness, newest source, then first encountered.
5. Confidence is calculated as source reliability times normalization success times cross-source agreement, capped at 1.0.
6. Provenance stores field, source, and method for every extracted field.
7. Projection uses runtime config to select, rename, normalize, include confidence/provenance, and apply missing value policy.
8. Validation runs before writing schema-valid JSON.

All stages are deterministic, modular, and designed to fail gracefully. Missing, invalid, malformed, or corrupted inputs return empty records or null values instead of crashing the pipeline.

## Example Output

```json
[
  {
    "candidate_id": "375b62ed083a9df1",
    "name": "Asha Rao",
    "primary_email": "asha@example.com",
    "emails": ["asha@example.com"],
    "phones": ["+14155552671"],
    "country": "IN",
    "skills": ["JavaScript", "Python", "React"],
    "overall_confidence": 0.93
  }
]
```

## Tests

```bash
pytest
```

Unit tests cover phone normalization, email normalization, skill normalization, identity resolution, conflict resolution, and projection.

