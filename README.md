# Studora AI

> An academic AI learning assistant for B.Tech students, built around syllabus-aligned Retrieval-Augmented Generation (RAG).

## What is Studora AI?

Studora AI is an academic AI assistant being developed specifically for B.Tech and undergraduate Computer Science students. Instead of building another generic chatbot, the project is being built to understand academic subjects, syllabus context, units, topics, follow-up doubts, exam preparation, practice questions, comparisons, and source provenance.

The project is being developed from scratch to explore how AI and RAG can support academic learning in a structured, syllabus-aware way.

## Target Users

B.Tech and undergraduate Computer Science students.

## Initial Subjects

- Python Programming
- Operating Systems
- Database Management Systems (DBMS)

The architecture is intended to expand to subjects such as C, Java, Data Structures and Algorithms (DSA), Computer Networks, Artificial Intelligence, Machine Learning, and other B.Tech subjects.

## Core Planned Features

These are planned product capabilities. They are not all implemented yet.

- Academic RAG Question Answering
- Exam Mode
- Follow-up / Doubt Chaining
- Topic-wise Practice Questions
- Compare X vs Y Mode
- Semester / Unit / Topic tagging

## Academic Sources and Provenance

The project prioritizes reliable academic sources, including:

- Official university syllabi and curricula
- NPTEL
- SWAYAM
- Official documentation
- Open educational resources
- Permitted institutional materials

Uncertain information should not be silently treated as verified. The research catalogue preserves institution, course, course code, semester, regulation or year, unit, original topic wording, source URL, source type, usage or license status, and provenance wherever available.

## Canonical Taxonomy

When multiple universities or resources cover the same concept, Studora AI should maintain one canonical concept while preserving each source's original wording and provenance.

For example:

```text
University A -> Normalization
University B -> Normalization
NPTEL -> Normalization

Canonical concept -> Normalization
```

University-specific wording, units, regulations, and source records remain separate. The project should not create university-specific duplicate canonical concepts.

## Planned RAG Architecture

```text
Student Question
        |
Intent / Mode Detection
        |
Metadata Filtering
        |
Academic Retrieval
        |
Conversation Context
        |
Prompt Construction
        |
LLM
        |
Grounded Answer
        |
Source / Provenance
```

## Current Development Status

### Phase 1 - Academic Research & Data Foundation

**STATUS: COMPLETED**

Current validated research snapshot:

- Institutions: 12
- Syllabus/course/unit/topic mapping records: 143
- Verified mappings: 139
- Manual-review mappings: 4
- Academic resources: 7
- Approved resources: 2
- Manual-review resources: 5
- Python canonical topics: 14
- OS canonical topics: 16
- DBMS canonical topics: 20
- Duplicate canonical topics: 0
- Duplicate IDs: 0
- Validation failures: 0

The count of 143 represents mapping records, not 143 separate syllabus documents. Multiple mappings can come from one source document. The JNTUH R25 source document is intentionally represented across its verified course, unit, and topic mappings.

## Verified JNTUH Evidence

The current verified JNTUH R25 CSE mappings include:

- `CS208ES` - Python Programming Lab
- `CS305PC` - DATABASE MANAGEMENT SYSTEMS
- `CS402PC` - Operating Systems

This does not mean that all JNTUH curriculum data is complete. Remaining curriculum and source-permission gaps are documented in `data/research/research_report.md`.

## Validation

Phase 1 included validation for:

- CSV structure and parsing
- UTF-8 encoding
- Duplicate IDs
- Duplicate canonical topics
- Status values
- Malformed URLs
- Resource licensing
- JNTUH metadata invariants
- Provenance-related data integrity

Current result: **0 validation failures**.

## What Has Not Been Built Yet

The following are not yet implemented:

- Document ingestion
- Text extraction
- Chunking
- Embeddings
- Vector database
- Retrieval pipeline
- RAG pipeline
- Conversation memory
- Exam Mode
- Compare Mode
- Topic-wise Practice
- Streamlit UI
- Evaluation
- Deployment

## Roadmap

- 🟢 Phase 1 - Academic Research & Data Foundation - Completed
- 🟡 Phase 2 - Approved Source Collection & Document Validation - Next
- ⬜ Phase 3 - Text Extraction & Chunking - Planned
- ⬜ Phase 4 - Embeddings & Vector Database - Planned
- ⬜ Phase 5 - Retrieval Layer - Planned
- ⬜ Phase 6 - Basic Academic RAG - Planned
- ⬜ Phase 7 - Conversation Context - Planned
- ⬜ Phase 8 - Exam Mode - Planned
- ⬜ Phase 9 - Compare Mode - Planned
- ⬜ Phase 10 - Topic-wise Practice - Planned
- ⬜ Phase 11 - Student UI - Planned
- ⬜ Phase 12 - Evaluation & Testing - Planned
- ⬜ Phase 13 - Deployment - Planned

## Project Structure

This is the current workspace structure. The research files are intentional project files; future implementation directories are not present yet.

```text
studora-ai/
├── .gitignore
├── README.md
├── PROJECT_STATUS.md
├── PROJECT_CONSTITUTION.md
└── data/
        ├── python/
        ├── os/
        ├── dbms/
        └── research/
                ├── dbms_topic_taxonomy.csv
                ├── duplicates.csv
                ├── os_topic_taxonomy.csv
                ├── python_topic_taxonomy.csv
                ├── research_report.md
                ├── resource_approval_matrix.csv
                ├── resource_sources.csv
                ├── syllabus_sources.csv
                └── universities.csv
```

`ingest/`, `app/`, `vectorstore/`, and `requirements.txt` will be added only when those implementation phases begin.

## Development Philosophy

```text
Research -> Data -> Retrieval -> RAG -> Features -> UI -> Evaluation -> Deployment
```

```text
Verify first -> Structure second -> Ingest third -> Retrieve fourth -> Generate last
```

## Current Milestone

Phase 1 is completed.

Next milestone: approved academic source collection and document validation.

**Studora AI is an actively developing project.**
