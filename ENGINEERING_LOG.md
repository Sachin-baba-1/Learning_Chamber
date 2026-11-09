# Learning Chamber — Engineering Log

> Decisions, lessons, and failed approaches — so they survive the conversation that produced them.
> Status: ACCEPTED / PROPOSED / SUPERSEDED / REJECTED. Newest context: 2026-10-24/25 design sessions.

---

**EL-001 — One canonical schema; decouple through storage** · 2026-10-24 · ACCEPTED
Problem: sources (drive/youtube/roadmap) must be replaceable without affecting internals or stored data. Options: adapter interfaces per source; mediator services; single canonical model behind storage. Decision: producers translate INTO one canonical schema; consumers read via typed storage API; storage is the only decoupling point. Why: interfaces guessed before a second source exists are wrong in expensive ways; data-model discipline is cheap now, migration later is not.

**EL-002 — Schema names the domain, never a source** · 2026-10-24 · ACCEPTED
`title` not `fileName`, `kind` not mime-routing flags. Evidence: a schema shaped like Drive's API won't fit YouTube → coupling reborn. Enforced by guardrail 2.

**EL-003 — Consumers are functions, not schema classes** · 2026-10-25 · ACCEPTED (after a failed attempt)
User's schema attempt #1 defined one class per consumer (tree_renderer, text_viewer, generator, player). Rejected: storage can't store four overlapping views; every new consumer would force a schema change. Live evidence found in the attempt itself: same concept as `valid_file` vs `file_type` in two classes — the name-divergence bug predicted and observed within 30 lines. Lesson recorded: **schema stores nouns; consumers are functions.** (Also fixed: `Literal("a"|"b")` is invalid — correct form `Literal["a", "b"]`.)

**EL-004 — Two plugin axes: sources vs extractors** · 2026-10-24 · ACCEPTED
"Where from" (drive, youtube) and "bytes→text" (pdf, docx, transcribe) are different registries. User's list conflated them; separating clarified that `sources/` was entirely missing from the first directory proposal.

**EL-005 — Ingest service is required; it is a module, not a microservice** · 2026-10-25 · ACCEPTED
Test applied: removing it forces a contract violation (plugins would persist, or routers would own integrity, or nothing persists = the old broken app). It is the enforcement mechanism of "in DB ⇒ valid": validation gate, idempotency, partial-failure recording, progress events, params/audit on Import. v1 shape: one synchronous function `run_import()`.

**EL-006 — Replaceability semantics: knowledge survives unconditionally; bytes need a scheme resolver** · 2026-10-24 · ACCEPTED
`source_uri` (e.g. `drive://file/x`) is opaque to consumers; only the resolver maps scheme→plugin. Honest boundary of "replaceable": swap same-scheme plugin = invisible; delete without replacement = everything renders except re-opening that resource's bytes.

**EL-007 — Render from own DB; read paths never live-fetch** · 2026-10-24 · ACCEPTED
Historical failure mode: blank screens whenever auth/quota/network hiccuped because every render re-fetched Drive. Structural fix: import once → persist → render from storage. Guardrail 4, testable by cutting network to the source.

**EL-008 — Provenance on every content block** · 2026-10-24 · ACCEPTED
`created_by: extractor | llm | user`. Directly prevents the placeholder-content failure (fabricated "Topic Summary" text shown as real content, June 2026 session). Guardrail 5.

**EL-009 — Prune = status mark, never delete** · 2026-10-25 · ACCEPTED
Relevance is a policy opinion that changes; irreversibility isn't worth it. Archived resources remain queryable (the "archive page" of the original vision).

**EL-010 — Partial success is a first-class state** · 2026-10-25 · ACCEPTED
`Import.status = completed_with_errors` + `problems[]` at import scope; file-level failure = Resource exists with missing Optional block (legitimate state, not error). Kills the all-or-nothing blank-tree failures.

**EL-011 — No auth/login in v1** · 2026-10-25 · ACCEPTED
Scar tissue: previous sessions died in OAuth consent rabbit holes before one tree rendered. Token passed manually to the endpoint; auth bolted on after M0. A folder you don't create is a rabbit hole you can't fall down.

**EL-012 — Agent framework: neither, yet; LangGraph when the loop exists** · 2026-10-24 · ACCEPTED
First "agent" is a function (context in → LLM → validate → store). Framework choice lives inside one consumer box (reversible). When generate→review→revise arrives: LangGraph over ADK — lower-level teaches the mechanics (stated learning goal); provider-neutral; no Vertex commitment.

**EL-013 — Default generator before LLM generator** · 2026-10-25 · ACCEPTED
Folder structure → modules with zero AI. If that's already useful, the product has legs and the LLM improves a working thing instead of being the thing. (The original drawio already contained both generators behind a conditional — instinct ratified.)

**EL-014 — File-truth vs user-truth split** · 2026-10-25 · ACCEPTED
Resource/ContentBlock = facts about the material. CourseUserData/notes/progress = facts about the user's relationship with it. Test: "would this still be true if a different user opened the same file?" Mixing them makes every schema change a migration.

**EL-015 — Import idempotency via `source_uri` upsert** · 2026-10-25 · PROPOSED
Re-pasting the same link: new Import (audit trail), Resources upserted by `source_uri` (no duplicate trees). Confirm during LC-005 implementation.

**EL-016 — Documentation consolidation** · 2026-10-25 · ACCEPTED
The requested doc system (PROJECT_CONTEXT / ARCHITECTURE / ROADMAP / ENGINEERING_LOG / CURRENT_STATE) replaces TODO.md, whose content is fully absorbed into ROADMAP.md (M0) and ARCHITECTURE.md (decisions). TASKS.md merged into ROADMAP.md to avoid two competing task lists in a solo project — revisit if the project grows contributors.

**EL-017 — GlobalContext is a derived view, not an entity** · 2026-10-25 · ACCEPTED (pending user ratification)
User's attempt #2 included GlobalContext (course counts/lists/completion/skills summary) as a stored entity. Decision: counts and lists are queries; the skills summary is an LLM-generated document (`created_by=llm`, rebuildable). Same error class as EL-003: modeling the report instead of the stored thing. Recorded as the pattern to self-check: *entities are stored nouns; views are computed.*
