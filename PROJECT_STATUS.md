# Studora AI Project Status

## Project Aim

Studora AI is being developed as an academic AI learning assistant for B.Tech students. Its purpose is to support syllabus-aligned learning through a trustworthy Retrieval-Augmented Generation (RAG) architecture.

## Project Goal

The project will connect academic source research, curriculum metadata, retrieval, and grounded generation so students can understand concepts, clear follow-up doubts, prepare for exams, practice by topic, compare concepts, and filter learning by semester, unit, and topic.

The project is being built from scratch. Its current state is research and data foundation work, not a finished chatbot.

## Target Audience

B.Tech and undergraduate Computer Science students.

## Core Features

The permanent planned student-facing capabilities are:

1. Academic RAG-based question answering
2. Exam Mode
3. Follow-up / Doubt Chaining
4. Topic-wise Practice Questions
5. Compare X vs Y Mode
6. Semester / Unit / Topic tagging

These capabilities must remain grounded in verified academic sources and provenance metadata. They are not all implemented yet.

## Planned Architecture

```text
Student Question
  -> Intent / Mode Detection
  -> Metadata Filtering
  -> Academic Retrieval
  -> Conversation Context
  -> Prompt Construction
  -> LLM
  -> Grounded Answer
  -> Source / Provenance
```

The system is intentionally academic and syllabus-aware rather than a generic PDF chatbot. Initial subject collections remain logically separate for Python Programming, Operating Systems, and DBMS, with room for future B.Tech subjects.

## Academic Data Principles

The catalogue prioritizes official university syllabi and curricula, official course material, NPTEL, SWAYAM, official documentation, open educational resources, and permitted institutional materials.

Missing or uncertain information must remain explicitly unresolved. Institution, provider, course, code, semester, regulation or year, unit, topic, source URL, source type, usage or license status, and provenance should be preserved where available. University wording and curriculum differences must not be silently merged. Public accessibility does not by itself establish permission to redistribute a resource.

Canonical taxonomy concepts are deduplicated within subject while source-specific wording and provenance remain in the research catalogue.

## Phase 1 Completed Work

Phase 1 - Academic Research & Data Foundation is complete. The catalogue includes verified and manual-review institution records, syllabus/course/unit/topic mappings, academic resources, canonical taxonomies, resource approval rules, and research evidence documentation.

Verified JNTUH R25 CSE mappings include:

- `CS208ES` - Python Programming Lab
- `CS305PC` - DATABASE MANAGEMENT SYSTEMS
- `CS402PC` - Operating Systems

The JNTUH Python course remains represented as a lab. This catalogue does not claim that all JNTUH curriculum data is complete.

## Validation Results

Validation covered:

- Exact CSV headers
- UTF-8 encoding
- CSV parsing
- Missing and shifted fields
- Duplicate IDs
- Duplicate canonical topics within subject
- Status values
- Malformed URLs
- Approved-resource licensing
- JNTUH metadata invariants
- Shared source-document provenance

Current result: **0 validation failures**.

The syllabus catalogue uses mapping semantics: one source document may support many course, unit, and topic records.

## Current Research Counts

- Institutions: 12
- Verified institutions: 2
- Manual-review institutions: 10
- Syllabus/course/unit/topic mapping records: 143
- Verified mapping records: 139
- Manual-review mapping records: 4
- Academic resources: 7
- Approved resources: 2
- Manual-review resources: 5
- Rejected resources: 0
- Python canonical topics: 14
- OS canonical topics: 16
- DBMS canonical topics: 20
- Duplicate canonical topics: 0
- Duplicate IDs: 0
- Validation failures: 0

The 143 count represents mapping records, not independent syllabus documents. Multiple records can intentionally reference the same source URL.

## Current Milestone

Completed milestone: verified academic research and data foundation.

Next milestone: approved academic source collection and document validation. Collection must wait until unresolved source permissions and manual-review evidence are addressed.

## Completed vs Planned

Completed:

- Project constitution
- Research catalogue structure
- Evidence-based institution and resource records
- JNTUH R25 mapping records supplied and validated
- Canonical Python, OS, and DBMS taxonomies
- Research validation and provenance documentation

Planned or not yet implemented:

- Approved source collection
- Document and PDF validation
- Text extraction
- Chunking
- Metadata tagging during ingestion
- Embeddings
- Vector database
- Retrieval pipeline
- Basic academic RAG
- Conversation memory
- Exam Mode
- Compare Mode
- Topic-wise Practice
- Streamlit UI
- Evaluation and testing
- Deployment

## Full Development Roadmap

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

## Repository Readiness

`README.md` explains the project for students, recruiters, and developers. This file records the more detailed project state. Research CSV files under `data/research/` are intentional project files and remain trackable. Secrets and local/generated artifacts are excluded through `.gitignore`.

The project is not yet committed or pushed to GitHub.

**Studora AI is an actively developing project.**
