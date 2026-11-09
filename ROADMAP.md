# Learning Chamber — Roadmap & Task List

> The ONLY task list (absorbs the old TODO.md — see ENGINEERING_LOG EL-016). Statuses: TODO / IN_PROGRESS / BLOCKED / IN_REVIEW / DONE / DEFERRED.
> A task is DONE only when its verification actually ran and passed. Updated 2026-10-25.

## Scope discipline

NOW = current milestone (M0). NEXT = known dependency, soon. LATER = parked, do not build. A new feature must displace something or wait.

---

## M0 — Walking skeleton (NOW)

**Milestone exit criteria (all must be demonstrably true):**
paste "anyone with link" Drive URL → backend recursively lists every folder/file (`id, name, kind, mime, size, modifiedTime`) → persisted → tree rendered **from our DB** → user visually confirms exact match against real Drive structure (names preserved exactly) on fixture folder `1TfRFgTIl_yPidjWo8YjK8QEQppjiaPVW` (≥3 nesting levels). Pagination handled. Failures produce readable messages, never blank screens.

| ID | Task | Status | Definition of done / verification |
|---|---|---|---|
| LC-001 | `schema/` v1: Resource, ResourceKind, ContentBlock, BlockType, Import, CourseUserData | IN_REVIEW (attempt #2 under review) | Imports only stdlib+pydantic; passes the four reviews (no external imports; no source-specific names; every Optional has a named state; no unconsumed field); two-source test conceivable; consumer functions sketched as signatures |
| LC-002 | `git init` + repo hygiene | TODO | Repo exists; `.gitignore` covers `.env`, `data/`, `__pycache__`, venv; first commit of docs |
| LC-003 | `storage/` module (SQLite via SQLModel) | TODO | Tables mirror schema exactly; write API (ingest only) + read API (`get_tree`, `build_course_context`) exist with typed returns; round-trip test: insert fake Resources → `get_tree` returns them |
| LC-004 | `sources/drive/`: `extract_folder_id(url)` + `list_folder_tree(token, root_id)` | TODO | Port of proven Colab logic (regex + `q="'<id>' in parents and trashed=false"` + pagination loop). Verified against fixture folder: all folders/files, ≥3 levels, exact names. Also: re-verify Google Cloud credentials still work (ASSUMED since June) |
| LC-005 | `ingest/`: `run_import()` + registry + events | TODO | Emits ResourceFound/Progress/Error events; validates before persist; Import record with status/counts/problems; folder containing one broken item → `completed_with_errors`, successes persisted |
| LC-006 | Router `GET /api/v1/courses/{import_id}/tree` reading FROM DB | TODO | Response = stored Resources only; works with source network blocked (guardrail 4) |
| LC-007 | Minimal frontend: paste link → live progress → tree | TODO | Explicit loading/empty/error/success states; error shows cause + fix ("token expired → re-connect") |

## M1 — Viewing honesty (NEXT)

Extractors created here, one at a time, only when first needed: md/txt (render stored text) → pdf (bytes via resolver + PDF.js; `Content-Disposition: inline`; never triggers download) → docx/pptx (extracted text view). Video streaming with Range support. No Google iframes, ever.

## M2 — Course generation (NEXT)

Default generator FIRST (folder structure → modules; zero AI — proves value without LLM). Then user states goal + carried question (CourseUserData) → context builder assembles bundle → LLM generator improves structure → user review gate → Course entity persisted referencing Resource IDs only.

## M3 — Learning loop (LATER)

Session logging (<30s), notes (user-truth keyed to resource), reflection prompts, explain-back mode (ephemeral option), dashboard (derived views: hours, streaks), progress/completion tracking.

## Deferred (LATER — do not start)

YouTube/roadmap.sh sources · auth/login (after M0) · knowledge graph view · transcripts/Whisper · LLM framework choice (LangGraph preferred when review-loop exists — EL-012) · embeddings/knowledge base · blockchain/social/sparring-partner ideas · frontend beyond the minimal tree page.

---

## Trace requirement (per task)

Requirement → expected behavior → design decision (EL-xxx) → components touched → contracts preserved → implementation → verification run → observed result → docs updated. Record in CURRENT_STATE.md when a task completes; log new decisions in ENGINEERING_LOG.md.
