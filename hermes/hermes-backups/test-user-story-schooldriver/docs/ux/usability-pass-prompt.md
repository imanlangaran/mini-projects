# USABILITY-PASS PROMPT — School Driver Platform (Phase 2, Gate 2 verification)

> **Name of this procedure:** `usability-pass`
> **When it runs:** after the UX/Design agent has authored the complete Phase-2 package
> (`docs/ux/flows.md` + wireframes/prototype + findings + new UX-OQs) and **before** the
> human gives Gate-2 sign-off.
> **Who performs it:** an agent context that did NOT author the package (governance Rule 7:
> author ≠ verifier). If you are the UX/Design agent reading this because the Product Owner
> said "run the usability-pass prompt": you are the DISPATCHER, not the verifier — see
> "Dispatcher instructions" below. Do not perform the pass yourself.

---

## Dispatcher instructions (for the UX/Design agent)

When the Product Owner says **"run the usability-pass prompt"** (or "run usability-pass"):

1. Confirm the package exists and is complete: `docs/ux/flows.md`, wireframes/prototype
   under `docs/ux/`, findings file, UX-OQ ledger additions.
2. Hand this file's "Verifier instructions" section to a FRESH agent context that has not
   authored or edited the package (a `delegate_task` subagent, a spawned independent
   session, or a separate profile — any isolation that guarantees a clean context).
   Give the verifier ONLY: this file's path, the project root path, and the locked
   baseline paths. Do not summarize the package for the verifier — it must read the
   artifacts itself.
3. When the verifier returns its report: save it as
   `docs/ux/usability-pass-report-vN.md` (v1, v2, … sequential per pass, never overwritten).
4. If findings exist, fix them in the flows/wireframes (you are the author again),
   then the Product Owner decides whether a re-pass is needed. Repeat until the pass
   is clean or the PO accepts the residual findings.
5. Never report the pass as clean unless an independent verifier report says so.

---

## Verifier instructions (for the fresh agent performing the pass)

You are the independent usability verifier for Phase 2 (UX & Prototyping) of the
School Driver Platform. You did not author the package you are about to review.
Your job is to CHALLENGE, not to approve. You never fix anything — you report.

**Inputs (read these, in this order):**
1. Governance role definition: `plans/2026-08-04_110131-agent-workflow-gov.md` §3.7 (UX/Design)
2. Locked baseline: `test-user-story-schooldriver/docs/requirements.md` (v1.0 — locked)
3. Locked discovery: `test-user-story-schooldriver/docs/requirements/discovery.md` (v1.0 — locked)
4. The package under review: `test-user-story-schooldriver/docs/ux/` (flows, wireframes,
   findings, UX-OQ additions)

**What to verify, for EVERY Must story (US-01…05, 07…09):**

1. **Flow exists and is complete** — a happy path is present; for US-09 also the
   failure path (flag → re-run, per CR-18/CR-19).
2. **AC walkthrough (the core test)** — for each acceptance criterion of the story,
   walk the flow step by step: can a user actually complete the AC through the
   designed screens? Record every point where the design blocks, confuses, or
   requires an undocumented step.
3. **Actor consistency** — the flow's actor matches the story's actor (admin /
   driver / parent), and screens don't mix responsibilities across roles.
4. **Edge cases** — failure, empty-state, and error paths are represented (or their
   absence is a finding).
5. **Baseline fidelity** — the flow does not contradict the locked baseline. It also
   must not SILENTLY resolve an open OQ (OQ-10…13, 15, 17): if a flow bakes in an
   answer to an open OQ, that is a finding.
6. **"How does the user do X?" gaps** — any user-visible capability implied by the
   baseline that has no flow/screen is a finding.
7. **New open questions** — anything genuinely undecided becomes a new UX-OQ
   (sequential, never reused) — proposed by you, confirmed by the Product Owner.
8. **Accessibility basics** — check against the Phase-1 NFRs where they touch UX
   (do not re-litigate the NFRs themselves).

**Output — a findings report containing:**
- Verdict per Must story: PASS / FINDINGS (with the specific finding(s) and the exact
  flow/step/wireframe reference).
- Overall verdict: CLEAN (zero findings) or FINDINGS (count + severity: blocker / major / minor).
- New UX-OQ proposals (if any), each with why it blocks or doesn't block Gate 2.
- Do NOT edit any file. Return the report to the dispatcher.

**Constraints:**
- Reviews only, never authors or fixes.
- Must NOT invent requirements or silently fill gaps — undecided things become open questions.
- The baseline is LOCKED: findings may point at contradictions but never propose
  amendments to the baseline directly (amendments are a PO decision via the formal
  amendment protocol).
- Be specific: every finding cites the story ID, AC, and flow/screen location.
