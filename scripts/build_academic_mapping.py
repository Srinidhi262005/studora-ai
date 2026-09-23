#!/usr/bin/env python3
"""Build the governed Phase 3.4 academic mapping layer.

Raw and normalized JSONL files are immutable inputs. This script creates one
mapping record for every normalized record, using only verified Phase 1
research evidence. Unsupported academic fields remain UNKNOWN.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
NORMALIZED_DIR = ROOT / "data" / "normalized"
RAW_DIR = ROOT / "data" / "extracted"
RESEARCH_DIR = ROOT / "data" / "research"
OUTPUT_DIR = ROOT / "data" / "mappings"
OUTPUT_PATH = OUTPUT_DIR / "academic_mapping.jsonl"
REPORT_PATH = OUTPUT_DIR / "mapping_report.json"
VERSION = "3.4.0"

SUBJECTS = {
    "Python Programming",
    "Operating Systems",
    "Database Management Systems",
}
ACADEMIC_FIELDS = (
    "institution",
    "regulation_year",
    "program",
    "semester",
    "subject",
    "course_code",
    "course_title",
    "unit",
    "topic",
    "subtopic",
    "canonical_topic",
)
JNTUH_SPANS = {
    (57, 58): {
        "subject": "Python Programming",
        "course_code": "CS208ES",
        "course_title": "Python Programming Lab",
        "semester": "I Year II Semester",
        "regulation_year": "R-25 Regulations",
        "evidence_ids": [f"JNTUH-R25-CS208ES-PY-{i:03d}" for i in range(1, 11)],
    },
    (73, 74): {
        "subject": "Database Management Systems",
        "course_code": "CS305PC",
        "course_title": "DATABASE MANAGEMENT SYSTEMS",
        "semester": "II Year I Semester",
        "regulation_year": "R-25 Regulations",
        "evidence_ids": [f"JNTUH-R25-CS305PC-DB-{i:03d}" for i in range(1, 34)],
    },
    (85, 86): {
        "subject": "Operating Systems",
        "course_code": "CS402PC",
        "course_title": "Operating Systems",
        "semester": "II Year II Semester",
        "regulation_year": "R-25 Regulations",
        "evidence_ids": [f"JNTUH-R25-CS402PC-OS-{i:03d}" for i in range(1, 25)],
    },
}


def read_csv(name: str) -> list[dict[str, str]]:
    with (RESEARCH_DIR / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                raise ValueError(f"{path}: blank line {line_number}")
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError(f"{path}: line {line_number} is not an object")
            records.append(record)
    return records


def span_metadata(record_index: int) -> dict[str, Any] | None:
    for (start, end), metadata in JNTUH_SPANS.items():
        if start <= record_index <= end:
            return metadata
    return None


def exact_heading_topic(record: dict[str, Any], taxonomies: list[dict[str, str]]) -> str:
    if record.get("block_type") != "heading":
        return "UNKNOWN"
    heading = record.get("extracted_text", "").strip()
    for row in taxonomies:
        if row["source_status"] == "VERIFIED" and heading in {
            row["canonical_topic"],
            row["canonical_subtopic"],
        }:
            return row["canonical_topic"]
    return "UNKNOWN"


def mapping_status(record: dict[str, Any], academic: dict[str, Any]) -> tuple[str, str]:
    if academic["course_code"] != "UNKNOWN" or academic["subject"] != "UNKNOWN":
        if academic["course_code"] != "UNKNOWN":
            return "MAPPED", "HIGH"
        return "MAPPED", "MEDIUM"
    if record["source_id"] == "UNKNOWN":
        return "NEEDS_MANUAL_REVIEW", "UNKNOWN"
    return "UNKNOWN", "UNKNOWN"


def make_mapping(
    source: str,
    record: dict[str, Any],
    raw: dict[str, Any],
    resource_by_id: dict[str, dict[str, str]],
    syllabus_by_id: dict[str, dict[str, str]],
    taxonomies: list[dict[str, str]],
) -> dict[str, Any]:
    identity = record.get("document_identity", "UNKNOWN")
    normalized_ref = (
        f"data/normalized/{source}_normalized.jsonl"
        f"#document_identity={identity}&record_index={record['record_index']}"
    )
    raw_ref = (
        f"data/extracted/{source}_raw.jsonl"
        f"#document_identity={identity}&record_index={raw['record_index']}"
    )
    academic = {field: "UNKNOWN" for field in ACADEMIC_FIELDS}
    source_id = record.get("source_id") or "UNKNOWN"
    evidence: list[str] = []
    notes = "No verified Phase 1 evidence supports academic metadata for this record."

    resource = resource_by_id.get(source_id) or resource_by_id.get(
        record.get("source_url", "")
    )
    if resource is not None:
        if resource["verification_status"] == "VERIFIED":
            academic["subject"] = resource["subject"]
            evidence.append(resource["resource_id"])
            notes = "Subject copied from verified Phase 1 resource_sources evidence."

    span = span_metadata(record["record_index"]) if source == "jntuh" else None
    if span is not None:
        academic.update(
            institution="Jawaharlal Nehru Technological University Hyderabad",
            regulation_year=span["regulation_year"],
            program="B.Tech. in Computer Science and Engineering",
            semester=span["semester"],
            subject=span["subject"],
            course_code=span["course_code"],
            course_title=span["course_title"],
        )
        evidence.extend(span["evidence_ids"])
        notes = "Course metadata copied from verified Phase 1 syllabus_sources evidence."

    academic["canonical_topic"] = exact_heading_topic(record, taxonomies)
    if academic["canonical_topic"] != "UNKNOWN":
        evidence.extend(
            row["topic_id"]
            for row in taxonomies
            if row["canonical_topic"] == academic["canonical_topic"]
        )

    status, confidence = mapping_status(record, academic)
    if status == "MAPPED" and academic["canonical_topic"] == "UNKNOWN":
        notes += " Topic-level mapping remains UNKNOWN because no exact taxonomy heading matched."
    return {
        "mapping_id": hashlib.sha256(normalized_ref.encode("utf-8")).hexdigest()[:20],
        "raw_record_reference": raw_ref,
        "normalized_record_reference": normalized_ref,
        "source_id": source_id,
        "source_url": record.get("source_url", "UNKNOWN"),
        "provider": record.get("provider", "UNKNOWN"),
        **academic,
        "mapping_confidence": confidence,
        "mapping_status": status,
        "evidence_reference": sorted(set(evidence)) or ["UNKNOWN"],
        "notes": notes,
    }


def main() -> None:
    resource_rows = read_csv("resource_sources.csv")
    syllabus_rows = read_csv("syllabus_sources.csv")
    manifest_rows = read_csv("collection_manifest.csv")
    taxonomies = (
        read_csv("python_topic_taxonomy.csv")
        + read_csv("os_topic_taxonomy.csv")
        + read_csv("dbms_topic_taxonomy.csv")
    )
    resource_by_id = {row["resource_id"]: row for row in resource_rows}
    resource_by_id.update({row["source_url"]: row for row in resource_rows})
    syllabus_by_id = {row["source_id"]: row for row in syllabus_rows}
    manifest_ids = {row["source_id"] for row in manifest_rows}
    if not all(row["source_status"] == "VERIFIED" for row in taxonomies):
        raise ValueError("All taxonomy rows used by the mapper must be VERIFIED")

    mappings: list[dict[str, Any]] = []
    source_counts: dict[str, int] = {}
    for source in ("python", "dbms", "jntuh"):
        normalized = load_jsonl(NORMALIZED_DIR / f"{source}_normalized.jsonl")
        raw = load_jsonl(RAW_DIR / f"{source}_raw.jsonl")
        if len(normalized) != len(raw):
            raise ValueError(f"{source}: normalized/raw record count mismatch")
        for normalized_record, raw_record in zip(normalized, raw):
            if normalized_record["record_index"] != raw_record["record_index"]:
                raise ValueError(f"{source}: record_index traceability mismatch")
            mapping = make_mapping(
                source,
                normalized_record,
                raw_record,
                resource_by_id,
                syllabus_by_id,
                taxonomies,
            )
            if mapping["source_id"] not in manifest_ids:
                raise ValueError(f"{source}: source_id missing from collection_manifest")
            if mapping["mapping_status"] == "MAPPED":
                if mapping["subject"] not in SUBJECTS:
                    raise ValueError("Mapped record outside Phase 3.4 subject scope")
                for evidence_id in mapping["evidence_reference"]:
                    if evidence_id.startswith("JNTUH-") and evidence_id not in syllabus_by_id:
                        raise ValueError(f"Missing syllabus evidence {evidence_id}")
            mappings.append(mapping)
        source_counts[source] = len(normalized)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        for mapping in mappings:
            handle.write(json.dumps(mapping, ensure_ascii=False, sort_keys=True) + "\n")

    status_counts = {}
    for mapping in mappings:
        status_counts[mapping["mapping_status"]] = (
            status_counts.get(mapping["mapping_status"], 0) + 1
        )
    report = {
        "mapping_version": VERSION,
        "total_records_considered": len(mappings),
        "mapped_records": status_counts.get("MAPPED", 0),
        "unknown_records": status_counts.get("UNKNOWN", 0),
        "needs_manual_review_records": status_counts.get("NEEDS_MANUAL_REVIEW", 0),
        "mapping_status_counts": status_counts,
        "subjects_represented": sorted(
            {m["subject"] for m in mappings if m["subject"] != "UNKNOWN"}
        ),
        "institutions_represented": sorted(
            {m["institution"] for m in mappings if m["institution"] != "UNKNOWN"}
        ),
        "source_record_counts": source_counts,
        "records_dropped": 0,
        "validation_warnings": [],
        "errors": [],
    }
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
