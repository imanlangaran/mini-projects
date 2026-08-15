# Agentic Development Workflow — Governance & Agent Spec

> **Purpose:** The working spec for an agent-driven software development workflow on a medium-to-large codebase (reference example: a Next.js application). This document defines the agent roles, the governance rules every agent must obey, and how those rules are communicated and enforced. It is the seed from which each agent will be created and its skills refined.
>
> **Relation to lifecycle:** Extends `project-lifecycle-v2.md`. Phases refer to the 10-phase flow in that doc (Phase 3 Architecture, Phase 4 Planning, Phase 5 Implementation, Phase 6 Testing & QA).
>
> **Updates:** 2026-08-04 — added Rule 6 (Spec-first / SDD) + spec-change path, named the Schema/Migration-owner role (§2), and added §8 ready-to-use `AGENTS.md` (the file that guides agents in every new session, under any profile).
>
> 2026-08-10 — Requirement Phase: added the structured User Story Session (discovery → capture → stories → independent review → human approval → approved baseline) as Rule 7; new **Requirements Reviewer** role (§2, §3.6) that independently challenges the complete package; lifecycle Phase 1 extended (see `project-lifecycle-v2.md`); SDD feature specs now derive from the approved baseline (Rule 6).

---

## 1. Reference example feature set

The example app decomposes into modules (discovered in Phase 3, ordered in Phase 4):

- Base application structure
- Dashboard layout
- Authentication
- User management
- Settings
- Notifications
- Other modules (added as discovered)

These must **not** be implemented simultaneously — they are introduced in a dependency-justified order (see §5).

---

## 2. Agent roles (who owns what)

| Agent / role | Lifecycle phase | Core responsibility |
|---|---|---|
| **Architect** | Phase 3 | Tech stack decisions (with tradeoffs), system design, OpenAPI contract, ERD, feature/dependency graph, ADRs |
| **Requirements (Product)** | Phase 1 | Facilitates the discovery session with the human, captures confirmed requirements / assumptions / decisions / open questions, writes user stories + acceptance criteria, applies MoSCoW → defines the **MVP**; stories are challenged by an independent reviewer before the human approves the baseline |
| **Requirements Reviewer** | Phase 1 | Independently challenges the complete requirements package (stories, acceptance criteria, assumptions, decisions, open questions, captured requirements) for inconsistency, missing info, hidden assumptions, unresolved requirements; findings feed the revision loop before human approval |
| **Milestone Planner** | Phase 4 | Decompose work into milestones (M0→…→M-release), roadmap, prioritized backlog, per-milestone task plans |
| **Implementer** | Phase 5 | Build a feature on a feature branch (TDD), write code + tests, fix reported issues |
| **Testing / QA** | Phase 6 | Run the full test suite, verify acceptance criteria, report failures back to the implementer |
| **Schema/Migration owner** | Phase 3/5/8 | Sole authority over the database schema, migrations, and seed data; the ONLY role that may touch the database (rule 1) |
| **Product Owner (human, iman)** | all gates | Confirms MVP, approves each feature, reviews every PR |

The user (product owner) makes product decisions and is the final approval gate; agents do the mechanics and produce artifacts.

---

## 3. Agent profiles (detail per agent — to be made concrete when each agent is created)

Each agent profile has: responsibilities, required skills/knowledge, inputs, outputs, tools, constraints, collaboration. These fields are refined incrementally.

### 3.1 Architect
- **Responsibilities:** Recommend and justify the tech stack; produce component/data-model/interfaces; write one ADR per significant decision; produce the feature→dependency graph that drives build order.
- **Skills/knowledge:** system design, ADRs, 12-Factor, OpenAPI/design-first, infrastructure/dependency analysis.
- **Inputs:** Approved UX (Phase 2), locked requirements (Phase 1), budget ceiling.
- **Outputs:** `docs/adr/00XX-*.md`, `docs/architecture.md`, OpenAPI spec, ERD, feature/dependency graph.
- **Tools:** `architecture-diagram`, `excalidraw`, doc generation, `docx`/`notion`.
- **Constraints:** Must not change locked scope; tech stack changes require user confirmation (Gate 3).
- **Collaboration:** From — Requirements/PRODUCT (scope). To — Milestone Planner (dependency graph + stack constraints).

### 3.2 Requirements (Product)
- **Responsibilities:** Run the discovery session (structured conversation with the human: actors/users, user goals, workflows, business rules, constraints, edge cases, expected outcomes — never silently inventing requirements); capture the discovered information into structured artifacts; write user stories + acceptance criteria; apply MoSCoW → define the MVP (Must set); present the final pre-approval packet (requirements, stories, assumptions, decisions, open questions, review findings) to the human; after approval, mark the approved requirements baseline for downstream consumption.
- **Skills/knowledge:** Agile user stories, acceptance-criteria authoring, MoSCoW, NFRs (incl. a11y/l10n), requirements elicitation/interviewing, requirement-capture practice (separating confirmed requirements / assumptions / decisions / open questions), story decomposition.
- **Inputs:** Approved one-pager (Phase 0), the human's answers during the discovery session.
- **Outputs:** `docs/requirements.md` (confirmed requirements + approved baseline), `docs/requirements/discovery.md` (assumptions, decisions, open questions), prioritized backlog, MVP scope definition, story-review findings (from the reviewer).
- **Tools:** doc generation, notion/airtable/obsidian.
- **Constraints:** MVP is final only after user confirmation (Gate 1); must not silently invent requirements — missing or ambiguous information is explicitly identified and carried as open questions; must not decide framework/library choices, database schema, API implementation, folder structure, infrastructure, or implementation tasks (those belong to Phase 3+); the workflow must not proceed past Gate 1 without human approval of the baseline; must not review its own package — the Requirements Reviewer does that.
- **Collaboration:** From — Product Owner (input + confirmation). To — Requirements Reviewer (complete package for challenge review); Architect (approved scope), Milestone Planner (MoSCoW Must set).

### 3.3 Milestone Planner
- **Responsibilities:** Turn the architecture's dependency graph into an ordered milestone plan (M0→…→M-release), roadmap, prioritized backlog, per-milestone task plans.
- **Skills/knowledge:** WBS, milestone planning, dependency-aware sequencing, Definition of Ready/Done, backlog grooming.
- **Inputs:** Phase-1 MoSCoW backlog, Phase-3 dependency graph + OpenAPI + ERD, budget.
- **Outputs:** milestone plan, roadmap, implementation backlog, per-milestone plan docs (`.hermes/plans/`), Definition of Ready/Done per milestone.
- **Tools:** `plan`, `todo`, doc generation, kanban seeding, `github-repo-management`.
- **Constraints:** Cannot invent/drop features; ordering only; must order within locked scope/budget; cannot re-prioritize a Should into an early milestone.
- **Collaboration:** From — Architect (dependency graph) + Requirements (backlog) + Product Owner (order approval). To — Implementer (via kanban + plan docs) + Testing (DoD).

### 3.4 Implementer
- **Responsibilities:** Build one confirmed feature at a time (TDD), maintain clean code, fix issues reported by Testing, open PR only after the full suite passes.
- **Skills/knowledge:** TDD, feature/branch/commit conventions, the `test-before-pr-loop` skill.
- **Inputs:** Approved feature card (from kanban), acceptance criteria, task plan, AGENTS.md rules.
- **Outputs:** feature code + tests on a feature branch, PR (only after tests pass), fixes.
- **Tools:** terminal, git, `test-driven-development`, `github-pr-workflow`, `delegate_task` (for parallel modules).
- **Constraints:** MUST NOT touch the database directly; MUST NOT proceed on an unconfirmed feature; MUST NOT open a PR until the full suite passes; MUST NOT self-merge.
- **Collaboration:** From — Milestone Planner (what to build) + Testing (failure reports). To — Testing (feature to verify), then PR to Product Owner.

### 3.5 Testing / QA
- **Responsibilities:** Run the ENTIRE test suite against each feature branch; verify acceptance criteria; decide pass/fail; report failures with evidence.
- **Skills/knowledge:** test strategy (unit/integration/e2e), CI, acceptance-spec verification, exploratory QA (`dogfood`).
- **Inputs:** Feature branch (from Implementer), full test suite, acceptance criteria, NFRs.
- **Outputs:** test verdict (PASS gate → PR allowed / FAIL → report to Implementer), QA report.
- **Tools:** CI, `dogfood`, `requesting-code-review`, systematic debugging.
- **Constraints:** Must test the feature in its entirety; only Testing's PASS unblocks a PR; never fixes code itself (reports instead).
- **Collaboration:** From — Implementer (feature to verify). To — Implementer (failure report → fix → retest loop); verdict feeds the PR gate.

### 3.6 Requirements Reviewer
- **Responsibilities:** Independently review the COMPLETE requirements package — user stories, acceptance criteria, assumptions, decisions, open questions, captured requirements — before human approval. Challenge rather than approve: check for ambiguity, missing requirements, hidden assumptions, incorrect scope, stories that are too large, non-testable acceptance criteria, missing edge cases, duplicated or overlapping stories, inconsistencies between the captured requirements and the stories, and technical implementation details incorrectly appearing as requirements. Return findings to the Requirements agent for a revision loop; record findings and revisions so the human can inspect what was changed.
- **Skills/knowledge:** Requirements review/validation, story-quality review, edge-case analysis, consistency checking across requirement artifacts.
- **Inputs:** Complete requirements package from the Requirements agent (confirmed requirements, user stories, acceptance criteria, assumptions, decisions, open questions).
- **Outputs:** Review findings (issues + required changes) recorded as a review artifact; feeds the Requirements agent's revision loop before the human approval gate.
- **Tools:** doc generation, notion/airtable/obsidian.
- **Constraints:** Must NOT invent requirements or silently fill gaps — unresolved items stay open questions for the human; reviews only, never authors; must be performed independently from the Requirements agent (separation of responsibilities — the same agent must not validate its own work).
- **Collaboration:** From — Requirements (complete package). To — Requirements (review findings → revision loop, repeated until the package is clean).

---

## 4. Governance rules (the non-negotiables)

These 7 rules apply to ALL agents and are encoded in `AGENTS.md` + skills + mechanical gates.

1. **No database access by agents.**
   - No agent touches the database directly — no migrations, no schema edits, no raw/ad-hoc DB access.
   - Only the designated schema/migration owner manages migrations, and only via the migration mechanism.
   - Agents write code against the data-access layer (repositories/models) only.

2. **Every feature requires confirmation (Definition of Ready).**
   - A feature is not claimable/in-progress until the product owner has approved it and its acceptance criteria.
   - A feature with an unapproved acceptance-criteria checklist must not be implemented.

3. **Git branching & versioning strategy.**
   - GitHub Flow / trunk-based; `main` is protected and always releasable.
   - Branches: `feature/<issue-key>-<slug>`, `fix/<...>`, `release/vX.Y.Z`.
   - Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `chore:`…
   - Semantic Versioning; tags `vX.Y.Z`.
   - Merge to `main` only via an approved PR (gate 5).

4. **Test-before-PR loop (the QA gate).**
   - Implementer writes the feature + tests (TDD red → green → refactor) on the feature branch.
   - Testing agent then runs the FULL test suite against that branch.
     - ALL pass → the Implementer may open the pull request for the feature.
     - ANY fail → Testing reports the failing issue(s) to the Implementer; the Implementer fixes; the loop repeats (re-run tests → pass → then PR).
   - A PR must NEVER be opened against a feature whose full suite has not passed.

5. **Human review gate.**
   - The product owner reviews every pull request.
   - A PR merges ONLY after: full suite green + explicit product-owner approval.
   - Never self-merge; never merge an unapproved PR.

6. **Spec-first (SDD) — every feature is built from an approved spec.**
   - The spec is the source of truth for a feature: behavior, acceptance criteria (Given/When/Then), boundaries, non-goals. One feature per spec.
   - Spec authorship: Requirements agent writes the user-facing feature spec from the **approved requirements baseline** (story + acceptance criteria from Phase 1); the API half comes from the Architect's OpenAPI contract; the Milestone Planner packages the approved spec into the feature card (Definition of Ready = spec approved).
   - Tests are DERIVED from the spec: every acceptance criterion maps to ≥1 test case (traceability).
   - The Implementer builds TO the spec only; the Tester verifies AGAINST the spec; PRs reference the spec version they implement.
   - Full procedure: `specification-driven-development` skill.

7. **Requirements baseline — no silent invention, no premature implementation.**
   - The Requirements agent discovers requirements in a structured session with the human — it never silently invents or fills gaps. Missing or ambiguous information is explicitly identified and recorded as open questions.
   - Captured artifacts separate confirmed requirements, assumptions, decisions, and open questions. The conversation is not a source of truth; artifacts are.
   - The complete requirements package is challenged by the Requirements Reviewer (independent from the Requirements agent) before it goes to the human; the revision loop stays internal; the human sees only the final pre-approval packet plus the recorded review findings.
   - The human approves the requirements baseline (Gate 1) before any architecture or implementation planning begins. Later agents consume the approved baseline — they must not rediscover requirements independently.
   - The Requirements phase decides product requirements only — never framework/library choices, database schema, API implementation, folder structure, infrastructure, or implementation tasks. Those belong to later phases (Phase 3+).

**Spec change / amendment path (never bypass):**
1. Any proposed spec change (product owner, tester gap, implementer raise-back) is written as a spec revision.
2. The revision goes through product-owner approval — the same gate as the original feature.
3. Approved revision → tests updated → re-verify (full suite) → only then does implementation continue / a PR open.
   - No silent improvisation: an implementer who needs behavior the spec doesn't state must STOP and raise it back. Guessing is a violation.

**Global Definition of Done:** tested → reviewed → merged → documented → deployed → monitored. Never skip a gate to save time.

---

## 5. Implementation ordering (who decides, and how)

**Responsibility:** The **Milestone Planner** owns the ordering decision (Phase 4). The **Architect** discovers the dependencies (Phase 3). Ordering is a *dependency* decision, not a choice.

**Rules the Planner applies:**
1. Dependency-first — a module others depend on goes first.
2. Riskiest-assumption-early — among peers, build the one most likely to invalidate the design first.
3. Minimal vertical slice first — M0 = base + thinnest end-to-end slice (e.g., base + auth-login/session).
4. Then parallelize independent modules once their dependencies are merged.
5. Topological sort across layers: foundation → shared/identity → features → cross-cutting.

**Example (dependency-justified order):**
```
M0  Base application structure (Next.js scaffold, CI, AGENTS.md, routing skeleton)
M1  Authentication             (everything depends on identity; riskiest assumption)
M2  Dashboard layout           (dept: base + session)    ┐
M3  User management            (dept: auth)              ├─ parallel after auth lands
M4  Settings                   (dept: auth + user model) │
M5  Notifications              (dept: auth + settings)   ┘
```

**Artifacts produced:** feature/dependency graph (Architect, Phase 3) → milestone plan + roadmap + prioritized backlog + per-milestone task plan (Planner, Phase 4).

---

## 6. How the rules are communicated & enforced

Three layers — instructions alone are soft; rules must also be load-bearing.

1. **`AGENTS.md`** (repo root) — the standing rulebook every agent auto-reads (auto-injected into each session's system prompt). Encodes §4 verbatim as the compact rule set (ready-to-use copy: §8). Portable across agent tools AND across Hermes profiles — it is loaded from the repo's working directory on every session, so sessions started under any profile see the same rules. Keep < 20,000 chars; move deep procedure to skills.
2. **Skills** — procedural memory for *how* to execute: `test-before-pr-loop` (implementer↔tester handoff), `github-pr-workflow`, `requesting-code-review`, `test-driven-development`, plus project-specific ones (e.g., `myapp-schema` for DB owner). Loaded on demand.
3. **Mechanical enforcement — so rules can't be forgotten:**
   - DB rule → DB/migration tooling lives only in the schema-owner's profile toolset; absent from Implementer/Testing profiles.
   - Feature confirmation → kanban Definition of Ready: an unapproved feature card cannot be claimed.
   - Branching/versioning → protected `main` (no direct push), Conventional-Commits lint + SemVer tag check in CI on every PR.
   - Test-before-PR → CI required-test job gates the PR; block until test job passes.
   - Human review → required reviewers on `main`; only owner's approval + green CI allows merge.
   - Requirements baseline → Gate 1: human approval of the baseline blocks all downstream phases; review role is separated from the author role (Requirements Reviewer ≠ Requirements agent).

---

## 7. Open items (to refine when creating each agent / its skills)

- [ ] Choose the Hermes primitive for each role: `delegate_task` subagent vs dedicated **profile** vs **kanban worker** vs spawned `hermes` instance (durability implications differ; delegation is not durable).
- [ ] Author the `test-before-pr-loop` skill (exact test command, failure→report→fix→retest flow, PR-open condition).
- [ ] Author the initial `AGENTS.md` for the target repo with the §4 rules verbatim.
- [x] DB-owner role named (Schema/Migration owner, §2) — still to define: its tool-permission restriction and migration workflow.
- [x] Backlog/requirements location — default: repo markdown (`docs/requirements.md` + `docs/requirements/discovery.md`, Phase 1) vs Notion/Airtable/Obsidian (choose per project).
- [ ] Confirm compliance needs (GDPR etc.) → separate Security-gate checklist if any.
- [ ] Confirm deploy target (Railway / Docker/VPS / serverless) → Phase 7.
- [ ] When the project repo exists: drop the §8 `AGENTS.md` at its root; keep task-plan docs inside the project repo (committed), not only in `.hermes/plans/` (wiped on this host).
- [ ] Install the SDD + relevant skills into every profile you'll use (skills/memory are per-profile; `AGENTS.md` + plan docs are not).

---

## 8. Ready-to-use AGENTS.md (drop into the project repo root)

> Copy the block below as `AGENTS.md` at the root of the project repo. Every Hermes session started in that repo — under ANY profile — auto-loads it. If it ever diverges from §4, AGENTS.md is the operative rulebook for agents (this plan is the design; AGENTS.md is the law).

```markdown
# Project guidance — ALL agents MUST follow (auto-loaded in every session in this repo)

You are working inside an agent-driven project. Read this file first; it is the standing rulebook.
Work comes from approved feature cards and milestone task plans — never improvise scope.

## 1. How to know what to build (task clarity)
- Work items come from: (a) milestone task plans in this repo (`.hermes/plans/` or `docs/plans/`),
  (b) kanban feature cards, (c) `docs/` in this repo.
- A feature card is workable ONLY when it carries an approved spec + acceptance criteria
  (Definition of Ready). No spec = do not start; ask the product owner.
- Build exactly what the spec states. If the spec is missing something the code needs, STOP and
  raise it back — never silently improvise.
- Requirements come from the approved requirements baseline (Phase 1: `docs/requirements.md` +
  `docs/requirements/discovery.md`) — never rediscover or silently invent requirements; missing
  or ambiguous items are open questions for the product owner, not guesses. The Requirements
  phase decides product requirements only — no framework/library, schema, API, folder, or
  infrastructure decisions until the Architect (Phase 3).

## 2. Spec-first (SDD)
- The spec is the source of truth: behavior, acceptance criteria (Given/When/Then), boundaries, non-goals.
- Tests are derived from the spec: every acceptance criterion maps to ≥1 test case.
- Implementer builds TO the spec; Tester verifies AGAINST the spec; PRs reference the spec version.
- Spec changes require product-owner approval and re-enter the gates:
  update spec → update tests → re-verify full suite → only then continue/PR.

## 3. Database access
- No agent touches the database directly — no migrations, no schema edits, no raw/ad-hoc SQL.
- Only the schema/migration owner runs migrations, via the migration mechanism.
- Write code against the data-access layer (repositories/models) only.

## 4. Feature confirmation
- A feature is NOT claimable/in-progress until the product owner has approved it and its
  acceptance criteria. Never implement an unconfirmed feature.

## 5. Git branching & versioning
- GitHub Flow / trunk-based; `main` is protected and always releasable.
- Branches: `feature/<issue-key>-<slug>`, `fix/<...>`, `release/vX.Y.Z`.
- Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `chore:`.
- Semantic Versioning; tags `vX.Y.Z`; merge to `main` only via approved PR.

## 6. Test-before-PR loop
1. Implement the feature on its branch + write tests (TDD: red → green → refactor).
2. The TESTING agent runs the FULL test suite against the feature branch.
   - ALL pass → the Implementer may open the pull request for that feature.
   - ANY fail → the Testing agent reports the failing issue(s) to the Implementer;
     the Implementer fixes; the loop repeats until the suite passes.
3. A PR must NEVER be opened against a feature whose full suite has not passed.

## 7. Human review gate
- The product owner reviews every pull request.
- Merge ONLY after: full suite green + explicit product-owner approval.
- Never self-merge; never merge an unapproved PR.

## Non-negotiables
- Definition of Done: tested → reviewed → merged → documented → deployed → monitored.
- Never skip a gate to save time. If in doubt, ask the product owner.
```