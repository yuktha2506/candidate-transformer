from __future__ import annotations

from canonical.schema import NormalizedRecord


def identity_key(record: NormalizedRecord) -> tuple[str, str]:
    fields = record.fields
    for field in ("email", "phone", "linkedin", "github"):
        value = fields.get(field)
        if value and value.value:
            return field, str(value.value).lower()
    name = fields.get("name")
    company = fields.get("current_company")
    if name and name.value and company and company.value:
        return "name_current_company", f"{name.value}|{company.value}".lower()
    return "record", f"{record.source_name}:{record.encountered_order}"


def group_records(records: list[NormalizedRecord]) -> list[list[NormalizedRecord]]:
    if not records:
        return []

    parents = list(range(len(records)))

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    # Process exact identifiers in the specified priority order. This allows a
    # lower-priority identifier to connect records only when email did not.
    for fields in (("email",), ("phone",), ("linkedin",), ("github",), ("name", "current_company")):
        seen: dict[tuple[str, ...], int] = {}
        for index, record in enumerate(records):
            values: list[str] = []
            for field in fields:
                normalized = record.fields.get(field)
                if not normalized or not normalized.value:
                    values = []
                    break
                values.append(str(normalized.value).strip().lower())
            if not values:
                continue
            key = tuple(values)
            if key in seen:
                union(seen[key], index)
            else:
                seen[key] = index

    grouped: dict[int, list[NormalizedRecord]] = {}
    for index, record in enumerate(records):
        grouped.setdefault(find(index), []).append(record)
    return list(grouped.values())
