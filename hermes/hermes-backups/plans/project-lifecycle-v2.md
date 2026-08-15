# Software Project Lifecycle with Hermes — From Idea to Deploy (v2)

> **Purpose:** The complete, repeatable flow for taking a project from a raw idea to a deployed, monitored product — using Hermes as the engineer/PM/ops throughout, and software project standards at every gate.

**Goal:** One defined pipeline (idea → deploy → iterate) that works for any project, with clear phases, artifacts, standards, and the exact Hermes tooling for each step.

**How to run it:** Each phase has entry criteria → activities → artifacts → exit criteria (the phase's Definition of Done) → a gate. The user makes product decisions; Hermes does the mechanics and produces the artifacts. Every artifact lives in the repo (docs-as-code) so nothing lives only in chat.

**It is NOT one session.** The flow is the *process*; sessions are just work units. Any phase can be executed by parallel subagents, independent Hermes instances, kanban workers, or scheduled cron jobs — see **Orchestration** below. Continuity comes from artifacts (plan files, repo, AGENTS.md, skills, memory), never from keeping one session alive.

**v2 changes:** inserted **Phase 2 — UX & Prototyping** (the biggest gap in v1: the flow jumped from user stories straight to architecture, silently assuming the UX was decided). Added **three explicit cross-cutting gates — Security, Budget, Documentation** — so what v1 left implicit now has a checklist and a gate. Renumbered all phases.

**2026-08-10 — Phase 1 (Requirements) extended** with the structured User Story Session: product intent → discovery session → capture (confirmed / assumptions / decisions / open questions) → user stories → independent review (Requirements Reviewer) → human approval → approved baseline; Gate 1 now *Requirements baseline approved + Scope locked + Budget approved*. Roles/rules live in the governance spec (`2026-08-04_110131-agent-workflow-gov.md`, §3.6 + Rule 7).

---

## Phase 0 — Idea & Discovery

**Standard:** Lean Canvas / one-pager, product discovery
**Entry:** A vague idea ("I want an app that…")

**Activities:**
1. Write the one-pager: problem, target user, value proposition, success metric, constraints, why now.
2. Recon: who else solved this, how, and what's missing (web research).
3. Feasibility spike: throwaway experiment to validate the riskiest assumption (auth? API? algorithm?).
4. Rough effort/cost estimate (see **Budget gate**).
5. Go/no-go decision on the one-pager.

**Hermes tooling:** chat session (idea capture), `spike` skill (throwaway validation), web research, `session_search` (prior context).

**Artifacts:** `docs/idea.md` (or `ONE-PAGER.md`)

**Exit criteria:** 1-page problem statement + 1 measurable success metric; go/no-go recorded.

**Gate 0:** *Go / No-Go*

---

## Phase 1 — Requirements

**Standard:** Agile user stories + acceptance criteria, MoSCoW prioritization, IEEE 830 NFRs
**Entry:** Approved one-pager

**Activities:**
1. **Product intent / initial input** — the human provides the initial product idea, goal, or feature request; it need not be fully specified.
2. **Requirements discovery session** — the Requirements agent facilitates a structured conversation with the human, asking targeted questions to uncover actors/users, user goals, workflows, business rules, constraints, edge cases, and expected outcomes. The agent must not silently invent requirements — missing or ambiguous information is explicitly identified.
3. **Capture requirements** — persist the discovered information as structured artifacts, separating **confirmed requirements**, **assumptions**, **decisions**, and **unresolved/open questions**. The conversation itself is not the source of truth; the artifacts are.
4. **User story creation** — convert the confirmed requirements into user stories: actor, desired capability, reason/value, acceptance criteria (Given / When / Then). Stories are appropriately scoped and independently understandable.
5. **User story review** — an independent review responsibility (the Requirements Reviewer role; governance spec §3.6) challenges the complete package — stories, acceptance criteria, assumptions, decisions, open questions, captured requirements — for ambiguity, missing requirements, hidden assumptions, incorrect scope, oversized stories, non-testable acceptance criteria, missing edge cases, duplication/overlap, and implementation details stated as requirements. Findings feed an internal revision loop until the package is clean; findings and revisions are recorded.
6. **Human review and approval** — present the final pre-approval packet (requirements, stories, assumptions, decisions, open questions, and the recorded review findings) to the human. The human is the final authority for product requirements; no architecture or implementation planning proceeds until approval. If the human requests changes, revise the artifacts and repeat the review.
7. **Requirements baseline** — after approval, the requirements/user stories become the approved baseline that later phases consume: Architect scope (Phase 3), Milestone Planner backlog (Phase 4), SDD feature specs (Rule 6).
8. MoSCoW: Must / Should / Could / Won't — locks the MVP scope.
9. Non-functional requirements: performance, security, availability, budget — **including accessibility & localization** (folded in here, verified in QA).

> **Principle:** this phase is requirements discovery and validation, not implementation planning — no framework/library choices, database schema, API implementation, folder structure, infrastructure, or implementation-task decisions here (governance spec Rule 7). Those belong to Phase 3+.

**Hermes tooling:** discovery session + story drafting in chat; storage in `docs/requirements.md` + `docs/requirements/discovery.md` (or `notion` / `airtable` / `obsidian` skills if you prefer external tools).

**Artifacts:** `docs/requirements.md` (confirmed requirements + approved baseline), `docs/requirements/discovery.md` (assumptions, decisions, open questions), story-review findings, prioritized backlog

**Exit criteria:** MVP scope locked; every **Must** story has acceptance criteria; NFRs written down; discovery complete with no open questions blocking scope; **human approved the requirements baseline**; **budget approved** (Budget gate).

**Gate 1:** *Requirements baseline approved + Scope locked + Budget approved*

---

## Phase 2 — UX & Prototyping

**Standard:** UX research, user flows, wireframing, usability testing
**Entry:** Locked requirements (what the product must do)

**Activities:**
1. User flows for each **Must** story — the happy path first.
2. Wireframes / clickable prototype (low-fi is fine; even a sketch beats nothing).
3. Cheap usability pass: walk the flows against the acceptance criteria — does the design actually let a user complete them?
4. Sign off the screens before any architecture is locked around them.

> **Why this phase exists:** v1 jumped from requirements straight to tech architecture, silently assuming the UX was already decided. UX is where most projects die — and changing it after the data model and API are built is expensive. A sketch before Phase 3 pays for itself. Even solo: one page of screens.

**Hermes tooling:** `sketch` / `claude-design` skills (HTML mockups), `excalidraw` (hand-drawn style diagrams), `p5js` (interactive prototypes).

**Artifacts:** `docs/ux/flows.md`, wireframes/prototype (committed to repo)

**Exit criteria:** Every **Must** story has an approved flow + screen; no "how does the user do X?" open questions.

**Gate 2:** *UX approved*

---

## Phase 3 — Architecture & Design

**Standard:** ADRs (Architecture Decision Records), 12-Factor App, design-first APIs (OpenAPI)
**Entry:** Approved UX

**Activities:**
1. Tech stack decision with documented tradeoffs.
2. System design: components, data model, interfaces.
3. One ADR per significant decision — context, decision, alternatives, consequences.
4. API contract first (OpenAPI spec) so frontend/backend can be built in parallel.
5. **Threat modeling** — auth design, data classification, what happens if data leaks (Security gate).

**Hermes tooling:** `architecture-diagram` skill (infra/architecture SVGs), `excalidraw` skill, doc generation (`docx`), `notion`/`google-workspace` if used.

**Artifacts:** `docs/adr/0001-*.md` (one per decision), architecture diagram, OpenAPI spec, ERD

**Exit criteria:** No open "how will we…?" questions; architecture reviewed and committed; **security review passed** (Security gate).

**Gate 3:** *Design review passed + Security reviewed*

---

## Phase 4 — Project Planning & Scaffolding

**Standard:** WBS, milestones, Definition of Ready, GitHub Flow / trunk-based
**Entry:** Reviewed architecture

**Activities:**
1. Break scope into milestones: M0 setup → M1 core → M2 … → M-release.
2. Write the implementation plan: bite-sized tasks (2–5 min each), exact file paths, complete code, exact test commands, verification steps → saved under `.hermes/plans/`.
3. Scaffold the repo: `git init`, `AGENTS.md` (project conventions Hermes must follow in this repo), CI skeleton, folder structure.
4. Choose git workflow + conventional commits.
5. If team: assign roles / Definition of Ready per person (trivial for solo).

**Hermes tooling:** `plan` skill (plan documents), `github-repo-management` skill, `github-auth` skill, AGENTS.md conventions (see hermes-agent `project-context-files` reference).

**Artifacts:** one plan doc per milestone, `AGENTS.md`, initialized repo, CI skeleton

**Exit criteria:** Plan reviewed; first milestone meets Definition of Ready.

**Gate 4:** *Ready to build*

---

## Phase 5 — Implementation (the dev loop)

**Standard:** TDD, frequent commits, clean code, code review, CI on every PR
**Entry:** Approved plan

**Per task (the loop):**
1. Write the failing test → run → verify it FAILS.
2. Implement minimal code → run → verify it PASSES.
3. Refactor (DRY, YAGNI).
4. Commit with conventional message (`feat:`, `fix:`…).
5. Push → PR → CI runs → review → merge.

**Hermes tooling:**
- `test-driven-development` skill — enforces red/green/refactor
- `delegate_task` — parallel workstreams; subagent per task with spec-compliance + code-quality review after each
- `github-pr-workflow`, `requesting-code-review`, `github-code-review` skills
- Optional: `claude-code` / `codex` / `opencode` skills to offload coding to those CLIs

**Artifacts:** code, tests, PRs, CHANGELOG

**Exit criteria (Definition of Done):** All **Must** stories implemented; tests green; code reviewed; CI passing.

**Gate 5:** *Milestone done*

---

## Phase 6 — Testing & QA

**Standard:** Test pyramid (unit ≫ integration > e2e), CI gating, DoD verification
**Entry:** Feature-complete milestone

**Activities:**
1. Unit + integration tests in CI (required to merge).
2. E2E tests for the critical user journeys.
3. Exploratory QA: actively hunt for bugs in the running app.
4. Security scan: dependency audit (Dependabot), secret scanning, pre-commit review.
5. Accessibility & localization checks against the Phase-1 NFRs.

**Hermes tooling:** `dogfood` skill (exploratory QA of web apps — find bugs, evidence, reports), `requesting-code-review` skill (security scan + quality gates), CI workflows.

**Artifacts:** full test suite, green CI, QA report, audit results

**Exit criteria:** No open blockers; every story's acceptance criteria verified against the live app; **security audit passed** (Security gate).

**Gate 6:** *QA sign-off*

---

## Phase 7 — Release & Deployment

**Standard:** Semantic versioning, immutable artifacts, environment promotion (dev → staging → prod), zero-downtime deploy + rollback, secrets management
**Entry:** QA sign-off

**Activities:**
1. Build an immutable artifact (Docker image / compiled bundle).
2. CI/CD pipeline: build → test → tag (semver) → deploy.
3. Environments driven by env vars (12-Factor); secrets in the platform's vault — never in the repo.
4. Deploy to staging → smoke tests → promote to production.
5. **Documentation & handoff:** user docs, release notes, ops runbook (already started in Phase 8), onboarding notes if anyone else will touch it (Documentation gate).
6. **Data migration** (only if replacing an existing system): export/import, backfill, cutover, dual-run.
7. Write release notes; document and rehearse rollback.

**Hermes tooling:** `github-pr-workflow` (CI/CD automation), `hermes-railway-deployment` skill (concrete example: deploying a service on Railway), Docker.

**Artifacts:** CI/CD workflow files, `docs/deploy.md`, release tag (e.g. `v1.0.0`), rollback runbook, user docs

**Exit criteria:** App live in production; smoke tests pass; rollback proven once; **docs shipped with the release** (Documentation gate); **cost re-checked against the Phase-1 budget** (Budget gate).

**Gate 7:** *Shipped*

---

## Phase 8 — Operations & Monitoring

**Standard:** SRE — SLIs/SLOs, alerting, structured logging, incident response
**Entry:** Production deployment

**Activities:**
1. Health-check endpoint + uptime monitoring.
2. Structured logs, metrics, error tracking.
3. Alerts on thresholds (silent when healthy).
4. **Backups & disaster recovery** — backup schedule, restore drill, recovery runbook (folded in here explicitly).
5. Incident runbook; systematic debugging when things break.

**Hermes tooling:**
- `cronjob` tool with `no_agent=True` watchdog scripts — silent when healthy, alerts on threshold breach
- LLM-driven cron jobs — daily digest / anomaly briefings
- `systematic-debugging` skill (root-cause before fixing), `hermes-cli-ops` / gateway health checks

**Artifacts:** monitoring config, alert rules, runbooks, backup schedule + restore drill evidence

**Exit criteria:** Alerts live and tested; first incident drill done; restore drill done once.

---

## Phase 9 — Iterate & Retire

**Standard:** Agile feedback loops, retrospectives, roadmap
**Entry:** Running product + data

**Activities:**
1. Measure against the Phase-0 success metric.
2. Retrospective: what worked, what didn't (Hermes summarizes from session history).
3. Groom backlog → new stories → return to Phase 1/2 for the next iteration.
4. When the time comes: deprecation plan, data export, sunset.

**Hermes tooling:** `session_search` (history & lessons), cron-driven feedback collection, summary generation.

**Artifacts:** retro notes, updated roadmap, next-iteration backlog

---

## Governance & cross-cutting gates (cut across every phase)

**Version control & quality**
- Conventional commits, protected main, PRs only, CI green before merge.
- **Definition of Done:** tested → reviewed → merged → documented → deployed → monitored.
- Docs-as-code: every artifact lives in the repo (`docs/`), including ADRs and runbooks.
- Hermes project scaffolding: `AGENTS.md` in the repo tells every future Hermes session the project's conventions; save project-specific skills after first deploy (e.g. `myapp-deploy`) — that's how Hermes gets faster at *your* project.
- Environments: dev / staging / prod separation.

**Gate A — Security** (checklist at Gate 3 design review + Gate 6 QA sign-off)
- Threat model written and reviewed at design; auth & data-classification decisions recorded in ADRs.
- Secrets only in the platform vault, least privilege.
- Dependency + secret scanning green before release.
- Compliance (GDPR/PCI/…) — only if it applies; check it explicitly, don't assume.

**Gate B — Budget** (checklist at Gate 1 scope lock + Gate 7 release)
- Effort estimate + hosting/tools cost written down before Phase 3.
- Budget ceiling agreed; re-checked when scope changes and before paying for production.

**Gate C — Documentation** (checklist at Gate 7 release)
- User docs + release notes ship with the release.
- Ops runbook exists (updated through Phase 8).
- Onboarding notes exist if anyone else will touch the project.

**Security** (in brief): secrets only in vaults; least privilege; dependency + secret scanning. **Budget**: estimate before building, ceiling agreed, re-check at release. **Docs**: user docs, runbook, onboarding — shipped, not assumed.

---

## Orchestration — running the flow across sessions, agents & time

The flow is the *process*, not a session. Any phase can be executed by parallel subagents, independent Hermes instances, kanban workers, or scheduled cron jobs. Continuity comes from **artifacts** (plan files, repo, AGENTS.md, skills, memory), never from keeping one session alive.

| Hermes feature | What it does | Where it fits the flow |
|---|---|---|
| `delegate_task` (batch) | Up to N parallel subagents, each with isolated context + own terminal; results re-enter the session | Phase 0 research, Phase 5 independent tasks (backend ‖ frontend), Phase 6 QA sprints |
| Spawned `hermes` instances | Fully independent processes (`hermes chat -q`, tmux + `-w` worktrees), full tool access, hours/days | Long autonomous missions, e.g. "implement milestone M1" as its own agent while you work elsewhere |
| Kanban | Durable SQLite work queue; dispatcher spawns worker profiles that claim/complete tasks | Multi-agent Phase 5/6: a board of tasks, workers pick them up, blockers tracked on the board |
| Cron jobs | Durable scheduler: recurring, "every monday 9am", 5-field cron, or one-shot ISO timestamps; fresh session per run; delivers to Telegram | Nightly builds, scheduled deploys, daily QA digest, weekly retro prompt |
| Cron scripts / watchdogs | `no_agent=True`: the script IS the job; silent when healthy, alerts on threshold breach | Phase 8 uptime/API watchdogs, heartbeat checks, backup verification |
| `context_from` chaining | Job A's output feeds job B's prompt | Data-collection job → daily briefing job |
| Webhooks | Event-driven runs (GitHub push / PR merged → Hermes run) | Deploy-on-merge, auto PR summary, CI-failure triage |
| Profiles | Independent Hermes instances per project: isolated skills, memory, sessions, cron | One profile per project = the project's "home" |
| Skills + curator | Save project procedures (`myapp-deploy`); curator auto-maintains them | Every repeated action becomes a skill after first use |
| Memory | Durable facts about the project, injected into every session | Stack, deploy target, conventions, preferences |
| `session_search` / resume | Full-text search over all past sessions; `--continue` / `--resume <id>` | Phase 9 retro, "where did we leave X", picking up old work |
| Surfaces | Telegram, CLI, TUI, desktop app, web dashboard | Drive from Telegram; watch the dashboard; deep work in the CLI |

**A week in the life of the flow (all features, one project):**

- **Mon (Phase 5):** batch-delegate 3 subagents — auth module, data model, API endpoints. Each works in its own terminal; results merge back. PRs opened; `requesting-code-review` runs on each.
- **Tue:** kanban board for remaining tasks; worker profiles claim and complete them; blockers noted on the board.
- **Wed:** webhook fires on PR merge → Hermes auto-deploys to staging.
- **Thu (Phase 7/8):** watchdog cron checks the staging API every 4h — silent while healthy; a one-shot cron deploys to prod at 18:00 (Asia/Tehran).
- **Fri (Phase 9):** daily-digest cron (LLM job, `attach_to_session`) delivers the week's summary to Telegram; you reply and the conversation continues. `session_search` pulls the week's context for the retro.

**Limits to know (this deployment):**
- Delegation is **not durable** — subagents die with the parent process. Long-lived work → cron, spawned instances, or kanban.
- Batch delegation caps at **3 concurrent children**, nesting depth **1** (children can't spawn children). Bigger trees → kanban or independent instances.
- Cron runs get a **3-minute hard interrupt** per run — keep cron prompts narrow and scripted; heavy work belongs in spawned instances.

---

## Hermes capability map

| Phase | Standards applied | Hermes skills | Hermes tools |
|---|---|---|---|
| 0 Idea | Lean Canvas, spike | `spike` | chat, web research, session_search |
| 1 Requirements | User stories, MoSCoW, elicitation + review | `notion` / `airtable` / `obsidian` | doc generation |
| 2 UX | User flows, wireframes | `sketch`, `claude-design`, `excalidraw`, `p5js` | prototype generation |
| 3 Design | ADR, 12-Factor, OpenAPI | `architecture-diagram`, `excalidraw` | docx |
| 4 Planning | WBS, Definition of Ready | `plan`, `github-repo-management` | todo, AGENTS.md |
| 5 Build | TDD, code review, CI | `test-driven-development`, `github-pr-workflow`, `requesting-code-review`, `claude-code`/`codex`/`opencode` | delegate_task, terminal, git |
| 6 QA | Test pyramid, DoD | `dogfood`, `requesting-code-review` | CI, dependency audit |
| 7 Deploy | SemVer, promotion, rollback | `hermes-railway-deployment`, `github-pr-workflow` | Docker, CI/CD |
| 8 Operate | SLOs, alerting, IR | `systematic-debugging`, `hermes-cli-ops` | cronjob (watchdogs), health checks |
| 9 Iterate | Retro, roadmap | — | session_search, cron |

---

## Open questions to settle before running this on a real project

1. Which idea goes through the flow first? (Do you have one?)
2. Deploy target preference — Railway (like this Hermes), Docker/VPS, serverless?
3. Where do requirements/backlog live — repo markdown, Notion, Airtable, Obsidian?
4. Solo or team? (Affects code-review workflow and delegation depth.)
5. Does compliance apply (GDPR etc.)? If yes, it gets its own Security-gate checklist.
6. Greenfield or replacing an existing system? (Determines whether Phase 7 includes data migration.)
