from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from canonical.schema import RawRecord
from canonical.validator import validate_outputs
from extractors.ats_json_extractor import extract_ats_json
from extractors.csv_extractor import extract_recruiter_csv
from extractors.github_parser import extract_github_json
from extractors.resume_parser import extract_resume_pdf
from merger.conflict_resolution import merge_records
from normalizers.record import normalize_record
from projection.projector import project_profiles


DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "default_config.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-Source Candidate Data Transformer")
    parser.add_argument("--csv", type=Path, help="Recruiter CSV input")
    parser.add_argument("--ats", type=Path, help="ATS JSON input")
    parser.add_argument("--resume", type=Path, help="Resume PDF input")
    parser.add_argument("--github", type=Path, help="GitHub profile JSON input")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Projection config JSON")
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    try:
        with DEFAULT_CONFIG_PATH.open(encoding="utf-8") as default_file:
            config = json.load(default_file)
        if path != DEFAULT_CONFIG_PATH:
            with path.open(encoding="utf-8") as custom_file:
                config.update(json.load(custom_file))
        return config
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        with DEFAULT_CONFIG_PATH.open(encoding="utf-8") as default_file:
            return json.load(default_file)


def collect_raw_records(args: argparse.Namespace) -> list[RawRecord]:
    records: list[RawRecord] = []
    extractors = [
        (args.csv, extract_recruiter_csv),
        (args.ats, extract_ats_json),
        (args.resume, extract_resume_pdf),
        (args.github, extract_github_json),
    ]
    for path, extractor in extractors:
        if path is None:
            continue
        records.extend(extractor(path, start_order=len(records)))
    return records


def run_pipeline(args: argparse.Namespace) -> list[dict[str, Any]]:
    config = load_config(args.config)
    raw_records = collect_raw_records(args)
    default_region = config.get("default_phone_region", "US")
    normalized_records = [normalize_record(record, default_region=default_region) for record in raw_records]
    canonical_profiles = merge_records(normalized_records)
    projected = project_profiles(canonical_profiles, config)
    return validate_outputs(projected)


def main() -> None:
    args = parse_args()
    output = run_pipeline(args)
    config = load_config(args.config)
    output_path = Path(config.get("output_file", "candidate_profile.json"))
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {output_path}")

