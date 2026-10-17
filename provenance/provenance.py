from __future__ import annotations
from typing import Any, Mapping, Protocol
from canonical.schema import MergedProvenance, ProvenanceEntry


class ResolutionResult(Protocol):
    value: Any
    winning_source: str | None
    contributing_sources: tuple[str, ...]


def make_provenance(field: str, source: str, method: str) -> ProvenanceEntry:
    return ProvenanceEntry(field=field, source=source, method=method)


def make_merged_provenance(result: ResolutionResult) -> MergedProvenance:
    if result.winning_source is None:
        raise ValueError("Cannot create provenance without a winning source")
    return MergedProvenance(
        winning_source=result.winning_source,
        contributing_sources=list(result.contributing_sources),
        method="normalization + merge",
    )


def validate_provenance_consistency(
    canonical_values: Mapping[str, Any],
    resolutions: Mapping[str, ResolutionResult],
) -> None:
    """Ensure canonical values and provenance share one conflict decision."""
    for field, value in canonical_values.items():
        if value in (None, [], ""):
            continue
        result = resolutions.get(field)
        if result is None or result.value != value:
            raise ValueError(
                f"Provenance mismatch for '{field}': canonical value does not "
                "match the conflict resolution result"
            )
        if (
            result.winning_source is None
            or result.winning_source not in result.contributing_sources
        ):
            raise ValueError(
                f"Provenance mismatch for '{field}': winning source is not a contributor"
            )
