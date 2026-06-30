from __future__ import annotations

from copy import deepcopy
from typing import Any

from canonical.schema import CanonicalProfile
from normalizers.record import normalize_field


def project_profile(profile: CanonicalProfile, config: dict[str, Any]) -> dict[str, Any]:
    source = profile.model_dump(mode="json")
    output: dict[str, Any] = {}
    missing_policy = config.get("missing_value_policy", "null")
    for field_config in config.get("fields", []):
        target = field_config["path"]
        source_path = field_config["from"]
        value = _get_path(source, source_path)
        if field_config.get("normalize_as") and value is not None:
            value = normalize_field(field_config["normalize_as"], value).value
        if value is None and missing_policy == "omit":
            continue
        output[target] = _missing_value(value, missing_policy)
    if config.get("include_confidence", True):
        output["field_confidence"] = deepcopy(source.get("field_confidence", {}))
        output["overall_confidence"] = source.get("overall_confidence", 0.0)
    if config.get("include_provenance", True):
        output["provenance"] = deepcopy(source.get("provenance", {}))
    return output


def project_profiles(profiles: list[CanonicalProfile], config: dict[str, Any]) -> list[dict[str, Any]]:
    return [project_profile(profile, config) for profile in profiles]


def _missing_value(value: Any, policy: str) -> Any:
    if value is not None:
        return value
    if policy == "empty_string":
        return ""
    if policy == "empty_list":
        return []
    return None


def _get_path(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for token in _tokenize(path):
        if isinstance(token, int):
            if not isinstance(current, list) or token >= len(current):
                return None
            current = current[token]
        else:
            if not isinstance(current, dict):
                return None
            current = current.get(token)
        if current is None:
            return None
    return current


def _tokenize(path: str) -> list[str | int]:
    tokens: list[str | int] = []
    for part in path.split("."):
        rest = part
        while "[" in rest:
            name, rest = rest.split("[", 1)
            if name:
                tokens.append(name)
            index, rest = rest.split("]", 1)
            tokens.append(int(index))
        if rest:
            tokens.append(rest)
    return tokens

