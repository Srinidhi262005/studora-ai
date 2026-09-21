#!/usr/bin/env python3
"""
Studora AI — Phase 3.2 raw source extraction (manifest-driven).

Reads data/research/collection_manifest.csv and writes:
  data/extracted/python_raw.jsonl
  data/extracted/dbms_raw.jsonl
  data/extracted/jntuh_raw.jsonl
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import pdfplumber
from bs4 import BeautifulSoup, Comment, NavigableString, Tag

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "research" / "collection_manifest.csv"
OUTPUT_DIR = ROOT / "data" / "extracted"



HTML_REQUIRED = (
    "source_url",
    "local_path",
    "original_filename",
    "document_identity",
    "provider",
    "source_type",
    "sha256",
    "extraction_timestamp",
    "section_path",
    "block_type",
    "extracted_text",
    "extraction_status",
)

PDF_REQUIRED = (
    "source_url",
    "local_path",
    "original_filename",
    "document_identity",
    "provider",
    "source_type",
    "sha256",
    "extraction_timestamp",
    "page_number",
    "block_type",
    "extracted_text",
    "extraction_status",
)

BLOCK_TAGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6", "p", "pre", "table", "ul", "ol", "dl"})

SKIP_ANCESTOR: tuple[str, ...] = (
    "script",
    "style",
    "nav",
    "footer",
    "form",
    "header",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_manifest() -> list[dict[str, str]]:
    with MANIFEST_PATH.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def output_family(local_path: str) -> str:
    normalized = local_path.replace("/", "\\").lower()
    if normalized.startswith("data\\python\\"):
        return "python"
    if normalized.startswith("data\\dbms\\"):
        return "dbms"
    if "jntuh" in normalized and normalized.endswith(".pdf"):
        return "jntuh"
    raise ValueError(f"Unrecognized manifest local_path: {local_path}")



def has_skip_ancestor(tag: Tag) -> bool:
    for parent in tag.parents:
        if not isinstance(parent, Tag):
            continue
        if parent.name in SKIP_ANCESTOR:
            return True
        classes = parent.get("class") or []
        parent_id = parent.get("id") or ""
        if "navheader" in classes or "navfooter" in classes:
            return True
        if parent_id == "docComments":
            return True
        if "sphinxsidebar" in classes or "related" in classes:
            return True
        if "navbar" in classes:
            return True
        if parent.name == "form" and parent.get("role") == "search":
            return True
    return False


def is_toc_div(tag: Tag) -> bool:
    return tag.name == "div" and "toc" in (tag.get("class") or [])


def heading_level(tag: Tag) -> int:
    if tag.name in BLOCK_TAGS and tag.name.startswith("h") and len(tag.name) == 2:
        return int(tag.name[1])
    return 0


def text_from_tag(tag: Tag) -> str:
    return tag.get_text("\n", strip=False).strip("\n")


def table_to_grid(table: Tag) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in table.find_all("tr", recursive=True):
        cells = tr.find_all(["th", "td"], recursive=False)
        if not cells:
            continue
        rows.append([text_from_tag(c) for c in cells])
    return rows


def list_items(tag: Tag) -> list[str]:
    items: list[str] = []
    for li in tag.find_all("li", recursive=False):
        items.append(text_from_tag(li))
    return items


def definition_pairs(tag: Tag) -> list[dict[str, str]]:
    pairs: list[dict[str, str]] = []
    for dt in tag.find_all("dt", recursive=False):
        dd = dt.find_next_sibling("dd")
        term = text_from_tag(dt)
        definition = text_from_tag(dd) if isinstance(dd, Tag) else ""
        pairs.append({"term": term, "definition": definition})
    return pairs


def find_html_content_root(soup: BeautifulSoup, local_path: str) -> Tag | None:
    if "data\\python\\" in local_path.replace("/", "\\") or local_path.replace("\\", "/").startswith(
        "data/python/"
    ):
        return soup.find("div", class_="body", attrs={"role": "main"}) or soup.find("div", class_="body")
    doc = soup.find("div", id="docContent")
    return doc


def walk_html_blocks(content: Tag) -> Iterator[tuple[str, Tag]]:
    """Depth-first document order; emit block elements without descending into them."""

    def walk(node: Tag) -> Iterator[tuple[str, Tag]]:
        for child in node.children:
            if isinstance(child, Comment):
                continue
            if isinstance(child, NavigableString):
                continue
            if not isinstance(child, Tag):
                continue
            if has_skip_ancestor(child):
                continue
            if is_toc_div(child):
                yield ("toc", child)
                continue
            if child.name in BLOCK_TAGS:
                yield (child.name, child)
                continue
            if child.name == "div" and "highlight" in (child.get("class") or []):
                pre = child.find("pre")
                if pre is not None:
                    yield ("pre", pre)
                else:
                    yield from walk(child)
                continue
            yield from walk(child)

    yield from walk(content)


def extract_html_records(
    path: Path,
    manifest_row: dict[str, str],
    sha256: str,
    extraction_timestamp: str,
) -> list[dict[str, Any]]:
    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    local_path = manifest_row["local_path"]
    content = find_html_content_root(soup, local_path)
    if content is None:
        raise RuntimeError("Primary content area not found")

    records: list[dict[str, Any]] = []
    section_stack: list[str] = []
    record_index = 0

    base = {
        "source_url": manifest_row["source_url"],
        "local_path": manifest_row["local_path"],
        "original_filename": manifest_row["original_filename"],
        "document_identity": manifest_row["document_identity"],
        "provider": manifest_row["provider"],
        "source_type": manifest_row["source_type"],
        "source_id": manifest_row.get("source_id", ""),
        "sha256": sha256,
        "extraction_timestamp": extraction_timestamp,
    }

    for kind, tag in walk_html_blocks(content):
        block_type = kind
        extracted_text = ""
        table_data: list[list[str]] | None = None
        definition_pairs_data: list[dict[str, str]] | None = None
        list_data: list[str] | None = None
        h_level = 0

        if kind in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            block_type = "heading"
            extracted_text = text_from_tag(tag)
            h_level = heading_level(tag)
            while section_stack and len(section_stack) >= h_level:
                section_stack.pop()
            while len(section_stack) < h_level - 1:
                section_stack.append("")
            if h_level > 0:
                if len(section_stack) == h_level - 1:
                    section_stack.append(extracted_text)
                else:
                    section_stack[h_level - 1] = extracted_text
        elif kind == "pre":
            block_type = "code"
            extracted_text = text_from_tag(tag)
        elif kind == "p":
            extracted_text = text_from_tag(tag)
            if not extracted_text.strip():
                continue
        elif kind == "table":
            table_data = table_to_grid(tag)
            if not table_data:
                continue
        elif kind in {"ul", "ol"}:
            block_type = "list"
            list_data = list_items(tag)
            if not list_data:
                continue
            extracted_text = "\n".join(list_data)
        elif kind == "dl":
            block_type = "definition_list"
            definition_pairs_data = definition_pairs(tag)
            if not definition_pairs_data:
                continue
        elif kind == "toc":
            inner_dl = tag.find("dl")
            if inner_dl is None:
                continue
            block_type = "definition_list"
            definition_pairs_data = definition_pairs(inner_dl)
            if not definition_pairs_data:
                continue

        record: dict[str, Any] = {
            **base,
            "record_index": record_index,
            "section_path": [s for s in section_stack if s],
            "heading_level": h_level,
            "block_type": block_type,
            "extracted_text": extracted_text,
            "extraction_status": "OK",
        }
        if table_data is not None:
            record["table_data"] = table_data
        if definition_pairs_data is not None:
            record["definition_pairs"] = definition_pairs_data
        if list_data is not None:
            record["list_items"] = list_data

        records.append(record)
        record_index += 1

    return records


def extract_pdf_records(
    path: Path,
    manifest_row: dict[str, str],
    sha256: str,
    extraction_timestamp: str,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    record_index = 0
    base = {
        "source_url": manifest_row["source_url"],
        "local_path": manifest_row["local_path"],
        "original_filename": manifest_row["original_filename"],
        "document_identity": manifest_row["document_identity"],
        "provider": manifest_row["provider"],
        "source_type": manifest_row["source_type"],
        "source_id": manifest_row.get("source_id", ""),
        "sha256": sha256,
        "extraction_timestamp": extraction_timestamp,
    }

    with pdfplumber.open(path) as pdf:
        total_pages = len(pdf.pages)
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                rec = {
                    **base,
                    "record_index": record_index,
                    "page_number": page_num,
                    "total_pages": total_pages,
                    "block_type": "page_text",
                    "extracted_text": text,
        
                    "extraction_status": "OK",
                }
                records.append(rec)
                record_index += 1

            tables = page.extract_tables() or []
            for table_index, raw_table in enumerate(tables):
                table_data = [[(cell or "").strip() for cell in row] for row in raw_table if row]
                if not table_data:
                    continue
                rec = {
                    **base,
                    "record_index": record_index,
                    "page_number": page_num,
                    "total_pages": total_pages,
                    "block_type": "table",
                    "extracted_text": "",
                    "table_data": table_data,
                    "table_index_on_page": table_index,

                    "extraction_status": "OK",
                }
                records.append(rec)
                record_index += 1

    return records


def validate_record(record: dict[str, Any], is_pdf: bool) -> list[str]:
    errors: list[str] = []
    required = PDF_REQUIRED if is_pdf else HTML_REQUIRED
    for key in required:
        if key not in record:
            errors.append(f"missing {key}")
    return errors


def is_toc_landing_html(records: list[dict[str, Any]]) -> bool:
    """Heuristic: chapter landing page whose body is mostly TOC."""
    if not records:
        return False
    has_toc_heading = any(
        r.get("block_type") == "paragraph" and r.get("extracted_text", "").strip() == "Table of Contents"
        for r in records
    )
    has_def_list = any(r.get("block_type") == "definition_list" for r in records)
    non_nav_blocks = [
        r
        for r in records
        if r.get("block_type") not in {"heading", "paragraph", "definition_list", "table"}
        or (r.get("block_type") == "paragraph" and r.get("extracted_text", "").strip() != "Table of Contents")
    ]
    thin_body = len(non_nav_blocks) == 0
    return has_toc_heading and has_def_list and thin_body


def run_extraction() -> dict[str, Any]:
    extraction_timestamp = utc_now_iso()
    manifest = load_manifest()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    buckets: dict[str, list[dict[str, Any]]] = {"python": [], "dbms": [], "jntuh": []}
    source_stats: list[dict[str, Any]] = []
    sha_failures: list[str] = []
    provenance_failures: list[str] = []

    families_expected = {"python": 12, "dbms": 13, "jntuh": 1}
    families_processed = {"python": 0, "dbms": 0, "jntuh": 0}
    families_failed = {"python": 0, "dbms": 0, "jntuh": 0}

    for row in manifest:
        family = output_family(row["local_path"])
        path = ROOT / row["local_path"]
        stat: dict[str, Any] = {
            "original_filename": row["original_filename"],
            "family": family,
            "sha256_match": False,
            "extraction_status": "FAILED",
            "record_count": 0,
            "error": None,
        }

        if not path.is_file():
            stat["error"] = "file missing"
            families_failed[family] += 1
            source_stats.append(stat)
            continue

        expected = row["sha256"].upper()
        actual = sha256_file(path)
        if actual != expected:
            stat["error"] = f"sha256 mismatch expected={expected} actual={actual}"
            sha_failures.append(row["original_filename"])
            families_failed[family] += 1
            source_stats.append(stat)
            continue

        stat["sha256_match"] = True

        try:
            if family == "jntuh":
                records = extract_pdf_records(path, row, actual, extraction_timestamp)
            else:
                records = extract_html_records(path, row, actual, extraction_timestamp)

            is_pdf = family == "jntuh"
            for rec in records:
                errs = validate_record(rec, is_pdf)
                if errs:
                    provenance_failures.append(f"{row['original_filename']}: {', '.join(errs)}")

            buckets[family].extend(records)
            stat["extraction_status"] = "OK"
            stat["record_count"] = len(records)
            stat["toc_landing"] = is_toc_landing_html(records) if family == "dbms" else False
            families_processed[family] += 1
        except Exception as exc:  # noqa: BLE001 — report and continue other sources
            stat["error"] = str(exc)
            families_failed[family] += 1
            fail_rec = {
                "source_url": row["source_url"],
                "local_path": row["local_path"],
                "original_filename": row["original_filename"],
                "document_identity": row["document_identity"],
                "provider": row["provider"],
                "source_type": row["source_type"],
                "source_id": row["source_id"],
                "sha256": actual,
                "extraction_timestamp": extraction_timestamp,
                "extraction_status": "FAILED",
                "error": str(exc),
            }
            if family == "jntuh":
                fail_rec["page_number"] = 0
                fail_rec["block_type"] = "error"
                fail_rec["extracted_text"] = ""
            else:
                fail_rec["section_path"] = []
                fail_rec["block_type"] = "error"
                fail_rec["extracted_text"] = ""
            buckets[family].append(fail_rec)

        source_stats.append(stat)

    outputs = {
        "python": OUTPUT_DIR / "python_raw.jsonl",
        "dbms": OUTPUT_DIR / "dbms_raw.jsonl",
        "jntuh": OUTPUT_DIR / "jntuh_raw.jsonl",
    }
    for family, out_path in outputs.items():
        with out_path.open("w", encoding="utf-8", newline="\n") as fh:
            for rec in buckets[family]:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    validation = validate_outputs(manifest, outputs, source_stats)

    return {
        "extraction_timestamp": extraction_timestamp,
        "source_stats": source_stats,
        "sha_failures": sha_failures,
        "provenance_failures": provenance_failures,
        "families_expected": families_expected,
        "families_processed": families_processed,
        "families_failed": families_failed,
        "validation": validation,
        "output_counts": {k: len(buckets[k]) for k in buckets},
    }


def validate_outputs(
    manifest: list[dict[str, str]],
    outputs: dict[str, Path],
    source_stats: list[dict[str, Any]],
) -> dict[str, Any]:
    allowed_paths = {row["local_path"] for row in manifest}
    allowed_filenames = {row["original_filename"] for row in manifest}
    result: dict[str, Any] = {
        "valid_jsonl": True,
        "malformed_lines": [],
        "missing_provenance": [],
        "unlisted_sources": [],
        "jntuh_pages": set(),
    }

    for family, path in outputs.items():
        if not path.is_file():
            result["valid_jsonl"] = False
            result["malformed_lines"].append(f"{path.name}: missing")
            continue
        with path.open(encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, start=1):
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError as err:
                    result["valid_jsonl"] = False
                    result["malformed_lines"].append(f"{path.name}:{line_no}: {err}")
                    continue
                lp = rec.get("local_path")
                fn = rec.get("original_filename")
                if lp not in allowed_paths and fn not in allowed_filenames:
                    result["unlisted_sources"].append(f"{path.name}:{line_no}")
                missing = [k for k in (PDF_REQUIRED if family == "jntuh" else HTML_REQUIRED) if k not in rec]
                if missing:
                    result["missing_provenance"].append(f"{path.name}:{line_no}: {missing}")
                if family == "jntuh" and rec.get("extraction_status") == "OK":
                    if "page_number" in rec:
                        result["jntuh_pages"].add(rec["page_number"])

    result["jntuh_page_count"] = len(result["jntuh_pages"])
    result["toc_landings"] = [s["original_filename"] for s in source_stats if s.get("toc_landing")]
    return result


def main() -> int:
    summary = run_extraction()
    print(json.dumps(summary, indent=2, default=str))
    if summary["sha_failures"] or summary["provenance_failures"]:
        return 1
    if any(summary["families_failed"].values()):
        return 1
    if not summary["validation"]["valid_jsonl"]:
        return 1
    if summary["validation"]["missing_provenance"] or summary["validation"]["unlisted_sources"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
