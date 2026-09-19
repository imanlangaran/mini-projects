# Usability-pass pending — Phase 2 package handoff (Gate-2 pre-condition)

> **Project:** School Driver Platform — **Phase 2 — UX & Prototyping**
> **Document type:** dispatcher's handoff record. Records what the Phase-2 package
> covers, the new UX open questions surfaced, and the exact steps the dispatcher
> (an independent context) must take to run the `usability-pass` procedure.
> **NOT a verification.** The author of this package **cannot** run the pass
> (governance Rule 7: author ≠ verifier). This file exists so the dispatcher and
> the Product Owner know precisely what exists, what is still open, and how to run
> the pass in a fresh context.
> **Status:** package authored (2026-08-31, completed/validated 2026-09-05). **Pass v1
> run** (2026-09-05 — 16 findings, see `usability-pass-report-v1.md`). **Author-fix pass
> applied** (all findings + PO rulings UX-OQ-25/26). **Re-pass v2 ran 2026-09-05:
> CLEAN — 0 findings** (`usability-pass-report-v2.md`). **Gate 2 signed by the PO
> 2026-09-05** — see `gate2-packet.md`; this handoff is retained as the historical
> dispatch record.

---

## 1. What the package covers (author's dispatch)

All under `docs/ux/`:

| Artifact | Purpose | Story / AC coverage |
|---|---|---|
| `flows.md` | Named flows per Must story (happy path first), AC walkthrough annotations, edge/empty/failure cases, OQ surfacings | US-01…05, US-07…09 (all Must) + US-06 sketch (Should) |
| `ux-findings.md` | **Author-side** per-AC walkthrough tables (self-check only — not the pass) | every AC of every Must story |
| `wireframes.html` | Clickable low-fi RTL prototype, screens **S1–S17** (login, admin home + parents-request queue, schools + **school edit S16**, students + **edit → S5 (stored sex, UX-OQ-26)**, **driver registry S6**, driver record, matching, **report S9: paginated assignments + drill-down, flagged/excluded in both views (UX-OQ-25)**, failure, approve, parent, parent account, driver roster, tweak, **parent-request accept/reject S17**) | all key screens implied by the flows |
| `skill-setup.md` | Step 1 record (verified, not redone) | — |
| `usability-pass-prompt.md` | The procedure the dispatcher uses | — |
| `phase2-package-summary.md` | Finish-line summary | — |

### Story coverage summary (Must set = US-01,02,03,04,05,07,08,09)

| Story | Priority | Happy path | Failure/edge path | Screens |
|---|---|---|---|---|
| US-01 Register school | Must | yes | validation (AC-2/5/6), post-edit (AC-4) | S3 |
| US-02 Register student | Must | yes | validation (AC-2/3/5/6), school-change re-validate (AC-4) | S4, S5 |
| US-03 Register driver | Must | yes | validation (AC-2/6/9/10/11/13/14), capacity guard (AC-7), post-pub identity (AC-8) | S6, S7 |
| US-04 Run matching | Must | yes | infeasible (AC-6), turnaround (AC-7), degenerate (AC-8), gender/area/selection shortfalls (AC-9/10/11) | S8, S9, S10 |
| US-05 Review & publish | Must | yes | pre-approval gate (AC-2), failure block (AC-4), staleness block (AC-5) | S9, S11 |
| US-07 Driver roster | Must | yes | per-direction only (AC-3), empty state (AC-4) | S14 |
| US-08 Parent view | Must | yes | not-published (AC-3), account states (AC-5/6/7) | S12, S13 |
| US-09 Flag student | Must | yes | unflag (AC-3), flag→re-run failure-resolution (AC-4, CR-18/CR-19) | S4, S10 |
| US-06 Tweak (Should) | Should | primary flow sketched | direction-scope per D-48 | S15 |

Cross-cutting: NFR-04 access control (role-separated screens), NFR-06 accessibility
(keyboard-focus + AA text in the prototype), NFR-07 Farsi RTL (`dir="rtl"`
throughout), NFR-01 multi-hour run UX (flagged, UX-OQ-24), NFR-02/03/05 noted as
Phase-3/6 meters, NFR-09 error messaging (inline field errors, no partial state).

---

## 2. New UX open questions surfaced (sequential IDs, never reused)

Surfaced on top of the locked baseline's open set (OQ-10…13, OQ-15 must be answered
by the **Product Owner** only; OQ-17 is post-MVP). **None of these are answered by
this package** — they are recorded, not invented.

| ID | Open question | Why it arose | Blocks Gate 2? |
|---|---|---|---|
| **UX-OQ-22** | What is on the **admin home** (S2) after login? Baseline defines no admin-home content. | Every admin flow starts at S2; content is undecided — a "how does the user do X?" gap | No (proposal exists) — PO to confirm/answer |
| **UX-OQ-23** | How do **drivers receive credentials**? (A-11 provisions accounts; OQ-12 covers parent credentials only.) | US-07 entry | No — may fold into OQ-12 |
| **UX-OQ-24** | **Multi-hour run UX** (NFR-01, D-22): non-blocking status vs modal; may the admin navigate away; re-trigger while one is in flight; older-report handling (adjacent OQ-10). | S8 shape for an overnight run | No, but **needed before Phase 3** |

These were first proposed in the prior session's draft as UX-OQ-22…24 and are
re-affirmed here. The Product Owner confirms/answers them; until then they remain
open (and re-appear in the independent pass as OQ surfacings).

### PO rulings on blocker UX-OQs (2026-09-05)

- **UX-OQ-25 — Report layout (S9) — ANSWERED (Product Owner, 2026-09-05):**
  paginated + drill-down is acceptable as "visible for review" per US-05 AC-1
  (paginated list of all assignments with drill-down to an individual
  assignment); **flagged/excluded students are marked in BOTH the summary and
  the drill-down views.**
- **UX-OQ-26 — Student-sex representation (S5) — ANSWERED (Product Owner,
  2026-09-05): the student's sex is stored-and-validated (D-30), independent of
  the school selection; **S5 must present the AC-4 sex-mismatch rejection with
  the mismatch message** when the school is changed and the stored sex differs
  from the new school's sex.

Both rulings are binding for the author-fix pass; the package author applies
them to `wireframes.html` (S9 pagination/drill-down + flagged markers in both
views; S5 sex field stored-and-validated with rejection) and `flows.md` /
`ux-findings.md` accordingly. The remaining UX-OQs (22…24) and the baseline
OQ-10…13/15 stay **open — PO only**, as recorded above.

### PO rulings on gating baseline OQs (2026-09-05)

- **OQ-10 — Re-run vs published plan / tweak survival — ANSWERED (PO,
  2026-09-05): "Re-run supersedes; tweaks re-applied or lost."** Interpretation
  recorded for sign-off: a new matching run **supersedes** the previous plan
  (the old plan stops being the published one); prior US-06 tweaks are **not
  automatically carried** into the re-run's plan — the admin may re-apply
  tweaks manually afterwards (US-06) for any assignment still valid under the
  new plan. UX disposition: the trigger screen (S8) shows a **warning before an
  in-flight re-run** that the current published plan (incl. tweaks) will be
  superseded.
- **OQ-11 — Mid-year flag/removal propagation — ANSWERED (PO, 2026-09-05):
  "Propagate immediately."** Flagging/removing a student mid-year updates live
  rosters and parent views immediately (S4 flag + S12/S14 update inline);
  matching itself is not re-run (CR-16/D-23 unchanged).
- **OQ-12 — Driver identity to parents + credential delivery — ANSWERED (PO,
  2026-09-05): driver name, car model, plate number, driver's phone number.**
  Extends D-15/CR-03 identity set with driver name + phone; parent view S12
  shows these. (Credential *delivery* mechanics remain UX-OQ-23, non-blocking.)
- **OQ-13 — Identifiers & duplicates — ANSWERED (PO, 2026-09-05):** **national
  ID (کد ملی) approved as the unique student key** — 10-digit, format-validated,
  unique across the registry; used for registry, reassignment, flagging, and
  parent↔student linkage (A-10); school student number is a display reference
  only. Duplicates: student = same کد ملی; school = same name + coordinates
  (D-26); driver = same plate **or** same کد ملی — each rejected with a message
  naming the existing record (NFR-09). Reassignment/flag/export key off کد ملی
  (stable across school changes — keeps US-02 AC-4 re-validation sound).
- **OQ-15 — Student-registration initiation — ANSWERED (PO, 2026-09-05):
  "Parent."** The parent initiates student registration; a registration request
  becomes a student record when the administrator/school accepts it (mirrors
  CR-20's parent-request pattern; S17-style queue). Implication: S4/S13 flows
  get a parent-initiated branch; authorized admin acceptance moves it into the
  registry.

All five are recorded **PO-side answers to baseline OQs** — they bind the UX
package now (flows/screens updated per above) and enter the **formal baseline
amendment queue** (`discovery.md` §5 → resolved; ripple sweep) for the
Requirements owner, per the amendment protocol. Locked files are not touched
here.

**Author-fix pass status (2026-09-05):** both rulings have been **applied author-side**
(F1–F16 all addressed — see `phase2-package-summary.md` §6). **Re-pass (v2) is the
dispatcher's next step**; it must run in a fresh context per §3 and its report is saved
as `usability-pass-report-v2.md` (sequential, never overwrite v1).

---

## 3. Steps to run the independent usability pass (dispatcher instructions)

The pass must be run by a **fresh agent context that did not author/edit** this
package (any isolation — a spawned session, a separate profile, or a
`delegate_task` subagent — that guarantees a clean context). This session's profile
(`ux-design`) has `skills` and `delegation` disabled, so it **cannot** spawn the
verifier; the Product Owner must dispatch it.

1. **Dispatch:** open a fresh agent session in this repo and direct it to read
   `docs/ux/usability-pass-prompt.md`. That file's "Verifier instructions" section
   is the pass. Tell the verifier the procedure name is **`usability-pass`** and
   give it ONLY: the project root path, the prompt file path, and the locked-baseline
   paths below. Do **not** summarize the package for the verifier — it must read the
   artifacts itself.
2. **Inputs the verifier must read (in order):**
   - governance role: `plans/2026-08-04_110131-agent-workflow-gov.md` §3.7
   - locked baseline: `test-user-story-schooldriver/docs/requirements.md` (v1.0)
   - locked discovery: `test-user-story-schooldriver/docs/requirements/discovery.md` (v1.0)
   - package under review: `test-user-story-schooldriver/docs/ux/`
3. **Verifier output:** a findings report with per-story verdict (PASS/FINDINGS),
   overall verdict (CLEAN / FINDINGS + severity), and any new UX-OQ proposals.
   The verifier reviews only — it never edits.
4. **Save the report** as `docs/ux/usability-pass-report-v1.md` (v1, v2, … sequential,
   never overwrite).
5. **If findings exist:** the author (this package's author role) fixes them in
   `flows.md` / `wireframes.html` / `ux-findings.md`, then the Product Owner decides
   whether a re-pass is needed. Repeat until clean or the PO accepts residuals.
6. **Never report the pass as clean** unless an independent verifier report says so.

> **Gate-2 exit criterion (lifecycle v2):** every Must story has an approved flow +
> screen and no open "how does the user do X?" questions. This is reached only after
> the independent pass reports and the **Product Owner** signs off. OQ-10…13/15 must
> be answered by the PO before Gate-2 exit — this package does not resolve them.

---

## 4. Author-side claims for the verifier to *challenge* (not trust)

- All Must-story ACs are satisfiable in the designed screens (author-side walkthrough
  in `ux-findings.md` — **self-check, not an approval**).
- No blockers/majors found by the author; 3 minors noted (S8 in-flight re-trigger,
  D-27 block-message state-dependency, S10 cause-tag data model) + the 3 UX-OQs.
- Design choices made **within** the baseline (flagged for the pass to challenge):
  inline resolve-actions on S10, per-driver-per-school report grouping on S9,
  published-state gate on S12/S14, derived-window display on S6.
- Accessibility basics (NFR-06) and RTL (NFR-07) are baked into the prototype's CSS/
  markup (`dir="rtl"`, `:focus-visible`, Farsi labels, AA contrast). The verifier
  should confirm these hold; the NFRs themselves are not re-litigated.

---
*End of handoff. Dispatch the pass per §3; record its report as `usability-pass-report-vN.md`.*