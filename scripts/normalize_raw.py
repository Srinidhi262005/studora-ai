#!/usr/bin/env python3
"""Studora AI - Phase 3.3 deterministic raw-content normalization.

The files under data/extracted are immutable inputs. This script writes a
separate normalized representation and a machine-readable audit report.
Normalization is deliberately representational: no academic interpretation,
metadata inference, or table repair is performed.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "extracted"
NORMALIZED_DIR = ROOT / "data" / "normalized"
NORMALIZATION_VERSION = "3.3.0"

INPUTS = {
    "python": RAW_DIR / "python_raw.jsonl",
    "dbms": RAW_DIR / "dbms_raw.jsonl",
    "jntuh": RAW_DIR / "jntuh_raw.jsonl",
}
OUTPUTS = {
    name: NORMALIZED_DIR / f"{name}_normalized.jsonl" for name in INPUTS
}

COMMON_PROVENANCE = (
    "source_id",
    "source_url",
    "provider",
    "local_path",
    "document_identity",
    "sha256",
    "extraction_timestamp",
    "record_index",
    "extraction_status",
)
FORBIDDEN_ADDED_FIELDS = {
    "university",
    "regulation",
    "regulation_year",
    "program",
    "semester",
    "course_code",
    "course_title",
    "unit",
    "topic",
    "subtopic",
    "canonical_topic",
}
HORIZONTAL_WHITESPACE = re.compile(r"[^\S\r\n]+")
EXCESS_BLANK_LINES = re.compile(r"\n{3,}")


class NormalizationError(ValueError):
    """Raised when an input record is malformed or structurally unexpected."""


def normalize_text(value: str, *, preserve_code: bool = False) -> tuple[str, bool]:
    """Remove extraction-only outer and horizontal whitespace.

    Newlines are retained because they can represent source structure. Code
    blocks retain all internal whitespace and only normalize line endings.
    """
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    if not preserve_code:
        normalized = HORIZONTAL_WHITESPACE.sub(" ", normalized)
        normalized = EXCESS_BLANK_LINES.sub("\n\n", normalized)
        normalized = normalized.strip()
    changed = normalized != value
    return normalized, changed


def normalize_value(value: Any, *, preserve_code: bool = False) -> tuple[Any, bool]:
    if isinstance(value, str):
        return normalize_text(value, preserve_code=preserve_code)
    if isinstance(value, list):
        result = []
        changed = False
        for item in value:
            normalized, item_changed = normalize_value(
                item, preserve_code=preserve_code
            )
            result.append(normalized)
            changed = changed or item_changed
        return result, changed
    if isinstance(value, dict):
        result = {}
        changed = False
        for key, item in value.items():
            normalized, item_changed = normalize_value(
                item, preserve_code=preserve_code
            )
            result[key] = normalized
            changed = changed or item_changed
        return result, changed
    return copy.deepcopy(value), False


def require(condition: bool, message: str) -> None:
    if not condition:
        raise NormalizationError(message)


def validate_record(record: Any, source: str, line_number: int) -> None:
    require(
        isinstance(record, dict),
        f"{source}: line {line_number}: expected a JSON object",
    )
    for field in COMMON_PROVENANCE:
        require(
            field in record,
            f"{source}: line {line_number}: missing required field {field}",
        )
    require(
        isinstance(record["record_index"], int)
        and not isinstance(record["record_index"], bool),
        f"{source}: line {line_number}: record_index must be an integer",
    )
    require(
        isinstance(record.get("block_type"), str) and record["block_type"],
        f"{source}: line {line_number}: block_type must be non-empty",
    )
    require(
        isinstance(record.get("extracted_text"), str),
        f"{source}: line {line_number}: extracted_text must be a string",
    )
    block_type = record["block_type"]
    if block_type == "list":
        require(
            isinstance(record.get("list_items"), list)
            and all(isinstance(item, str) for item in record["list_items"]),
            f"{source}: line {line_number}: list_items must be a list of strings",
        )
    if block_type == "definition_list":
        pairs = record.get("definition_pairs")
        require(
            isinstance(pairs, list),
            f"{source}: line {line_number}: definition_pairs must be a list",
        )
        for pair in pairs:
            require(
                isinstance(pair, dict)
                and isinstance(pair.get("term"), str)
                and isinstance(pair.get("definition"), str),
                f"{source}: line {line_number}: malformed definition pair",
            )
    if block_type == "table":
        table = record.get("table_data")
        require(
            isinstance(table, list)
            and all(
                isinstance(row, list) and all(isinstance(cell, str) for cell in row)
                for row in table
            ),
            f"{source}: line {line_number}: table_data must be a list of string rows",
        )


def validate_no_academic_fields_added(raw: dict[str, Any], normalized: dict[str, Any]) -> None:
    added = (set(normalized) - set(raw)) & FORBIDDEN_ADDED_FIELDS
    if added:
        raise NormalizationError(
            f"record {raw.get('record_index')}: normalization added academic fields: "
            + ", ".join(sorted(added))
        )


def normalize_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Normalize content fields without rewriting provenance or heading metadata."""
    normalized = copy.deepcopy(record)
    changed = False

    text, text_changed = normalize_text(
        record["extracted_text"], preserve_code=record["block_type"] == "code"
    )
    normalized["extracted_text"] = text
    changed = changed or text_changed

    if "page_text" in record:
        page_text, page_changed = normalize_text(record["page_text"])
        normalized["page_text"] = page_text
        changed = changed or page_changed

    if record["block_type"] == "list":
        items, items_changed = normalize_value(record["list_items"])
        normalized["list_items"] = items
        changed = changed or items_changed
    elif record["block_type"] == "definition_list":
        pairs, pairs_changed = normalize_value(record["definition_pairs"])
        normalized["definition_pairs"] = pairs
        changed = changed or pairs_changed
    elif record["block_type"] == "table":
        table, table_changed = normalize_value(record["table_data"])
        normalized["table_data"] = table
        changed = changed or table_changed

    return normalized, changed


def normalize_file(source: str, input_path: Path, output_path: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    changed = 0
    whitespace_changes = 0
    structured_records = 0
    warnings: list[str] = []

    with input_path.open("r", encoding="utf-8", newline="") as source_file:
        for line_number, line in enumerate(source_file, start=1):
            if not line.strip():
                raise NormalizationError(f"{source}: line {line_number}: blank JSONL line")
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise NormalizationError(
                    f"{source}: line {line_number}: malformed JSON: {exc}"
                ) from exc
            validate_record(record, source, line_number)
            normalized, record_changed = normalize_record(record)
            validate_record(normalized, source, line_number)
            validate_no_academic_fields_added(record, normalized)
            if record["block_type"] in {"list", "definition_list", "table"}:
                structured_records += 1
            if record_changed:
                changed += 1
                whitespace_changes += 1
            if record["block_type"] == "table":
                rows = normalized["table_data"]
                lengths = {len(row) for row in rows}
                if len(lengths) > 1:
                    warnings.append(
                        f"record {record['record_index']}: table rows have inconsistent lengths"
                    )
            records.append(normalized)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as output_file:
        for record in records:
            output_file.write(
                json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                + "\n"
            )

    return {
        "input_file": str(input_path.relative_to(ROOT)),
        "output_file": str(output_path.relative_to(ROOT)),
        "input_record_count": len(records),
        "output_record_count": len(records),
        "records_changed": changed,
        "records_unchanged": len(records) - changed,
        "whitespace_changes": whitespace_changes,
        "structured_records_preserved": structured_records,
        "validation_warnings": warnings,
        "errors": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    if root != ROOT:
        raise SystemExit("--root must point to the repository root")

    report = {
        "normalization_version": NORMALIZATION_VERSION,
        "inputs": [],
        "total_input_record_count": 0,
        "total_output_record_count": 0,
        "total_records_changed": 0,
        "total_records_unchanged": 0,
        "total_records_dropped": 0,
    }
    try:
        for source, input_path in INPUTS.items():
            output_path = OUTPUTS[source]
            result = normalize_file(source, input_path, output_path)
            report["inputs"].append(result)
            report["total_input_record_count"] += result["input_record_count"]
            report["total_output_record_count"] += result["output_record_count"]
            report["total_records_changed"] += result["records_changed"]
            report["total_records_unchanged"] += result["records_unchanged"]
    except (OSError, NormalizationError) as exc:
        print(f"Normalization failed: {exc}", file=sys.stderr)
        return 1

    report["total_records_dropped"] = (
        report["total_input_record_count"] - report["total_output_record_count"]
    )
    report_path = NORMALIZED_DIR / "normalization_report.json"
    with report_path.open("w", encoding="utf-8", newline="\n") as report_file:
        json.dump(report, report_file, ensure_ascii=False, indent=2)
        report_file.write("\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
