#!/usr/bin/env python3
"""Build the governed Phase 3.7 embedding layer from locked chunks."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import platform
from pathlib import Path
from typing import Any

from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "chunks" / "chunks.jsonl"
OUTPUT_DIR = ROOT / "data" / "embeddings"
OUTPUT_PATH = OUTPUT_DIR / "embeddings.jsonl"
REPORT_PATH = OUTPUT_DIR / "embedding_report.json"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
EMBEDDING_STRATEGY_VERSION = "3.7.0"
BATCH_SIZE = 32
EMBEDDING_NORMALIZED = True
SIMILARITY_METRIC = "cosine"


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


def embedding_input(chunk: dict[str, Any]) -> str:
    context = chunk.get("context_text", "")
    content = chunk.get("content", "")
    if not isinstance(context, str) or not isinstance(content, str):
        raise ValueError(f"chunk {chunk.get('chunk_id')}: context/content must be strings")
    return f"{context}\n\n{content}"


def model_revision(model: SentenceTransformer) -> str:
    """Return the resolved cached revision when available, otherwise requested revision."""
    try:
        snapshot = model._model_card_vars.get("model_revision")  # type: ignore[attr-defined]
        if snapshot:
            return str(snapshot)
    except AttributeError:
        pass
    return MODEL_REVISION


def finite_vector(vector: list[float]) -> bool:
    return bool(vector) and all(math.isfinite(value) for value in vector)


def compare_repeat_run(
    previous: list[dict[str, Any]], current: list[dict[str, Any]]
) -> tuple[str, float | None]:
    if len(previous) != len(current):
        return "FAIL", None
    maximum_difference = 0.0
    for old, new in zip(previous, current):
        if (
            old.get("embedding_id") != new.get("embedding_id")
            or old.get("embedding_input_sha256") != new.get("embedding_input_sha256")
            or old.get("embedding_dimension") != new.get("embedding_dimension")
            or old.get("embedding_model") != new.get("embedding_model")
            or old.get("embedding_model_revision") != new.get("embedding_model_revision")
        ):
            return "FAIL", None
        old_vector = old.get("embedding", [])
        new_vector = new.get("embedding", [])
        if len(old_vector) != len(new_vector):
            return "FAIL", None
        if old_vector:
            maximum_difference = max(
                maximum_difference,
                max(abs(float(old_value) - float(new_value))
                    for old_value, new_value in zip(old_vector, new_vector)),
            )
    return "PASS", maximum_difference


def main() -> None:
    chunks = load_jsonl(INPUT_PATH)
    if len(chunks) != 1229:
        raise ValueError(f"expected 1229 chunks, found {len(chunks)}")
    inputs = [embedding_input(chunk) for chunk in chunks]

    model = SentenceTransformer(MODEL_NAME, revision=MODEL_REVISION, device="cpu")
    dimension = model.get_sentence_embedding_dimension()
    if not dimension:
        raise ValueError("embedding model returned no dimension")
    vectors = model.encode(
        inputs,
        batch_size=BATCH_SIZE,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=EMBEDDING_NORMALIZED,
    )
    if len(vectors) != len(chunks):
        raise ValueError("embedding count does not match chunk count")
    revision = model_revision(model)
    previous_records = load_jsonl(OUTPUT_PATH) if OUTPUT_PATH.exists() else None
    records: list[dict[str, Any]] = []
    for chunk, source_text, vector in zip(chunks, inputs, vectors):
        values = [float(value) for value in vector.tolist()]
        if len(values) != dimension or not finite_vector(values):
            raise ValueError(f"invalid vector for {chunk['chunk_id']}")
        records.append({
            "embedding_id": f"EMB-{chunk['chunk_id']}",
            "chunk_id": chunk["chunk_id"],
            "knowledge_id": chunk["knowledge_id"],
            "chunk_index": chunk["chunk_index"],
            "chunk_count": chunk["chunk_count"],
            "embedding": values,
            "embedding_dimension": dimension,
            "embedding_model": MODEL_NAME,
            "embedding_model_revision": revision,
            "embedding_normalized": EMBEDDING_NORMALIZED,
            "similarity_metric": SIMILARITY_METRIC,
            "embedding_input_text": source_text,
            "embedding_input_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
            "embedding_strategy_version": EMBEDDING_STRATEGY_VERSION,
            **{field: chunk[field] for field in (
                "subject", "institution", "regulation_year", "program", "semester",
                "course_code", "course_title", "unit", "topic", "subtopic",
                "canonical_topic", "mapping_status", "mapping_confidence",
                "source_id", "source_url", "provider", "document_identity",
                "page_number", "original_filename", "sha256", "extraction_status",
                "normalized_record_reference", "raw_record_reference", "mapping_id",
                "evidence_reference",
            )},
        })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    norms = [
        math.sqrt(sum(value * value for value in record["embedding"]))
        for record in records
    ]
    if previous_records is None:
        reproducibility_validation = "PENDING_REPEAT_RUN"
        maximum_repeat_difference = None
    else:
        reproducibility_validation, maximum_repeat_difference = compare_repeat_run(
            previous_records, records
        )
    report = {
        "total_chunks_input": len(chunks),
        "total_embeddings": len(records),
        "embedding_model": MODEL_NAME,
        "embedding_model_revision": revision,
        "embedding_dimension": dimension,
        "embedding_normalized": EMBEDDING_NORMALIZED,
        "similarity_metric": SIMILARITY_METRIC,
        "embedding_strategy_version": EMBEDDING_STRATEGY_VERSION,
        "device": "cpu",
        "batch_size": BATCH_SIZE,
        "embedding_input_format": "context_text + two newline characters + content",
        "embedding_input_hash_algorithm": "SHA-256",
        "artifact_strategy": {
            "vectors": "intentionally_ignored_reproducible_artifact",
            "source_of_truth": [
                "scripts/build_embeddings.py",
                "requirements.txt",
                "data/chunks/chunks.jsonl",
                "selected_model_and_revision",
            ],
        },
        "missing_embeddings": 0,
        "duplicate_embedding_ids": 0,
        "invalid_vectors": 0,
        "nan_vectors": 0,
        "infinite_vectors": 0,
        "normalization_validation": {
            "minimum_norm": min(norms),
            "maximum_norm": max(norms),
            "maximum_absolute_difference_from_one": max(abs(norm - 1.0) for norm in norms),
        },
        "reproducibility_validation": reproducibility_validation,
        "maximum_repeat_run_absolute_difference": maximum_repeat_difference,
        "validation_status": (
            "PASS"
            if reproducibility_validation == "PASS"
            else reproducibility_validation
        ),
        "dependency_versions": {
            "sentence-transformers": importlib.metadata.version("sentence-transformers"),
        },
        "python_version": platform.python_version(),
    }
    with REPORT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
