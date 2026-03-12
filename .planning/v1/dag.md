# Iterative Decomposition DAG

**This file contains directives only. Do not add justifications, rationale, history, or editorial. Every sentence must be a directive, constraint, or definition. If a rule needs a "why", put it in FINDINGS.md.**

**Sync requirement: Before starting any project iteration: (1) run `python3 scripts/dag-to-json.py DAG.md templates/json/` to regenerate JSON templates from this DAG, (2) if any JSON changed, commit before proceeding, (3) copy `templates/json/` into the project's `.planning/vN/checklists/` as runtime state. Agents read and update the JSON checklists during execution — the JSON is the machine-readable form of this DAG.**

## Stages

1. **Raw requirements** — Capture user's words verbatim. Do not modify after initial capture.

   | # | Step | Executor |
   |---|------|----------|
   | items[0] | Capture user's words verbatim | Lead agent |
   | gates[0] | User confirms capture is accurate | User |

2. **Clean requirements** — Derive from raw requirements first, unbiased. Then reconcile against previous clean requirements and upstream feedback. Organize by domain. Write WHAT, not HOW.

   | # | Step | Executor |
   |---|------|----------|
   | items[0] | Derive clean requirements from raw + upstream feedback | Lead agent |
   | items[1] | Organize by domain, write WHAT not HOW | Lead agent |
   | gates[0] | User reviews and approves clean requirements | User |

3. **Research** — Survey existing code, tools, skills, prior art, and technical constraints. Write findings to disk.

   | # | Step | Executor |
   |---|------|----------|
   | items[0] | Scope research topics from clean requirements | Lead agent |
   | items[1] | Survey existing code, tools, prior art per topic | Explore agents (parallel) — Opus for highest-uncertainty topic, Sonnet for rest |
   | items[2] | Assemble findings to disk | Lead agent |
   | gates[0] | User reviews research findings | User |

4. **Decomposition** — Map requirements to spec units. Identify dependencies. Sequence build order. Produce: spec unit list with dependency graph. Produce: **boundary dependency map** — for every edge in the dependency graph, name the shared boundary and its contract type (naming contract, data shape, event type, state transition, route path). The boundary dependency map is a living artifact — create it here, refine it at every reflect gate through Stage 9.

   | # | Step | Executor |
   |---|------|----------|
   | items[0] | Map requirements to spec units | Lead agent |
   | items[1] | Identify dependencies, sequence build order | Lead agent |
   | items[2] | Produce boundary dependency map with contract types | Lead agent |
   | gates[0] | User reviews decomposition and dependency graph | User |

5. **Spec tree** — Express architecture as filesystem hierarchy. The tree must be reviewable from `tree` output alone.

   | # | Step | Executor |
   |---|------|----------|
   | items[0] | Create filesystem hierarchy from decomposition | Lead agent |
   | gates[0] | Tree is reviewable from `tree` output alone | Lead agent |
   | gates[1] | User reviews and approves spec tree | User |

6. **Specifications** — Fill each spec with behavior, constraints, and edge cases. Write WHAT, not HOW. Leave zero judgment calls for the implementer. After specs are approved, a **separate agent** (not the spec-writing agents) reads each spec and extracts every testable behavioral contract to `test-contracts.md` — input/output pairs, precondition/postcondition pairs, edge case expected outcomes. Vague behavior ("handles errors appropriately") is not a contract — rewrite the spec. `test-contracts.md` is a **living artifact**: behavioral contracts (Stage 6) → test file stubs (Stage 7) → test pseudo-logic (Stage 7d) → implemented tests (Stage 8) → reconciled (Stage 8b). **Reflect gate: cross-spec contract reconciliation.** After all specs are written, assign one agent per boundary edge (from the dependency map). That agent reads both specs and extracts the contract each side assumes — function name, event type, DOM ID, state name, route path. Mismatches are findings. Append newly discovered boundaries to the dependency map.

   | # | Step | Executor |
   |---|------|----------|
   | items[0] | Write specs — behavior, constraints, edge cases | General-purpose agents (fan-out) — Opus for deepest spec, Sonnet for rest |
   | items[1] | Extract testable contracts to `test-contracts.md` | Separate Sonnet agent (not the spec writers) |
   | items[2] | Cross-spec contract reconciliation per boundary edge | Explore agents (one per edge) |
   | gates[0] | Reflect gate: zero contract mismatches across spec boundaries | Lead agent |
   | gates[1] | User reviews and approves specifications | User |

7. **Scaffolding** — Create stubs, file headers, pseudo-logic per project conventions. Execute in two phases: tree first (biased generalist), then content (unbiased specialists per spec). **Manifest-driven file creation:** the tree agent produces a `.scaffold-manifest` file (tab-separated: path, spec, purpose, responsibilities, not_responsible_for, dependencies) instead of creating files individually. Run `python3 scripts/scaffold-from-manifest.py <manifest> --project-root <path>` to create the directory structure and stamp every file with its `SPEC:` provenance tag and comment header in one pass. See `templates/scaffold-manifest-format.md` for the manifest format. This eliminates hundreds of individual file-creation tool calls. Every scaffold file header must include a `SPEC:` provenance tag pointing to the spec that owns it (e.g. `SPEC: .planning/v2/specs/s06-gemm.md`). The tree agent also produces: test file stubs for every contract in `test-contracts.md`, and a **pattern registry** (`pattern-registry.md`) declaring the one chosen pattern per cross-cutting concern (HTTP client, error handling, data access, logging, config, template rendering). **Convergence gate:** zero tree mutations across specialist passes. After specialist passes converge, run **cross-reference reconciliation**: extract every string-based cross-reference (template names, DOM IDs, CSS classes, route paths, config keys) from all scaffold files and verify both sides agree. Run **pattern consistency check**: verify all scaffold files follow the pattern registry — deviations are findings. Run **test contract coverage check**: verify every contract in `test-contracts.md` has a test stub in the scaffold. Run **spec provenance check**: `grep -rh "SPEC:" src/` must cover every spec in the decomposition — missing or mismatched tags are findings. Name mismatches between scaffold files are findings that block Stage 8. Use the boundary dependency map from Stage 4 (refined at Stage 6) as input — check every named edge. Append newly discovered file-level boundaries to the map.

   | # | Step | Executor |
   |---|------|----------|
   | items[0] | Phase 1: generate `.scaffold-manifest`, run script | Lead agent |
   | items[1] | Phase 2: fill pseudo-logic per spec into stubs | Sonnet agents (fan-out, one per spec) |
   | items[2] | Cross-reference reconciliation (string-based contracts) | Explore agent(s) |
   | items[3] | Pattern consistency check against `pattern-registry.md` | Explore agent |
   | items[4] | Test contract coverage check | Explore agent |
   | items[5] | Spec provenance check (`grep -rh "SPEC:"`) | Explore agent |
   | gates[0] | Convergence gate: zero tree mutations across specialist passes | Lead agent |
   | gates[1] | User reviews and approves scaffold | User |

8. **Implementation** — Write code between scaffold comments. Implementation agents may only create or modify files that exist in the scaffold tree. Implement tests alongside production code, not after. Follow the pattern registry for every cross-cutting concern.

   | # | Step | Executor |
   |---|------|----------|
   | items[0] | Implement production code per build wave | General-purpose agents (fan-out) — Opus for hardest task per wave, Sonnet for rest |
   | items[1] | Implement tests alongside production code | Same agents as items[0] |
   | items[2] | Reflect gate between each wave | Lead agent |
   | gates[0] | All scaffold files have code between comments | Lead agent verifies |
   | gates[1] | User reviews and approves implementation | User |

8b. **Scaffold Reconciliation** — Convergent single-pass verification. For every file in the scaffold tree, classify as IMPLEMENTED, SUPERSEDED (name the replacement), INTENTIONAL-EMPTY (state the rationale), or MISSING (this is a finding). Diff scaffold file list against implementation file list. Any file in one but not the other is a finding. MISSING entries block Stage 9. **Wiring check**: for every coordinator/orchestrator/bridge file, verify it actually calls the sub-packages it references. A file that imports a package but never calls its functions is a finding. **Test contract reconciliation**: for every contract in `test-contracts.md`, verify a test function exists with actual assertions (not stubs). Contracts without tests block Stage 9. **Pattern drift check**: verify all implementation files follow `pattern-registry.md`. No package may use a different approach than the registered pattern for the same concern. **Spec provenance reconciliation**: `grep -rh "SPEC:" src/` — every spec must have at least one file, every file must trace to exactly one spec, no orphan tags pointing to nonexistent specs. **Dependency map update**: append newly discovered function-level boundaries. The map now has three layers: spec-to-spec (Stage 4/6), file-to-file (Stage 7), function-to-function (Stage 8b).

   | # | Step | Executor |
   |---|------|----------|
   | items[0] | Classify every scaffold file (IMPLEMENTED/SUPERSEDED/EMPTY/MISSING) | Explore agent (Sonnet) |
   | items[1] | Wiring check — coordinators call what they import | Explore agent (Sonnet) |
   | items[2] | Test contract reconciliation — assertions not stubs | Explore agent (Sonnet) |
   | items[3] | Pattern drift check against `pattern-registry.md` | Explore agent (Sonnet) |
   | items[4] | Spec provenance reconciliation (`grep -rh "SPEC:"`) | Explore agent (Sonnet) |
   | gates[0] | Zero MISSING files, zero orphan tags | Lead agent verifies |
   | gates[1] | User reviews reconciliation report | User |

9. **Verify** — Two layers. Layer 1 (static): run build, vet, and test, including frontend assertions — template manifest completeness, CSS link validation, orphan template detection. Layer 2 (runtime): run smoke tests — app boot, primary flow, moving parts connect. Coordinator writes runbook, spawns verify agent.

   | # | Step | Executor |
   |---|------|----------|
   | items[0] | Layer 1 (static): run build, vet, test | Sonnet agent |
   | items[1] | Layer 2 (runtime): run smoke tests — app boot, primary flow | Sonnet agent (depends on items[0]) |
   | items[2] | Cross-spec mismatch audit + backward correctness | Opus agent |
   | items[3] | SPEC tag integrity + manifesto compliance | Sonnet agent |
   | gates[0] | Coordinator writes runbook | Lead agent |
   | gates[1] | User reviews and approves verification | User |

## Gating

- Each stage gates the next. Do not begin stage N+1 until stage N is reviewed and approved.
- Apply /husband protocol at every stage: listen, record, clarify, draw out. Do not solution ahead of the current stage.
- Gate pass/fail is recorded in the stage's JSON checklist. When all `gates[].done` are `true` and user approves, set `status` to `"done"`. If any gate fails, set `status` to `"blocked"` and append the failure to `findings[]`.

### Checklist Bookend Protocol

At the **beginning** and **end** of every stage, the lead agent presents the stage's checklist to the user as a table. The two presentations must align — same items, same structure, different status column.

1. **Stage entry:** Read the stage's JSON checklist via `jq`. Present a table with columns: `#`, `Step`, `Executor`, `Status`. All items show their current status (typically `pending` at entry). This is the contract — "here is what this stage will do."
2. **Stage exit:** Read the same JSON checklist via `jq`. Present the same table with updated statuses. Every item must be `done`, `blocked` (with reason), or `deferred` (with reason). No item may silently disappear between entry and exit.
3. **Alignment rule:** The entry table and exit table must have the same rows in the same order. If work during the stage revealed new items, append them to the checklist JSON before presenting the exit table — they appear as new rows, not replacements.
4. **The exit table IS the gate review.** Do not present a prose summary instead of the table. The user sees the checklist, not a narrative.

### Reflect Gate Failure Protocol

When a reflect gate fails:

1. **Stop.** Do not fix the failure in place. Do not patch downstream artifacts.
2. **Diagnose upstream.** Trace the failure to the upstream layer that caused it. A missing test stub is not a scaffold problem — it is a scaffold agent prompt problem or a spec ambiguity.
3. **Record the finding.** Write to `upstream-feedback.md` with: stage, gate name, failure description, upstream layer responsible, proposed fix. Also append to the stage's JSON checklist `findings[]` and set the gate's `done` to `false`.
4. **Present to user.** Report the failure and the upstream diagnosis. Do not proceed without approval.
5. **Fix upstream, regenerate downstream.** If the fix is in the spec, update the spec, then regenerate scaffold from the spec. If the fix is in the scaffold agent prompt, re-run the scaffold agent with the corrected prompt. Do not hand-edit downstream artifacts to compensate for upstream gaps.
6. **Re-run the gate.** After regeneration, re-run the same reflect gate. The gate must pass on regenerated output, not on patched output.
7. **Cost awareness.** Before regenerating, estimate the token/time cost. If regenerating an entire stage is disproportionate to the fix, present the tradeoff to the user: regenerate (correct) vs. targeted upstream fix + partial regeneration (pragmatic). User decides.

## Inputs

Two immutable inputs feed the DAG:

1. **REQUIREMENTS-RAW.md** — What the user said. Do not modify.
2. **upstream-feedback.md** — Accumulated HOW from every stage: every design decision, bug fix, gap discovered, correction applied. Classify each entry by the upstream layer that was wrong.

`upstream-feedback.md` is the single artifact that survives regeneration. When v(N+1) starts, agents read raw requirements + upstream feedback and re-derive everything.

## Convergence-Divergence Boundary

- **Stages 1-6:** Convergent. Single agent (or sequential per-spec fan-out for Stage 6), sequential, full context.
- **Stages 7-8:** Divergent. Fan-out across spec units. Coordinator assembles context blob. Agents claim specs via registry. Work per-spec. Run reflect gate between each wave.
- **Stage 8b:** Convergent. Single reconciliation pass.
- **Stage 9:** Convergent. Single verify agent with runbook.

## Rules

### Stage Discipline
- Every stage gates the next. Do not skip. Do not blend.
- Write WHAT not HOW until Stage 7. Requirements and specs describe behavior. HOW decisions go to `upstream-feedback.md`, not into specs.
- Trace everything. Every spec traces to requirements. Every scaffold file traces to a spec via its `SPEC:` header tag. Every implemented file traces to a scaffold file. Untraced artifacts are ungrounded. `grep -rh "SPEC:" src/` is the traceability index.
- Conventions that shape output are requirements. If a constraint in agent instructions affects the product, it must also appear in clean requirements.

### Derivation Discipline
- Derive fresh, then reconcile. Do not patch incrementally. Derive from upstream inputs first, then diff against prior output.
- Raw is immutable. New information goes to `upstream-feedback.md`. Do not modify raw.
- Nothing downstream is precious. If the DAG says regenerate, regenerate.
- Do not read prior specs when deriving new specs. Agents derive from upstream inputs only.
- A stage is done when independent agents stop finding new gaps, not when all agents finish.

### Grounding Discipline
- On context resumption, re-read artifacts from disk. Do not rely on conversation summaries. Re-read the stage's JSON checklist to restore progress state.
- **Initialize checklists at iteration start.** Before any stage work begins: (1) run `python3 scripts/dag-to-json.py DAG.md templates/json/` to ensure templates reflect the current DAG, (2) copy `templates/json/` into `.planning/vN/checklists/`, replacing `vX` with the actual iteration version. These JSON files are the runtime checklists agents read and update. The full pipeline is visible from day one.
- **JSON checklist update protocol.** Agents read and write `.planning/vN/checklists/stage-NN-name.json` directly. The JSON is the runtime state — not a report, not a log. Agents interact with it using `jq` via the Bash tool:

  **Read current state** — agent loads JSON at stage start and after context resumption:
  ```
  cat .planning/v1/checklists/stage-04-decomposition.json | jq .
  ```

  **Set stage status:**
  ```
  jq '.status = "in-progress"' file.json > tmp.$$.json && mv tmp.$$.json file.json
  ```

  **Mark item done by index:**
  ```
  jq '.items[0].done = true' file.json > tmp.$$.json && mv tmp.$$.json file.json
  ```

  **Mark gate done by index:**
  ```
  jq '.gates[1].done = true' file.json > tmp.$$.json && mv tmp.$$.json file.json
  ```

  **Mark cross-ref checked by index:**
  ```
  jq '.cross_refs[0].done = true' file.json > tmp.$$.json && mv tmp.$$.json file.json
  ```

  **Append a finding:**
  ```
  jq '.findings += ["boundary map missing edge between auth and session"]' file.json > tmp.$$.json && mv tmp.$$.json file.json
  ```

  **Recompute progress:**
  ```
  jq '.progress.done = ([.items[], .gates[]] | map(select(.done)) | length) | .progress.total = ([.items[], .gates[]] | length)' file.json > tmp.$$.json && mv tmp.$$.json file.json
  ```

  **Compound update** — multiple fields in one pass:
  ```
  jq '.status = "done" | .items[2].done = true | .gates[0].done = true | .findings += ["resolved: missing stub"]' file.json > tmp.$$.json && mv tmp.$$.json file.json
  ```

  **Query remaining work** — filter incomplete items without reading the full file:
  ```
  jq '[.items[] | select(.done == false) | .text]' file.json
  ```

  **Query failing gates:**
  ```
  jq '[.gates[] | select(.done == false) | .text]' file.json
  ```

  **Query unchecked cross-refs:**
  ```
  jq '[.cross_refs[] | select(.done == false) | .text]' file.json
  ```

  **Pipeline-wide status** — find what's blocking across all stages:
  ```
  jq '.stages[] | select(.status != "done") | {stage, name, remaining: [.items[] | select(.done == false) | .text]}' .planning/v1/checklists/dag-progress.json
  ```

  **Why jq, not Edit/Read:** Agents must use `jq` for all checklist interaction — not the Read tool, not the Edit tool, not manual markdown parsing. `jq` queries return only what the agent needs (remaining items, failing gates) without loading file contents into context. `jq` writes update fields by index without pattern-matching on strings. This keeps agent context small and eliminates drift between what the agent thinks the file says and what it actually says.

  **Rules:** Read before writing — never write from memory. Update after each discrete action, not in batch at stage end. If two agents share a stage (fan-out), the coordinator owns the JSON and agents report completions to the coordinator who writes. Always use the `jq ... > tmp.$$.json && mv` pattern — never redirect to the same file you're reading.
- Blocked means blocked. Do not improvise workarounds. Set `status` to `"blocked"`, record why in `findings[]`, stop, report.
- Do not decompose without research. No specs without surveying existing code, tools, and prior art.
- DAG changes invalidate downstream artifacts. Regenerate JSON templates from DAG, re-copy into `.planning/vN/checklists/`, and re-derive from the new checklists.

### Manifesto Enforcement (Stages 7-9)
- `MANIFESTO.md` is active at stages 7, 8, 8b, and 9. Violations are findings.
- Scaffold agents apply manifesto rules structurally: filesystem-as-DB naming, reference integrity design, machine-readable outputs, config cascade. Bake these into the scaffold.
- Scaffold cross-reference reconciliation is mandatory. After specialist scaffold passes converge, extract all string-based naming contracts between scaffold files (template name ↔ Execute() call, DOM ID ↔ OOB target, CSS class ↔ HTML class, route path ↔ handler registration). Both sides must agree. Mismatches block implementation.
- Verify agents check manifesto compliance. Each manifesto rule must have a checkable artifact or test. "We followed it" is not evidence.
- Run two-pass audit at verify. Pass 1 (broad sweep): one agent scans the full project against all manifesto rules, produces a triage list of failing rules and violation counts. Pass 2 (deep dive): one agent per spec reads the spec's behavioral guarantees and the implementing code line by line, checks whether the code delivers what the spec promises. Do not skip Pass 1. Do not stop at Pass 1.

### Implementation Discipline
- The scaffold file list IS the implementation checklist. Do not create files outside the scaffold tree. If the scaffold structure is wrong, that is a finding → write to upstream feedback → update scaffold → then implement.
- Implementation agents read scaffold stubs and write code between the comments. They do not need the full upstream context chain.
- Stage 8b classifies every scaffold file as IMPLEMENTED, SUPERSEDED (with named replacement), INTENTIONAL-EMPTY (with rationale), or MISSING (finding). No silent survivors. Stage 8b also verifies every `SPEC:` tag — orphan tags, missing tags, and mismatched tags are findings.
- Stage 8b checks wiring, not just existence. For every coordinator, orchestrator, or bridge file: verify it calls the sub-packages and functions it references. Import without invocation is a finding. Handler that bypasses its orchestrator is a finding.
- Empty stubs satisfy compilers. Only the reconciliation manifest and runtime smoke tests catch silent gaps.

### Feedback Discipline
- Identify which upstream layer was wrong. Record in `upstream-feedback.md`. Fix upstream and regenerate. Do not patch downstream.
- Classify findings as PROJECT or METHODOLOGY. Project findings go to `upstream-feedback.md`. Methodology findings go to this repo. Do not mix.
- All reflect gate resolutions go to `upstream-feedback.md` — resolved and unresolved. Tag by stage and wave. Also record in the stage's JSON checklist `findings[]`.

### Coordinator Discipline
- Coordinator manages context, not content. Do not write specs, scaffold, or code. Spawn agents with scoped context.
- Write coordinator playbook to disk: agent prompt template, per-spec file ownership, wave dependencies, reflect protocol. A fresh coordinator picks up from the playbook.
- Include explicit file ownership in every agent prompt: YOUR FILES (specific scaffold files) and OFF-LIMITS (everything else, including files that do not exist).
- **Checklist-driven execution protocol.** Before spawning agents for any stage:
  1. **Read** the stage's JSON checklist via `jq .` — load items, gates, cross_refs.
  2. **Present** the checklist to the user as a table: item text, who will execute it (lead or which subagent type), and current done/not-done status. The user must see the plan derived from the checklist, not from the coordinator's memory. The stage definitions above include the canonical table for each stage — use that as the template, add a `Status` column populated from the JSON.
  3. **Derive** each agent's prompt FROM the checklist items — items become the agent's work list, gates become its acceptance criteria. Include the `jq` commands the agent must run to mark items done as it completes them.
  4. **Require** every agent to update the JSON checklist via `jq` after completing each item. No prose-only reports. The JSON is the source of truth.
  5. **Verify** after agents complete: re-read the checklist via `jq`, confirm items are marked done, present updated state to user. If prose reports and checklist state disagree, the checklist wins.
  Do not spawn an agent without a task checklist on disk. Do not present gate reviews based on prose summaries when the checklist shows 0/N done. Do not write agent prompts from memory — read the JSON first.
- Enforce claim ordering: use sequential spawn or coordinator pre-marking. Verify wave dependencies before claiming.
- Coordinator never idles. Spot-check output, update claims, write manifests, prep next wave, log findings.
- Wave context is the file tree, not a source dump. Agents read specific files on-demand.
- Model routing for fan-out: assign the hardest agent task per wave to Opus (`model: "opus"`). All other agents use Sonnet (default). "Hardest" = deepest algorithmic reasoning, most cross-cutting dependencies, or highest risk of subtle bugs.

## Stage Gate Cross-References

External skill rules that apply at each stage gate. Agents check these alongside DAG rules. Rule definitions live in their source skill — do not duplicate here. Record pass/fail per rule by setting `cross_refs[N].done` in the stage's JSON checklist.

Source: `~/.skills/pragmatic-programmer/SKILL.md` (prefix `PP-`), `~/.skills/clean-architecture/SKILL.md` (prefix `CA-`), `~/.skills/implementation-coding-core/SKILL.md` (prefix `IC-`), `~/.skills/test-driven-development/SKILL.md` (prefix `TDD-`), `~/.skills/cs-foundations/SKILL.md` (prefix `CS-`)

### Stages 1-2 (Requirements)
- PP-REQ-1, PP-REQ-2, PP-REQ-3, PP-REQ-4 (discover with users, feedback loops, policy as metadata, glossary)
- PP-APPROACH-4 (keep options reversible — don't lock in HOW decisions)

### Stage 3 (Research)
- PP-APPROACH-1 (tracer bullets — thin end-to-end when surveying unknowns)
- PP-APPROACH-2 (prototypes to learn — disposable explorations before committing)

### Stage 4 (Decomposition)
- **CS-SEP-1 through CS-SEP-5** (full pass — read/write split, command/query, layers, bounded contexts, API surface)
- **CS-DATA-1 through CS-DATA-6** (full pass — ownership, state model, storage, schema, lifecycle, derived data)
- **CS-COMM-1 through CS-COMM-5** (full pass — sync/async, integrations, events, API style, serialization)
- **CS-CONSIST-1 through CS-CONSIST-5** (full pass — consistency model, transactions, concurrency, idempotency, ordering)
- **CS-SCALE-1 through CS-SCALE-5** (full pass — load, hot path, caching, Big-O, resource bounds)
- **CS-SEC-1 through CS-SEC-5** (full pass — trust boundaries, authn, authz, secrets, input validation)
- **CS-ERR-1 through CS-ERR-5** (full pass — failure taxonomy, retry, partial failure, degradation, observability)
- PP-ORTH-1, PP-ORTH-3 (decomposed specs are self-contained, changes don't ripple)
- PP-DRY-1 (no duplicated knowledge across spec units)
- CA-COMP-1 (no cycles in dependency graph)
- CA-COMP-4, CA-COMP-5 (classes that change together / are used together belong in same component)

### Stage 5 (Spec Tree)
- CA-SCRM-1, CA-SCRM-2 (tree communicates use cases, stranger understands domain from `tree`)
- PP-CRAFT-5 (names reveal intent)

### Stage 6 (Specifications)
- CS-* spot check (verify specs are consistent with Stage 4 decisions — new questions are findings)
- PP-CONTRACT-1 (preconditions, postconditions, invariants defined)
- PP-REQ-3 (policy is metadata — specs don't hardcode business rules)
- PP-REQ-4 (glossary — terms consistent across specs)
- TDD-COV-1, TDD-COV-2, TDD-COV-3 (contracts cover happy path, edge cases, error cases)
- CA-BOUND-3 (data crossing boundaries is simple structures)

### Stage 7 (Scaffolding)
- CS-* verify scaffold embodies Stage 4 decisions (event types exist if async, separate read/write models if CQRS, etc.)
- PP-APPROACH-3 (no broken windows — fix bad naming/structure immediately)
- PP-DRY-1, PP-DRY-2 (single source of truth, no inter-developer duplication)
- PP-ORTH-1 (components self-contained)
- IC-LAY-1, IC-LAY-2, IC-LAY-3 (layering discipline — structure before headers before signatures)
- IC-HDR-1 through IC-HDR-5 (every file has PURPOSE, RESPONSIBILITIES, NOT RESPONSIBLE FOR, DEPENDENCIES; headers permanent)
- CA-DEP-1, CA-DEP-2, CA-DEP-5 (dependencies inward, entities clean, DIP at boundaries)

### Stage 8 (Implementation)
- PP-CRAFT-1 (no programming by coincidence)
- PP-CRAFT-2 (Big-O considered)
- PP-CRAFT-3 (refactor on duplication or non-orthogonality)
- PP-CRAFT-4 (test-first drives design)
- PP-CRAFT-6 (small steps, check feedback)
- PP-CONTRACT-2 (crash early)
- PP-CONTRACT-3 (assertions for impossible conditions)
- PP-CONTRACT-4 (finish what you start)
- PP-DECOUPLE-1 through PP-DECOUPLE-5 (no train wrecks, Tell Don't Ask, Demeter, interfaces over inheritance, config externalized)
- TDD-CYC-1 through TDD-CYC-6 (full Red-Green-Refactor cycle)
- IC-SCALE-1 through IC-SCALE-4 (10x/100x/1000x, timeouts, streaming, assumptions documented)
- IC-DATA-1 through IC-DATA-5 (schema validation at boundaries)

### Stage 8b (Reconciliation)
- PP-DELIVER-4 (find bugs once — every bug gets a test)
- PP-DRY-2 (no inter-developer duplication across implemented specs)
- PP-ORTH-3 (change to one module doesn't ripple)
- IC-VER-1 through IC-VER-4 (compiles, imports correct, tests pass, verified before declaring done)
- TDD-QUAL-1 (tests verify behavior not implementation)

### Stage 9 (Verify)
- PP-DELIVER-1 (version control drives builds/tests/releases)
- PP-DELIVER-2 (no manual procedures)
- PP-DELIVER-3 (not done until all tests pass)
- PP-DELIVER-5 (state coverage, not just code coverage)
- CA-TEST-1, CA-TEST-2 (behavior not implementation, structured by use case)
- TDD-BUG-1 through TDD-BUG-4 (bug fix protocol — reproduce, confirm, fix, full suite)

## Iteration Lifecycle

Each pass through the DAG produces a complete snapshot:

```
.planning/
├── raw/REQUIREMENTS-RAW.md          # immutable
├── v1/
│   ├── checklists/                  # JSON runtime state — agents read/write these
│   │   ├── dag-progress.json        # combined view of all stages
│   │   ├── stage-01-raw-requirements.json
│   │   ├── stage-02-clean-requirements.json
│   │   └── ...                      # one per stage through 09
│   ├── dag.md                       # DAG definition for this iteration
│   ├── upstream-feedback.md         # findings from this iteration
│   ├── clean-requirements.md
│   ├── decomposition.md
│   └── spec-tree/
├── v2/
│   ├── checklists/                  # fresh copy from templates/json/
│   ├── dag.md                       # may differ from v1
│   ├── upstream-feedback.md         # includes v1 findings + new
│   └── ...
```

- Complete `upstream-feedback.md` before tagging an iteration closed. Classify and write back all verify fix log entries.
- To start v(N+1): read raw requirements + all `upstream-feedback.md` files. Re-derive clean requirements and decomposition fresh. The DAG itself may evolve.
- **Delta vs full regeneration gate (Stages 3, 6, 7, 8).** At each fan-out stage, present the user with a choice before proceeding:
  1. **Full regeneration** — re-derive all artifacts from upstream inputs. Use when upstream changes are pervasive or when prior iteration had systemic issues.
  2. **Delta-only** — identify which specs/artifacts are affected by upstream feedback, regenerate only those, carry forward unaffected artifacts with a reconciliation check. Use when changes are localized and prior iteration was mostly sound.
  The coordinator must present: (a) which specs are affected by upstream findings, (b) which are unchanged, (c) estimated cost of full vs delta. User decides. Record the decision in `upstream-feedback.md`.
- Surgical iterations: when the codebase is stable and the addition is orthogonal, a single-spec streamlined path is permitted — no full fan-out required.

## Audit Variant

The DAG can be run as a retrospective audit against an existing codebase. Stage mapping:

- **Stages 1-2 (Raw/Clean):** Define audit scope — which skill checklists, which codebase areas, what deliverables. Raw requirements describe the audit objective, not a feature to build.

  | # | Step | Executor |
  |---|------|----------|
  | items[0] | Define audit scope and objectives | Lead agent |
  | gates[0] | User approves audit scope | User |

- **Stage 3 (Research):** Survey the existing codebase. Discover actual patterns, conventions, test coverage, and architecture. Record what exists, not what should exist.

  | # | Step | Executor |
  |---|------|----------|
  | items[0] | Survey codebase per area | Explore agents (Sonnet, parallel — one per area) |
  | items[1] | Assemble findings | Lead agent |
  | gates[0] | User reviews survey findings | User |

- **Stage 4 (Decomposition):** Decompose into audit specs — one broad sweep (Pass 1) plus domain-specific deep dives (Pass 2). Each spec lists: scope (files), skills (rule IDs), audit procedure, expected findings from research.

  | # | Step | Executor |
  |---|------|----------|
  | items[0] | Decompose into audit specs (broad + deep) | Lead agent |
  | gates[0] | User approves audit decomposition | User |

- **Stages 5-6 (Spec Tree/Specs):** Write audit spec files with step-by-step audit procedures, not behavioral specifications. Each spec is self-contained — an auditor agent reads only its spec file.

  | # | Step | Executor |
  |---|------|----------|
  | items[0] | Create spec tree | Lead agent |
  | items[1] | Write audit specs with procedures | Sonnet agents if volume warrants, else lead |
  | gates[0] | User approves audit specs | User |

- **Stage 7 (Scaffold):** Skipped. There is no scaffold for an audit.

- **Stage 8 (Implementation → Audit Execution):** Pass 1: one agent scans entire codebase against all rules, produces triage. Pass 2: one agent per domain spec, reads triage + its spec, produces filled checklist + findings + strengths. Stage 8b: cross-domain reconciliation — dedup, consistent severity, boundary health.

  | # | Step | Executor |
  |---|------|----------|
  | items[0] | Pass 1: broad sweep against all rules | Opus agent (single, needs judgment) |
  | items[1] | Pass 2: deep dive per domain spec | Sonnet agents (fan-out, one per spec) |
  | items[2] | Stage 8b: cross-domain reconciliation | Sonnet agent (single) |
  | gates[0] | User reviews audit findings | User |

- **Stage 9 (Verify → Backlog Ingestion):** Verify findings are actionable. Ingest into project backlog system. Record upstream feedback. Produce: consolidated findings, remediation backlog (prioritized), strengths report.

  | # | Step | Executor |
  |---|------|----------|
  | items[0] | Verify findings are actionable | Lead agent |
  | items[1] | Ingest into backlog system | Lead agent |
  | items[2] | Produce consolidated report + remediation backlog | Lead agent |
  | gates[0] | User approves final audit report | User |

Audit does not modify source code. All output goes to `.planning/v<N>/audit-results/`.
