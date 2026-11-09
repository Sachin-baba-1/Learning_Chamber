# CURRENT STATE — Recovery Checkpoint

> The resume point. Read after PROJECT_CONTEXT.md. If anything here contradicts the repo, the repo wins — then fix this file. Updated: 2026-11-01.

## Where the project is

**Design phase; first code file exists and compiles.** `schema.py` (attempt #4, project root) fixes the two attempt-#3 blockers (imports added, enum colon syntax fixed) — it compiles and the enums have members. Reviewed 2026-11-01: still NOT passing — one new critical defect (a fastapi import breaching guardrail 1) plus unapplied design corrections (below). No test file yet. `venv1/` virtualenv and `__pycache__/` exist — both get gitignored at LC-002. `schema.py` lives at the root for now; it moves into `backend/app/schema/` when the scaffold is created (§7).

## What is implemented and tested

Nothing works yet. `schema.py` compiles (attempt #4); zero tests exist or run. No backend, no git repo.

## Decisions made

17 entries in ENGINEERING_LOG.md (EL-001…EL-017). Load-bearing: canonical schema + storage as the only decoupling point (EL-001), consumers are functions not classes (EL-003), two plugin axes (EL-004), ingest required (EL-005), render-from-own-DB (EL-007), provenance on all content (EL-008), no auth in v1 (EL-011), default generator first (EL-013).

## Current task: LC-001 — schema v1 (IN_REVIEW)

**Attempt #8 (2026-11-01, VERIFIED ON DISK).** All previous blockers cleared: Import duplicate clock deleted, transcript comment fixed, leftover description line gone, `test_schema.py` created (matches the assigned trio exactly). ONE defect left: `CourseUserData.goal/context/level` written as `goal: str = None` — annotation must be `str | None = None` (the type must admit None; mirror of the earlier missing-default lesson). Tests exist but have NOT been run — user runs the print proof + pytest trio and pastes actual output. On green + the one-line fix ⇒ LC-001 PASS ⇒ LC-002 git init (sequence handed to user: .gitignore with venv1/__pycache__/.env/data, init, add, first commit).

**Assigned lesson (how to test a schema), pytest trio:** valid construction; invalid kind raises ValidationError; JSON round-trip equality — with a `make_resource(**overrides)` fixture. Sequence: fix defects → `print(list(ResourceKind))` proof → 3 tests green → resubmit for contract review. **The user runs all commands themselves (their explicit instruction) — mentor hands scripts, never executes their verification.**

Prior attempt #2 verdicts (2026-10-25), still reference material:

| Draft entity | Verdict | Corrections to apply |
|---|---|---|
| `resource: id, parent_id, path, order, ResourceKind, title` | Strong — 80% there | ADD `source_uri`, `import_id`, `mime`, `status`; make `parent_id` and `order_index` Optional with named states |
| `userContentFORcourse: goal, context, level, knowledge, course_completed` | Keep, rename `CourseUserData` | Drop `knowledge` and `course_completed` (progress = M3) |
| `GlobalContext` | **Not an entity** — derived view (EL-017) | Counts/lists = queries; summary = generated doc with provenance |
| `file: id, content` | This is `ContentBlock` | Needs `resource_id`, `type`, `created_by`, `created_at` |

Recall-draft review (2026-10-26) key corrections, still standing: ContentBlock needs `created_by` + `created_at`; naming drift ("urlpath" → `source_uri`, "name or title" → `title`); `metadata` grab-bag stays cut; `knowledgeID` is dangling (no Knowledge entity); lesson-level user data deferred to M3; `Course`/`CourseLesson` PARKED as M2 entities (CourseLesson must reference `resource_id` when it arrives).

Target field list to write against: **ARCHITECTURE.md §3**. Acceptance: the four schema reviews (no external imports; no source-specific names; every Optional has a named state; no unconsumed field) + consumer functions sketched as signatures.

## Incomplete / blocked / risky

- Google Cloud credentials ASSUMED working (set up June 2026, not touched since) — first thing to re-verify at LC-004.
- No git repo yet (LC-002) — docs + schema.py are unprotected against accidental loss. **Do LC-002 early.**
- Project root is this folder for now; if the code scaffold moves elsewhere, these docs move with it (EL-016 context).
- Session stability: the prior chat died to context-window overflow — keep new-session resumes small and lean on this doc system (that is what it is for).

## Single best next task

**Finish LC-001 on disk:** apply the six attempt-#4 findings to `schema.py`, create `test_schema.py` (script handed in-session), run the print proof + pytest trio (user runs them), paste the actual output for contract review. Then LC-002 (git init — protects everything; gitignore `venv1/`, `__pycache__/`, `.env`, `data/`).

## Read before continuing

1. CURRENT_STATE.md (this file) 2. PROJECT_CONTEXT.md 3. ARCHITECTURE.md §3 (canonical model target) + §6 (guardrails) 4. ENGINEERING_LOG.md EL-003, EL-014, EL-017 (the lessons most likely to recur).

## Commands to verify current state

Run from the folder containing `schema.py`:

- `python -c "import schema"` — compiles since attempt #4 (enums have members). Expected to keep working after the fastapi line is deleted.
- `python -c "from schema import ResourceKind; print(list(ResourceKind))"` — currently lists 8 members; after the value fixes it must list: folder, text, pdf, pptx, docx, markdown, video, webpage.
- `pytest test_schema.py -v` — the trio; all green = attempt #5 ready for contract review.

Do not invent verification results — run and paste actual output.

## Do not change without reopening the decision

- The one-canonical-schema principle and "consumers are functions" (EL-001/EL-003).
- No-auth-in-v1 (EL-011) — resist the OAuth rabbit hole until M0 exits.
- Default-generator-first ordering (EL-013).
- The M0 gate itself: no M1 work until the milestone exit criteria in ROADMAP.md demonstrably pass on the fixture folder.
