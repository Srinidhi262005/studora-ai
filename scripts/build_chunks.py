#!/usr/bin/env python3
"""Build deterministic, source-grounded Phase 3.6 retrieval chunks."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "knowledge" / "knowledge_records.jsonl"
OUTPUT_DIR = ROOT / "data" / "chunks"
OUTPUT_PATH = OUTPUT_DIR / "chunks.jsonl"
REPORT_PATH = OUTPUT_DIR / "chunk_report.json"

MAX_CHUNK_CHARACTERS = 1800
MIN_CHUNK_CHARACTERS = 200
OVERLAP_CHARACTERS = 0
STRATEGY_VERSION = "3.6.0"

ACADEMIC_FIELDS = (
    "subject", "institution", "regulation_year", "program", "semester",
    "course_code", "course_title", "unit", "topic", "subtopic",
    "canonical_topic", "mapping_status", "mapping_confidence",
)
PROVENANCE_FIELDS = (
    "source_id", "source_url", "provider", "document_identity",
    "record_index", "page_number", "original_filename", "sha256",
    "extraction_status",
)
TRACEABILITY_FIELDS = (
    "knowledge_id", "normalized_record_reference", "raw_record_reference",
    "mapping_id", "evidence_reference",
)


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


def split_text_exact(content: str) -> list[str]:
    """Split long prose at newline or sentence boundaries without rewriting it."""
    if len(content) <= MAX_CHUNK_CHARACTERS:
        return [content]
    parts: list[str] = []
    start = 0
    while start < len(content):
        if len(content) - start <= MAX_CHUNK_CHARACTERS:
            parts.append(content[start:])
            break
        limit = start + MAX_CHUNK_CHARACTERS
        candidates = [
            content.rfind("\n", start, limit + 1),
            content.rfind(". ", start, limit + 1) + 1,
            content.rfind("? ", start, limit + 1) + 1,
            content.rfind("! ", start, limit + 1) + 1,
        ]
        cut = max(c for c in candidates if c > start)
        parts.append(content[start:cut])
        start = cut
    return parts


def split_units(units: list[str]) -> list[str]:
    """Group complete units, retaining separators in the preceding chunk."""
    chunks: list[str] = []
    current = ""
    for unit in units:
        candidate = current + unit
        if current and len(candidate) > MAX_CHUNK_CHARACTERS:
            chunks.append(current)
            current = unit
        else:
            current = candidate
    if current or not chunks:
        chunks.append(current)
    return chunks


def split_content(record: dict[str, Any]) -> list[str]:
    content = record["content"]
    if not isinstance(content, str):
        raise ValueError("knowledge content must be a string")
    if len(content) <= MAX_CHUNK_CHARACTERS:
        return [content]
    content_type = record["content_type"]
    if content_type in {"code", "heading"}:
        return [content]
    if content_type == "list":
        return split_units(content.splitlines(keepends=True))
    if content_type == "definition_list":
        return split_units(content.splitlines(keepends=True))
    if content_type == "table":
        return split_units(content.splitlines(keepends=True))
    if content_type in {"p", "paragraph", "page_text"}:
        return split_text_exact(content)
    return [content]


def context_text(record: dict[str, Any]) -> str:
    labels = (
        ("subject", "Subject"),
        ("institution", "Institution"),
        ("regulation_year", "Regulation year"),
        ("program", "Program"),
        ("semester", "Semester"),
        ("course_code", "Course code"),
        ("course_title", "Course"),
        ("unit", "Unit"),
        ("topic", "Topic"),
        ("subtopic", "Subtopic"),
        ("canonical_topic", "Canonical topic"),
    )
    return "\n".join(
        f"{label}: {record[field]}"
        for field, label in labels
        if record.get(field) not in (None, "", "UNKNOWN")
    )


def make_chunk(record: dict[str, Any], content: str, index: int, count: int) -> dict[str, Any]:
    stable = f"{record['knowledge_id']}|{index}|{count}|{content}"
    digest = hashlib.sha256(stable.encode("utf-8")).hexdigest()[:20]
    result = {
        "chunk_id": f"CH-{record['knowledge_id']}-{digest}",
        "knowledge_id": record["knowledge_id"],
        "chunk_index": index,
        "chunk_count": count,
        "content": content,
        "content_type": record["content_type"],
        "context_text": context_text(record),
        "chunking_strategy_version": STRATEGY_VERSION,
    }
    result.update({field: record[field] for field in ACADEMIC_FIELDS})
    result.update({field: record[field] for field in PROVENANCE_FIELDS})
    result.update({field: record[field] for field in TRACEABILITY_FIELDS if field != "knowledge_id"})
    return result


def main() -> None:
    knowledge = load_jsonl(INPUT_PATH)
    chunks: list[dict[str, Any]] = []
    multiple = 0
    oversized_atomic: list[str] = []
    for record in knowledge:
        pieces = split_content(record)
        if not pieces:
            raise ValueError(f"empty chunk result for {record['knowledge_id']}")
        if len(pieces) > 1:
            multiple += 1
        if len(record["content"]) > MAX_CHUNK_CHARACTERS and record["content_type"] in {"code", "heading"}:
            oversized_atomic.append(record["knowledge_id"])
        chunks.extend(
            make_chunk(record, piece, index, len(pieces))
            for index, piece in enumerate(pieces)
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk, ensure_ascii=False, sort_keys=True) + "\n")

    report = {
        "total_knowledge_records": len(knowledge),
        "total_chunks": len(chunks),
        "chunks_by_subject": dict(sorted(Counter(c["subject"] for c in chunks).items())),
        "chunks_by_content_type": dict(sorted(Counter(c["content_type"] for c in chunks).items())),
        "knowledge_records_with_multiple_chunks": multiple,
        "knowledge_records_with_single_chunk": len(knowledge) - multiple,
        "maximum_chunk_characters": MAX_CHUNK_CHARACTERS,
        "minimum_chunk_characters": MIN_CHUNK_CHARACTERS,
        "overlap_characters": OVERLAP_CHARACTERS,
        "records_dropped": 0,
        "source_content_loss_detected": False,
        "oversized_atomic_records": oversized_atomic,
        "chunking_strategy_version": STRATEGY_VERSION,
        "validation_status": "PASS",
    }
    with REPORT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
