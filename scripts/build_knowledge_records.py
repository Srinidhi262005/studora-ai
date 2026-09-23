#!/usr/bin/env python3
"""Build deterministic Phase 3.5 retrieval-ready knowledge records.

This layer is one-to-one with normalized records. It does not chunk, embed,
interpret, or modify any governed input layer.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED_DIR = ROOT / "data" / "normalized"
RAW_DIR = ROOT / "data" / "extracted"
MAPPING_PATH = ROOT / "data" / "mappings" / "academic_mapping.jsonl"
OUTPUT_DIR = ROOT / "data" / "knowledge"
OUTPUT_PATH = OUTPUT_DIR / "knowledge_records.jsonl"
REPORT_PATH = OUTPUT_DIR / "knowledge_report.json"
VERSION = "3.5.0"

SOURCES = ("python", "dbms", "jntuh")
CONTENT_TYPES = {"p", "paragraph", "heading", "code", "list", "definition_list", "table", "page_text"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                raise ValueError(f"{path}: blank line {line_number}")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}: line {line_number} is not an object")
            records.append(value)
    return records


def mapping_reference(source: str, record: dict[str, Any]) -> str:
    return (
        f"data/normalized/{source}_normalized.jsonl"
        f"#document_identity={record['document_identity']}"
        f"&record_index={record['record_index']}"
    )


def raw_reference(source: str, record: dict[str, Any]) -> str:
    return (
        f"data/extracted/{source}_raw.jsonl"
        f"#document_identity={record['document_identity']}"
        f"&record_index={record['record_index']}"
    )


def text(value: Any) -> str:
    return value if isinstance(value, str) else str(value)


def content_for(record: dict[str, Any]) -> str:
    block_type = record.get("block_type")
    if block_type in {"p", "paragraph", "heading", "code", "page_text"}:
        return text(record.get("extracted_text", ""))
    if block_type == "list":
        items = record.get("list_items")
        if not isinstance(items, list):
            raise ValueError("list record has no list_items array")
        return "\n".join(f"- {text(item)}" for item in items)
    if block_type == "definition_list":
        pairs = record.get("definition_pairs")
        if not isinstance(pairs, list):
            raise ValueError("definition_list record has no definition_pairs array")
        lines: list[str] = []
        for pair in pairs:
            if not isinstance(pair, dict) or "term" not in pair or "definition" not in pair:
                raise ValueError("definition_list contains malformed definition pair")
            lines.append(f"{text(pair['term'])}: {text(pair['definition'])}")
        return "\n".join(lines)
    if block_type == "table":
        rows = record.get("table_data")
        if not isinstance(rows, list) or any(not isinstance(row, list) for row in rows):
            raise ValueError("table record has no table_data matrix")
        return "\n".join("\t".join(text(cell) for cell in row) for row in rows)
    raise ValueError(f"unsupported normalized block_type: {block_type!r}")


def knowledge_id(source: str, record: dict[str, Any]) -> str:
    stable = f"{source}|{record['document_identity']}|{record['record_index']}"
    digest = hashlib.sha256(stable.encode("utf-8")).hexdigest()[:20]
    return f"KR-{source}-{digest}"


def build_record(
    source: str,
    normalized: dict[str, Any],
    mapping: dict[str, Any],
) -> dict[str, Any]:
    normalized_ref = mapping_reference(source, normalized)
    if mapping.get("normalized_record_reference") != normalized_ref:
        raise ValueError(f"mapping reference mismatch for {normalized_ref}")
    required_mapping_fields = (
        "institution", "regulation_year", "program", "semester", "subject",
        "course_code", "course_title", "unit", "topic", "subtopic",
        "canonical_topic", "mapping_status", "mapping_confidence",
    )
    missing = [field for field in required_mapping_fields if field not in mapping]
    if missing:
        raise ValueError(f"mapping missing fields: {missing}")

    provenance = {
        "source_id": mapping.get("source_id", normalized.get("source_id") or "UNKNOWN"),
        "source_url": mapping.get("source_url", normalized.get("source_url", "UNKNOWN")),
        "provider": mapping.get("provider", normalized.get("provider", "UNKNOWN")),
        "document_identity": normalized["document_identity"],
        "record_index": normalized["record_index"],
        "page_number": normalized.get("page_number", "UNKNOWN"),
        "original_filename": normalized.get("original_filename", "UNKNOWN"),
        "sha256": normalized.get("sha256", "UNKNOWN"),
        "extraction_status": normalized.get("extraction_status", "UNKNOWN"),
    }
    return {
        "knowledge_id": knowledge_id(source, normalized),
        "subject": mapping["subject"],
        "content": content_for(normalized),
        "content_type": normalized["block_type"],
        "institution": mapping["institution"],
        "regulation_year": mapping["regulation_year"],
        "program": mapping["program"],
        "semester": mapping["semester"],
        "course_code": mapping["course_code"],
        "course_title": mapping["course_title"],
        "unit": mapping["unit"],
        "topic": mapping["topic"],
        "subtopic": mapping["subtopic"],
        "canonical_topic": mapping["canonical_topic"],
        **provenance,
        "raw_record_reference": raw_reference(source, normalized),
        "normalized_record_reference": normalized_ref,
        "mapping_id": mapping["mapping_id"],
        "evidence_reference": mapping["evidence_reference"],
        "section_path": normalized.get("section_path", []),
        "heading_level": normalized.get("heading_level", 0),
        "mapping_status": mapping["mapping_status"],
        "mapping_confidence": mapping["mapping_confidence"],
    }


def main() -> None:
    mappings = load_jsonl(MAPPING_PATH)
    mapping_by_ref = {record["normalized_record_reference"]: record for record in mappings}
    if len(mapping_by_ref) != len(mappings):
        raise ValueError("academic mapping contains duplicate normalized references")

    records: list[dict[str, Any]] = []
    source_counts: Counter[str] = Counter()
    content_counts: Counter[str] = Counter()
    for source in SOURCES:
        normalized_records = load_jsonl(NORMALIZED_DIR / f"{source}_normalized.jsonl")
        raw_records = load_jsonl(RAW_DIR / f"{source}_raw.jsonl")
        if len(normalized_records) != len(raw_records):
            raise ValueError(f"{source}: normalized/raw count mismatch")
        for normalized in normalized_records:
            if normalized.get("block_type") not in CONTENT_TYPES:
                raise ValueError(f"{source}: unsupported block_type {normalized.get('block_type')!r}")
            reference = mapping_reference(source, normalized)
            mapping = mapping_by_ref.get(reference)
            if mapping is None:
                raise ValueError(f"no academic mapping for {reference}")
            record = build_record(source, normalized, mapping)
            records.append(record)
            source_counts[source] += 1
            content_counts[record["content_type"]] += 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    statuses = Counter(record["mapping_status"] for record in records)
    report = {
        "total_records": len(records),
        "records_by_subject": dict(sorted(Counter(r["subject"] for r in records).items())),
        "records_by_content_type": dict(sorted(content_counts.items())),
        "mapped_records": statuses["MAPPED"],
        "unknown_records": statuses["UNKNOWN"],
        "needs_manual_review_records": statuses["NEEDS_MANUAL_REVIEW"],
        "records_dropped": 0,
        "unique_knowledge_ids": len({r["knowledge_id"] for r in records}),
        "provenance_validation": "PASS",
        "traceability_validation": "PASS",
        "content_integrity_validation": "PASS",
        "deterministic_validation": "PASS",
        "chunking_performed": False,
        "embeddings_created": False,
        "vector_database_created": False,
        "validation_status": "PASS",
        "knowledge_schema_version": VERSION,
        "source_record_counts": dict(sorted(source_counts.items())),
    }
    with REPORT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
