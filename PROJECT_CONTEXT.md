# Learning Chamber — Project Context

> Entry point for any new session. Read this, then CURRENT_STATE.md, then work.
> Status labels: VERIFIED (confirmed by inspection/run), DECIDED (agreed decision), PROPOSED (awaiting approval), ASSUMED (unverified belief). Updated 2026-10-25.

## What this is

A platform where a user turns learning resources they already own (Google Drive folders of videos/PDFs/slides/md — later YouTube playlists, roadmap.sh) into a structured, personalized course, then learns inside it: viewer, notes, reflections, explain-back (Feynman) mode, progress dashboard.

Core loop:
```
source link → ingest (translate → validate → persist) → canonical storage
→ course generation (default first, LLM later) → user review → learn (viewer/notes/reflect)
→ dashboard/graph (derived views)
```

The builder is also learning engineering by building this (FastAPI, context engineering, agentic systems) — the project is both product and curriculum.

## Current status — DESIGN PHASE

- **VERIFIED:** No code exists. This folder contains documentation only (listed below).
- Schema v1 is drafted by the user and under review (see CURRENT_STATE.md → LC-001).
- Google Cloud setup (Drive API enabled, OAuth consent, test user, client ID) was completed in prior sessions (June 2026). **ASSUMED still valid — re-verify at first use (LC-004).**
- Previous codebase (June–July 2026) was lost; its failure history is distilled into guardrails in ARCHITECTURE.md.

## Current milestone

**M0 — Walking skeleton:** `Drive link → full recursive folder tree → persisted → rendered from our own DB`. Nothing else until this demonstrably works on the test fixture folder `1TfRFgTIl_yPidjWo8YjK8QEQppjiaPVW` (≥3 nesting levels).

## Architecture in one paragraph

Decoupling happens through **storage, not interfaces**. Source plugins (axis 1: drive, later youtube) translate raw API shapes into **one canonical schema** (Resource, ContentBlock, Import, CourseUserData). Extractors (axis 2: pdf/docx/md/transcribe) turn bytes into ContentBlocks. The **ingest service** is the only writer to storage. All consumers (tree renderer, viewers, player, generator, dashboard) read through a typed storage API — they never know which source produced the data. Full design + guardrails: **ARCHITECTURE.md**.

## Invariants (DECIDED)

1. User-created data (goals, notes, reflections, progress) survives source loss — never cascade-deleted, never stored source-side.
2. The system renders from its own DB; read paths never live-fetch from third parties.
3. Generated content is always distinguishable from extracted content (`created_by` provenance). Never display fabricated text as real content.
4. Schema names the domain, never a source (`title`, not `fileName`).
5. What the user writes is the user's; no silent persistence of content meant to be temporary (ephemeral explain-mode comes later).

## Terminology

- **Resource** — a stored, learnable thing (folder/video/pdf/md/...). Has OUR id + opaque `source_uri`.
- **ContentBlock** — extracted or generated text attached to a Resource (text/transcript/summary/structure), with provenance.
- **Import** — one ingest run: audit record of input, params, status, problems.
- **Source plugin / Extractor** — the two plugin axes (where from / bytes→text).
- **Resolver** — infrastructure that maps `source_uri` scheme (e.g. `drive://`) to a plugin that can re-open bytes.
- **Derived view** — computed or generated data (counts, summaries, embeddings): rebuildable, never primary truth.
- **Walking skeleton** — thinnest end-to-end slice touching every layer.

## Known limitations (current design, deliberate)

Single user, no auth until after M0 (token passed manually), Drive-only source, transcripts deferred, LLM layer deferred behind the default generator.

## Document map

| File | Purpose |
|---|---|
| ARCHITECTURE.md | Components, contracts, canonical model v1 target, guardrails, directory layout |
| ROADMAP.md | Milestones, tasks (LC-xxx) with definition-of-done and status — the only task list |
| ENGINEERING_LOG.md | Every significant decision: context, options, choice, reasoning, status |
| CURRENT_STATE.md | Recovery checkpoint: exactly where to resume and how to verify |

## Working method (condensed protocol)

- User writes the code; the agent is senior mentor/reviewer — direct, critical, no rubber-stamping. Teaching order: intuition → mechanism → implementation.
- Review at three levels: local correctness, component/contract correctness, system correctness.
- A task is DONE only when verified (run/test/inspection) — never because code was written. Unverifiable = marked unknown.
- Scope discipline: NOW / NEXT / LATER. New features must displace something or wait. Don't redesign when running the code would answer cheaper.
- Session recovery: read PROJECT_CONTEXT → CURRENT_STATE → relevant ARCHITECTURE/LOG sections → check repo state → report before acting. Docs win over chat memory; repo wins over docs.

## Next action

**LC-001 — finalize `schema.py`** (entities: Resource, ContentBlock, Import, CourseUserData). See CURRENT_STATE.md for the outstanding corrections.
