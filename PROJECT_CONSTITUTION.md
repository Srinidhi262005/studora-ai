# Studora AI — Project Constitution

## Project Identity
Project Name: Studora AI

Project Type: AI-powered academic learning assistant / Retrieval-Augmented Generation (RAG) chatbot for B.Tech students.

## Core Aim
Studora AI is designed to help B.Tech students understand academic subjects, clear doubts through conversational follow-ups, prepare for examinations, practice topic-specific questions, compare concepts, and navigate syllabus-aligned academic content using an AI-powered RAG architecture.

## Initial Subject Scope
Version 1:

- Python Programming
- Operating Systems
- Database Management Systems (DBMS)
The architecture must support future expansion to additional B.Tech subjects such as C, Java, Data Structures and Algorithms, Computer Networks, Artificial Intelligence, Machine Learning, and other academic subjects.

## Six Core Student Features
These are permanent core requirements:

1. Academic RAG-based question answering
2. Exam Mode
3. Follow-up / Doubt Chaining
4. Topic-wise Practice Questions
5. Compare X vs Y Mode
6. Semester / Unit / Topic Tagging

## Data Provenance and Verification
The knowledge base must prioritize trustworthy academic sources.

Preferred sources:

- Official university syllabi
- Official university curriculum documents
- Official university course material
- NPTEL
- SWAYAM
- Official documentation
- Open Educational Resources
- Institutionally published educational resources with permitted use
Do not ingest:

- Pirated textbooks
- Unauthorized copies of copyrighted textbooks
- Suspicious file-sharing sources
- Anonymous PDF repositories
- Unverified academic material
- Content whose provenance or usage permission is unclear
Every ingested document should retain provenance metadata wherever available.

Metadata should include:

- Institution
- Provider
- Subject
- Course
- Course code
- Semester
- Regulation / academic year
- Unit
- Topic
- Subtopic
- Source URL
- Source type
- License / usage status
- Document ID
- Page number

## No Fabrication Rule
Never invent institution names, URLs, course codes, semester information, regulations, units, topics, licenses, or source claims.

When information cannot be verified, explicitly mark it UNKNOWN or NEEDS_MANUAL_REVIEW.

Never silently infer missing academic metadata.

## Curriculum Principle
Different universities may organize and teach the same subject differently.

Therefore:

- Preserve original university wording.
- Preserve regulation/year differences.
- Preserve university-specific unit structures.
- Do not present a merged curriculum as an official syllabus.
- Maintain canonical topic mappings separately.
- Clearly distinguish official syllabus information from derived learning material.

## RAG Architecture
The project must remain an academic RAG system.

Core flow:

User Question
→ Intent / Mode Detection
→ Metadata Filtering
→ Retrieval
→ Conversation Context
→ Prompt Construction
→ LLM
→ Answer
→ Source / Provenance

## Follow-up / Conversation Context
The chatbot must understand follow-up questions.

Example:

User:
Explain normalization.

Assistant:
Explains normalization.

User:
What about 3NF?

Studora AI should understand that 3NF relates to the previous normalization discussion.

## Exam Mode
Exam Mode adapts responses for examination preparation.

Possible structure:

- Definition
- Key concepts
- Explanation
- Example
- Important exam points
- Advantages / disadvantages where applicable
- Short-answer preparation
- Long-answer preparation
Exam responses should remain grounded in retrieved academic material.

## Topic-wise Practice
Students can request practice by subject and topic.

Example:

DBMS → Normalization → 10 practice questions

Questions should be grounded in the relevant academic context whenever appropriate source material is available.

## Compare Mode
Students can compare two concepts.

Example:

Compare process vs thread.

Responses should clearly distinguish the two concepts and use retrieved academic sources where applicable.

## Semester / Unit / Topic Hierarchy
Academic content should support:

Subject
→ Semester
→ Unit
→ Topic
→ Subtopic

Example:

DBMS
→ Semester 3-1
→ Unit 2
→ Normalization
→ 3NF

## Data Storage
Initial subjects should remain logically separable:

- Python
- Operating Systems
- DBMS
The system must allow future subjects to be added without redesigning the entire architecture.

## Product Boundary
Do not reduce Studora AI to a generic PDF chatbot.

Do not remove the six core student features.

Do not replace the academic RAG architecture with an unrelated chatbot design.

Do not change the target audience from B.Tech students without explicit project-owner instruction.

## Development Order
The intended development order is:

1. Academic source research
2. Curriculum normalization
3. Data validation
4. Approved source collection
5. PDF/document validation
6. Text extraction
7. Chunking
8. Metadata tagging
9. Embeddings
10. Vector database
11. Retrieval
12. Basic RAG
13. Follow-up memory
14. Exam Mode
15. Compare Mode
16. Topic-wise Practice
17. Streamlit UI
18. Testing and evaluation
19. Deployment
Do not skip source validation simply to accelerate implementation.

## Project Governance
This file is the governing source of truth for Studora AI.

Before any major implementation task:

1. Read this file.
2. Preserve its requirements.
3. Do not silently alter the project's aim or scope.
4. Do not fabricate missing information.
If another implementation instruction conflicts with this file, follow this file unless the project owner explicitly changes it.

## Product Vision
Studora AI should feel like a reliable AI study companion for B.Tech students.

Understand concepts.
Clear doubts.
Prepare for exams.
Practice intelligently.
Compare concepts.
Navigate syllabus topics.
Learn from trustworthy academic sources.