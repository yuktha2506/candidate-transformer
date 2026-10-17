from __future__ import annotations
from pathlib import Path
import pandas as pd
from canonical.schema import RawRecord
from extractors.common import build_raw_record


def extract_recruiter_csv(path: Path, start_order: int = 0) -> list[RawRecord]:
    try:
        frame = pd.read_csv(path)
    except (pd.errors.EmptyDataError, FileNotFoundError, OSError, UnicodeDecodeError):
        return []
    if frame.empty:
        return []
    records: list[RawRecord] = []
    for offset, row in enumerate(frame.to_dict(orient="records")):
        fields = {key: (None if pd.isna(value) else value) for key, value in row.items()}
        records.append(
            build_raw_record(
                source_type="recruiter_csv",
                path=path,
                encountered_order=start_order + offset,
                fields=fields,
                method="pandas CSV extraction",
            )
        )
    return records

