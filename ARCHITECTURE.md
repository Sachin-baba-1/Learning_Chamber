# Learning Chamber — Architecture

> How the system is designed and why. Status labels as in PROJECT_CONTEXT.md. Updated 2026-10-25.
> Nothing here is implemented yet — this is the approved target (DECIDED) the code will be built against.

## 1. The one principle

**Decouple through storage, not interfaces.** Plugins never talk to plugins; consumers never talk to plugins. Producers write INTO one canonical model; consumers read FROM it. There are exactly two contracts and one data model between them:

```
SOURCE PLUGINS ──(contract 1: produce canonical entities)──▶ STORAGE ──(contract 2: typed read API)──▶ CONSUMERS
 drive, later yt/roadmap      ingest validates before         canonical schema       tree renderer, viewers,
                              writing (only door in)          = single truth         player, generator, dashboard
```

Corollary (DECIDED): **the schema is designed from the domain and consumers, never from a source.** Sources bend to fit it (translation happens inside the plugin; raw API shapes never leave it).

## 2. Components

| Component | Owns | Must never |
|---|---|---|
| `schema/` | canonical entities, pure types | import anything beyond stdlib/pydantic |
| `storage/` | the only door to the DB (write via ingest, typed reads for consumers) | be bypassed by direct DB access elsewhere |
| `ingest/` | `run_import()`: route input → plugin → validate → persist → progress events; registry; idempotency | contain source-specific or extraction logic |
| `sources/<name>/` | axis 1 plugins: accept input, translate raw → canonical, re-open bytes by scheme | persist directly, leak raw shapes, know about other plugins |
| `extractors/` | axis 2: bytes → ContentBlock (pdf, docx, md, later transcribe) | know which source fetched the bytes |
| `ai/` (later) | context builder, default generator, LLM generator, coach; its own I/O DTOs validated → canonical before storing | redefine canonical entities; keep private memory stores (memory = storage-backed UserData) |
| `routers/` | thin HTTP layer | own business logic or persist |

## 3. Canonical model v1 (target for LC-001)

```python
ResourceKind: folder | video | pdf | markdown | text | docx | pptx | webpage

Resource
  id: UUID                      # ours forever, generated at ingest
  import_id: UUID               # provenance: which ingest run
  title: str                    # exact source string, never normalized
  kind: ResourceKind            # routing decision for renderer/viewer/player
  parent_id: UUID | None        # None = root of this import
  path: str                     # "Mission 1/Week 2.3" display hierarchy
  order_index: int | None       # None = source defined no order
  mime: str | None              # None = source gave no mime; player detail
  size_bytes: int | None
  modified_at: datetime | None  # source's timestamp if any
  source_uri: str               # "drive://file/<id>" — OPAQUE to all consumers
  status: active | archived     # prune = mark, never delete

ContentBlock
  id, resource_id
  type: text | transcript | summary | structure
  content: str                  # transcripts keep timestamps inline (VTT-style)
  created_by: extractor | llm | user     # provenance — honesty invariant
  created_at

Import
  id, source_id (which plugin), input_raw (pasted link)
  params: {max_depth, ...}
  status: running | completed | completed_with_errors | failed   # durable progress
  counts: folders_found, files_found, problems_count
  problems: [str]               # import-scope failures (auth, root inaccessible)
  started_at, finished_at

CourseUserData                  # user-truth, keyed by (user, course)
  goal: str | None              # includes "the question I carry into this course"
  context: str | None
  level: str | None             # beginner/intermediate/... self-declared
```

**Not entities (DECIDED — derived views, do not store):** GlobalContext (course counts/lists/completion = queries; skills summary = LLM-generated doc with `created_by=llm`, rebuildable), `depth` (derivable from path), any `metadata: dict` grab-bag. Notes/reflections/lesson-completion become entities in M3, not before.

**Two-source test (the schema's acceptance test):** a Drive file and a YouTube video must both map into `Resource` with zero schema change — `drive://file/...` vs `youtube://video/...`, `order_index=None` vs playlist position.

## 4. What "replaceable plugin" honestly means (DECIDED)

- Extracted knowledge in storage survives any plugin swap **unconditionally** (it's ours).
- **Re-streaming bytes** is the only source-dependent act: `source_uri` scheme → resolver → plugin. Swap Drive v1 for v2 (both speak `drive://`) → nothing downstream notices. Delete with no replacement → everything renders except re-opening that one video.

## 5. Data flows

**Import (write path):** user pastes link → router → `ingest.run_import()` → registry picks plugin (`can_accept`) → plugin streams events (`ResourceFound`, `BlockExtracted`, `Progress`, `Error`) → ingest validates each against schema → persists → forwards events to UI. Import finishes `completed_with_errors` if some files failed — **partial success never discards success**. Same link pasted twice → two Imports (audit), Resources **upsert on `source_uri`** (no duplicate trees) — PROPOSED, confirm at implementation.

**Render (read path):** every consumer queries storage. Tree renderer: `get_tree() -> list[Resource]` (title, kind, parent_id, order_index, path). Text viewer: `kind` decides family — md/docx/pptx/text render stored ContentBlocks (no source contact); pdf/video ask the resolver for bytes. Player: bytes via resolver + transcript block + pause point (UserData, M3). Generator: context builder assembles Resources + Blocks + CourseUserData into the course-context bundle — never sees raw files.

**Idempotency & audit:** Import is the audit record — what was pasted, which plugin, params, what failed, when. "What actually happened" must always be answerable from storage.

## 6. Guardrails

Each: rule — why — how to detect/enforce.

1. **`schema/` imports nothing external** (stdlib/pydantic only) — the contract stays pure — code review; trivially checkable.
2. **No source-native field names/IDs beyond the plugin boundary** — replaceability — review: grep for `drive`/`youtube` outside `sources/`; `source_uri` never parsed by consumers.
3. **All reads/writes go through `storage/`** — single door keeps "in DB ⇒ valid" true — review; no direct engine/session use elsewhere.
4. **Read paths never live-fetch from sources** — fixes the blank-screen failure class — test: render tree with network to source cut.
5. **Generated ≠ extracted, always distinguishable** — `created_by` on every block — test + review; violation = fake-content bug (killed a previous session).
6. **Every Optional has a named legitimate state** (comment) — None is a state, not an error — review at schema changes.
7. **Partial failure keeps partial results** (`completed_with_errors` + problems) — all-or-nothing blank screens killed previous sessions — test with a folder containing one broken file.
8. **No secrets in the repo** — `.env` + `data/` gitignored from commit zero — automated via .gitignore.
9. **User data survives source loss** — no deletion path from source state to UserData — design review of any delete logic.
10. **UI states are explicit**: loading / empty / error / success — "blank screen" is a bug by definition — review each screen.

## 7. Directory layout (DECIDED)

```
backend/
  app/
    main.py            # FastAPI wiring only
    schema/            # canonical entities (this file's §3)
    storage/           # only door to DB
    ingest/            # run_import(), registry, events
    sources/drive/     # axis 1 plugin #1
    extractors/        # axis 2 (pdf, docx, md — created when first needed)
    ai/                # created at M2, not before
    routers/
data/                  # runtime artifacts (SQLite file) — gitignored, ZERO code
frontend/              # separate app, decided later
```

Create folders only when they receive code. v1 needs: `main.py`, `schema/`, `storage/`, `ingest/`, `sources/drive/`, one router. **No auth/login in v1** — deliberately deferred past M0 (previous sessions died in OAuth rabbit holes before a single tree rendered).

## 8. Known risks

- **Drive token flow unverified in this workspace** (prior setup ASSUMED) — first real risk to surface at LC-004.
- **Project root not yet fixed as a git repo** — decide at LC-002; if the project moves, these docs move with it.
- LLM/agent layer deliberately last (default generator first) — see ENGINEERING_LOG EL-013/EL-012.
