# Studora AI Academic Source Research Report

## Phase and scope

Final research data-entry pass using supplied verified evidence. No new web research was performed. No PDF was downloaded, scraped, ingested, embedded, or added to a vector database.

The initial subjects are Python Programming, Operating Systems, and Database Management Systems (DBMS). Telangana was researched first, followed by a limited national coverage pass. This is curriculum coverage research, not a ranking or best-institution list.

## Research methodology

1. Read `PROJECT_CONSTITUTION.md` before research.
2. Open the institution or provider page directly.
3. Confirm that the page belongs to the claimed institution/provider.
4. Record only names, URLs, topics, and licensing statements visible in the opened source.
5. Preserve university-specific wording and do not infer course codes, semesters, regulations, units, or syllabus topics.
6. Use `NEEDS_MANUAL_REVIEW` whenever a CSE curriculum, license, or metadata claim remains unresolved.
7. Keep resource evidence separate from university syllabus evidence.

## Institutions researched

JNTUH, IIT Hyderabad, IIIT Hyderabad, NIT Warangal, University of Hyderabad, Osmania University, IIT Bombay, IIT Delhi, IIT Madras, IIT Kanpur, IIT Kharagpur, and IISc. Existing official-page research plus supplied course evidence was used; no new web research was performed in this pass.

## Institutions verified

JNTUH and IIT Madras have directly evidenced official Computer Science and Engineering department URLs. JNTUH now also has supplied direct R25 course evidence recorded in `syllabus_sources.csv`. This does not make the IIT Madras curriculum verified.

## Institutions requiring manual review

IIT Hyderabad, IIIT Hyderabad, NIT Warangal, University of Hyderabad, Osmania University, IIT Bombay, IIT Delhi, IIT Kanpur, IIT Kharagpur, and IISc require official URL and/or detailed curriculum review. JNTUH still requires regulation applicability and document audit beyond the supplied R25 evidence. No course document was downloaded.

## JNTUH Deep Verification

### Supplied direct course evidence

The supplied official source is [R25B.Tech.CSEIIIYearSyllabusV2.pdf](https://www.jntuh.ac.in/uploads/academics/R25B.Tech.CSEIIIYearSyllabusV2.pdf), titled `B.Tech. in Computer Science and Engineering - Course Structure & Syllabus - R-25 Regulations`, applicable from `AY 2025-2026 Batch`. It directly supports `CS208ES Python Programming Lab` in `I Year II Sem.`, `CS305PC Database Management Systems` in `II Year I Sem.`, and `CS402PC Operating Systems` in `II Year II Sem.` with the supplied Unit I through Unit V topic wording. The Python course is preserved as a lab and is not renamed to a theory course.

### Official pages discovered

| Official URL | Page type | What it proves | What it does not prove |
|---|---|---|---|
| https://jntuh.ac.in/ | JNTUH institutional homepage | Identifies JNTUH, its Telangana location, B.Tech offering, and official academic navigation. | It does not prove any specific CSE course, code, semester, regulation, unit, or topic. |
| https://jntuh.ac.in/content/programs-offered/127/a92c063baa09fa0ab9649ea103144422 | Programs navigation | JNTUH exposes UG Programs and the official UG program listing. | It does not itself provide course-level syllabus details. |
| https://jntuh.ac.in/content/ug-programs/99/42c96486a633f20842b3b37289e8214a | UG program listing | The official listing includes `B.Tech-CSE` and separately lists specialized branches such as CSE (Data Science), CSE (Networks), and CSE (IoT). | It does not provide the CSE course structure or detailed subject syllabus. Specialized branches cannot be treated as plain CSE evidence. |
| https://jntuh.ac.in/content/departments---centres/128/b263df2f013183974fc74734a4ea8692 | Departments/Centres navigation | The official JNTUH page links Computer Science and Engineering to the JNTUH University College of Engineering CSE page. | It does not prove the course metadata for Python, Operating Systems, or DBMS. |
| https://jntuhceh.ac.in/viewdept/5 | Official constituent-college CSE department page | The page identifies the Department of Computer Science and Engineering and exposes Courses and Syllabus links. | The opened page says the site is being updated and does not expose the target CSE R25 course structure or detailed syllabus content. |
| https://jntuhceh.ac.in/syllabus/5/dept | CSE department syllabus endpoint | This is the exact syllabus link exposed by the official CSE department page. | Its course-level contents were not established in this pass; no PDF was downloaded. |
| https://jntuh.ac.in/syllabus | Central syllabus listing | JNTUH publishes a central syllabus listing and links the official Student Services syllabus repository. The visible listing includes R25 entries for CSE (Networks) and CSE (IoT and Cyber Security Including Blockchain Technology). | It does not show a plain B.Tech CSE R25 entry in the opened listing and does not prove any target-subject course tuple. |
| https://studentservices.jntuh.ac.in/oss/syllabus.html?type=syllabus | Student Services syllabus navigation | The official repository exposes B.Tech, among other levels. | It does not provide the target course details on the opened navigation page. |
| https://studentservices.jntuh.ac.in/oss/syllabus_action.html?level=1.B.Tech&l123=0&type=syllabus | B.Tech syllabus repository | The opened page exposes regulation navigation: R22, R18, R16, R15, R13, R09, R07, R05, NR, OR, OOR, and RR. | It does not expose a plain CSE course structure or detailed Python/OS/DBMS syllabus in the opened HTML. |
| https://jntuh.ac.in/rules-and-regulations | Academic regulations listing | The official listing contains `R25 B.Tech. Academic Regulations` dated 11 Aug 2025 and a draft-feedback entry dated 31 Jul 2025. | The listing alone does not prove the contents, applicability to plain CSE, or any course metadata. |
| https://jntuh.ac.in/academic-downloads | Academic downloads listing | The page exposes official academic-download records and academic years. | It does not provide the target CSE course structure or detailed subject syllabus. |

### R25 evidence levels

| Evidence level | Result | Evidence boundary |
|---|---|---|
| A. R25 exists on JNTUH | VERIFIED | The official academic regulations listing includes R25 entries. |
| B. R25 B.Tech exists | VERIFIED | The official listing includes `R25 B.Tech. Academic Regulations` dated 11 Aug 2025. |
| C. R25 B.Tech CSE exists | NOT VERIFIED | The visible R25 syllabus entries are for specialized branches including CSE (Networks) and CSE (IoT and Cyber Security Including Blockchain Technology), not plain CSE. |
| D. R25 B.Tech CSE course structure exists | NOT VERIFIED | The opened HTML did not expose a plain CSE R25 course structure. |
| E. R25 B.Tech CSE detailed syllabus exists | NOT VERIFIED | The opened HTML did not expose plain CSE R25 detailed syllabus content; no PDF was downloaded. |

### CSE evidence

Plain `B.Tech-CSE` is directly listed by the official UG Programs page, and the official JNTUH navigation links a CSE department page. The university identity and official CSE department URL are therefore verified in `universities.csv`. A verified CSE curriculum is not claimed.

### Regulation evidence

R25 B.Tech Academic Regulations are listed by JNTUH. The B.Tech Student Services repository also exposes older regulation navigation labels. The applicable regulation for the target plain B.Tech CSE subject records remains unresolved.

### Python evidence

Supplied official JNTUH R25 evidence directly supports `Python Programming Lab`, course code `CS208ES`, and semester `I Year II Sem.` The source identifies the course as a lab with L-T-P `0-0-2` and 1 credit. Supported original topic wording is recorded in `syllabus_sources.csv`; this is not represented as a Python theory course.

### Operating Systems evidence

Supplied official JNTUH R25 evidence directly supports `Operating Systems`, course code `CS402PC`, and semester `II Year II Sem.` The source identifies L-T-P `3-0-0` and 3 credits. Unit I through Unit V topic wording supplied for the course is recorded in `syllabus_sources.csv`.

### DBMS evidence

Supplied official JNTUH R25 evidence directly supports `Database Management Systems`, course code `CS305PC`, and semester `II Year I Sem.` The source identifies L-T-P `3-0-0` and 3 credits. Unit I through Unit V topic wording supplied for the course is recorded in `syllabus_sources.csv`.

### Verified fields and unresolved fields

Verified fields: institution identity, official JNTUH domain, official CSE department URL, existence of a plain `B.Tech-CSE` program listing, existence of an R25 B.Tech academic-regulations listing, the supplied R25 source URL, JNTUH course names, course codes, semesters, regulation, units, and supplied topics for the three target subjects.

Unresolved fields: independent local audit of the supplied source document, explicit JNTUH source-page confirmation of AY applicability beyond the supplied evidence, course-level details for NITW/IIITH/Osmania, and detailed licensing/reuse terms for NPTEL candidates.

### Reason for manual review

The supplied source evidence supports the JNTUH course-level rows, but the document itself has not been downloaded or locally audited in this phase. Manual review remains appropriate before collection, especially for document integrity and any metadata not present in the supplied evidence.

## Syllabus records

JNTUH R25 course and topic rows were added from the supplied official source evidence. NITW, IIITH, and Osmania rows remain `NEEDS_MANUAL_REVIEW` where detailed URLs or mappings were not supplied. No course metadata was inferred.

`syllabus_sources.csv` currently represents verified syllabus/course/unit/topic mappings. Multiple rows may originate from the same source document. The 143 records are syllabus/course/unit/topic mapping records, not 143 separate syllabus documents. The 139 `VERIFIED` records are verified mapping records, not independent syllabus documents.

## Institution records

The catalogue lists 12 institutions: 2 verified institution records and 10 manual-review records. Institution verification is separate from course and curriculum verification.

## Canonical taxonomy

The taxonomy contains 14 Python, 16 OS, and 20 DBMS canonical concepts after subject-scoped, case-insensitive, trimmed-name deduplication. `source_status` is status-only and uses the allowed values `VERIFIED`, `NEEDS_MANUAL_REVIEW`, or `UNKNOWN`. Source provenance remains in the syllabus/resource catalogues and report evidence; canonical topics are not university-specific duplicates.

## Source provenance

One official source document may support many course/unit/topic mapping records. Accordingly, the JNTUH R25 source URL intentionally appears on 139 mapping rows and is not deduplicated out of `syllabus_sources.csv`. `source_id` remains the unique identifier for each mapping record.

## Python course and topic coverage

Resource evidence only: `RES-PY-001` is the official Python Tutorial. The taxonomy records interpreter use, data types, control flow, functions, data structures, modules/packages, input/output, exceptions, classes, iterators/generators, comprehensions, string pattern matching, standard-library areas, and virtual environments/packages. These are not claims about any university syllabus.

## OS course and topic coverage

Resource evidence only: `RES-OS-001` is the author-hosted Operating Systems: Three Easy Pieces page. The taxonomy records virtualization, processes, CPU scheduling, memory management, threads, synchronization, file systems, storage/I/O, concurrency, persistence, and security. Its reuse permission remains unresolved.

## DBMS course and topic coverage

Resource evidence only: `RES-DB-001` is the official PostgreSQL documentation. The taxonomy records SQL, data definition/manipulation, data types, functions/operators, indexes, concurrency control, query processing, and backup/restore. These are not claims about any university syllabus.

## Common and institution-specific topics

Common university topics cannot yet be established because no university syllabus tuple was verified. Institution-specific wording and regulation-specific differences are therefore not yet available. No merged curriculum has been created.

## Resource providers and status

Resources researched: Python Software Foundation documentation, University of Wisconsin-hosted OSTEP material, PostgreSQL Global Development Group documentation, NPTEL course candidates from Chennai Mathematical Institute, IIT Kharagpur, and IIT Madras.

Approved resources: Python Tutorial and PostgreSQL Documentation.

Resources requiring review: Operating Systems: Three Easy Pieces and all four NPTEL candidates, because reuse/redistribution terms were not established. Public accessibility is not treated as redistribution permission.

Rejected resources: none found in this pass.

## Quality-control results

- Duplicate source IDs: none in the populated resource records or syllabus records.
- Duplicate canonical topics: none after merging the two Standard library rows into one canonical topic.
- Duplicate URLs: the JNTUH R25 syllabus URL is intentionally shared by 139 topic mappings from one source document; no conflicting source URL was found.
- Duplicate university records: none.
- Malformed URLs: none observed in populated URL fields.
- Empty critical fields: unresolved institution URLs and unsupported NITW/IIITH course metadata are explicitly `UNKNOWN` and those records are marked `NEEDS_MANUAL_REVIEW`.
- Unsupported license claims: none; unresolved resource licensing is `UNKNOWN`.
- Unsupported course codes, topics, or regulation claims: none added.
- Conflicting regulation/year information: none observed.

## Missing information and limitations

The supplied evidence establishes JNTUH R-25 course metadata for the three target subjects, but local document verification remains pending because no PDF was downloaded. NITW and IIITH evidence is course-level only, with detailed URLs and mappings unresolved. Osmania evidence confirms the B.E. CSE III & IV Semester syllabus effective Academic Year 2025-26, but not subjects or topics. NPTEL candidates are verified candidates with unknown reuse licensing; no NPTEL/SWAYAM resource is approved for redistribution.

## Research Evidence Gaps

### JNTUH Python

- What we need: the official plain B.Tech CSE course structure and the exact Python-related course name, course code, semester, regulation, unit, and topics.
- Source found: the official JNTUH syllabus page and the official Student Services B.Tech syllabus repository.
- What was verified: supplied evidence directly supports `Python Programming Lab`, `CS208ES`, `I Year II Sem.`, R-25 Regulations, and the supplied topic list. The source identifies the course as a lab, not a theory course.
- What remains unverified: local audit of the source document and any additional JNTUH metadata not included in the supplied evidence.
- Why unresolved: the document was not downloaded under the stop condition.

### JNTUH Operating Systems

- What we need: the exact plain B.Tech CSE Operating Systems course name, course code, semester, regulation, units, and topics.
- Source found: the official JNTUH B.Tech syllabus repository.
- What was verified: supplied evidence directly supports `Operating Systems`, `CS402PC`, `II Year II Sem.`, R-25 Regulations, Units I-V, and the supplied topic list.
- What remains unverified: local audit of the source document and any additional metadata not included in the supplied evidence.
- Why unresolved: the document was not downloaded under the stop condition.

### JNTUH DBMS

- What we need: the exact plain B.Tech CSE Database Management Systems course name, course code, semester, regulation, units, and topics.
- Source found: the official JNTUH B.Tech syllabus repository.
- What was verified: supplied evidence directly supports `Database Management Systems`, `CS305PC`, `II Year I Sem.`, R-25 Regulations, Units I-V, and the supplied topic list.
- What remains unverified: local audit of the source document and any additional metadata not included in the supplied evidence.
- Why unresolved: the document was not downloaded under the stop condition.

### JNTUH regulation/year

- What we need: the currently applicable plain B.Tech CSE regulation and the relevant academic year.
- Source found: JNTUH’s official syllabus listing and Student Services regulation navigation.
- What was verified: the listing includes an R25 date entry for specialized branches, and the B.Tech repository exposes R22, R18, R16, R15, R13, R09, R07, R05, NR, OR, OOR, and RR navigation labels.
- What remains unverified: which regulation applies to the target plain B.Tech CSE curriculum and whether its R25 material is publicly exposed.
- Why unresolved: branch-specific R25 listings cannot be silently represented as plain CSE evidence.

### Telangana institutions requiring manual review

IIT Hyderabad, IIIT Hyderabad, NIT Warangal, University of Hyderabad, and Osmania University still require a directly opened CSE curriculum source. JNTUH has an official syllabus repository record, but its target course metadata is unresolved. The current catalogue does not claim verified CSE curricula for these institutions.

### NPTEL/SWAYAM licensing and reuse

Four supplied NPTEL candidates were recorded with `verification_status=VERIFIED`, `license=UNKNOWN`, and `usage_status=NEEDS_MANUAL_REVIEW`. Public accessibility is not treated as redistribution permission. No SWAYAM resource was added because no specific candidate record was supplied in this pass.

### Taxonomy mappings requiring academic evidence

The current Python, OS, and DBMS taxonomy rows are canonical resource-evidence records only. They are not university syllabus claims. No university-specific wording, regulation, semester, unit, or canonical mapping has been asserted. Those mappings require verified syllabus course documents.

## Final cleanup counts

- Total institutions: 12
- `VERIFIED` institutions: 2
- `NEEDS_MANUAL_REVIEW` institutions: 10
- Syllabus/course/unit/topic mapping records: 143
- `VERIFIED` syllabus records: 139
- `NEEDS_MANUAL_REVIEW` syllabus records: 4
- Total resources: 7
- `APPROVED` resources: 2
- `NEEDS_MANUAL_REVIEW` resources: 5
- `REJECTED` resources: 0
- Python taxonomy records: 14
- OS taxonomy records: 16
- DBMS taxonomy records: 20
- Duplicate IDs: 0
- Duplicate canonical topics: 0
- Validation failures: 0

## Stop condition

Do not download documents or begin ingestion until the unresolved curriculum URLs, exact course metadata, source permissions, and duplicate/validation checks have been reviewed and approved.
