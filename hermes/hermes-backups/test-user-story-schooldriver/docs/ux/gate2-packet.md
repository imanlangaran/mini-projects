# Gate-2 Sign-off Package — Phase 2 UX & Prototyping (School Driver Platform)

> **Gate:** Gate 2 — *UX approved* (lifecycle v2 Phase 2 exit)
> **Status:** **SIGNED — Gate 2 approved by the Product Owner (2026-09-05)** — package
> verified CLEAN by independent usability pass v2; all gating OQs answered by the PO.
> **Date:** 2026-09-05
> **Project root:** `test-user-story-schooldriver/`

---

## 1. What this gate approves

The Phase-2 UX package for the School Driver Platform: user flows for every
Must story, the low-fi clickable RTL prototype, and the recorded UX decisions /
open-question rulings. Phase 3 (Architecture) may begin against this approved
UX once the PO signs.

**Package under approval (all under `docs/ux/`):**
- `flows.md` — operations manual: named flows + local branches per story;
  US-06 sketch separately cased (Should, out of the Must set).
- `wireframes.html` — S1–S17 clickable Farsi RTL prototype (D-13/NFR-07), with
  both the reviews summary (S9) and per-case drill-down, flagged/excluded
  markers in both, school/student/driver edit screens, driver registry list,
  parent-request queue, and accessibility (NFR-06) and error handling (NFR-09)
  baked in.
- `ux-findings.md` — author-side per-AC walkthrough (self-check only).
- `phase2-package-summary.md` — coverage status + author-fix record §6.
- `usability-pass-pending.md` — OQ ledger incl. PO rulings (see §3).

## 2. Independent verification (Rule 7 — author ≠ verifier)

| Pass | Verdict | Report |
|---|---|---|
| v1 (independent) | **FINDINGS — 16 (1 blocker, 5 major, 10 minor)** | `usability-pass-report-v1.md` |
| v2 re-pass (independent, after author fixes) | **CLEAN — 0 findings (0/0/0)** | `usability-pass-report-v2.md` |

v2 re-walked **all 8 Must stories' ACs independently** (US-01…05, US-07…09):
**PASS** for every story; all 16 v1 findings verified RESOLVED with
file/screen evidence; no silent OQ resolution; no new UX-OQ proposed.

## 3. Open questions — status at this gate

### 3.1 Gating baseline OQs — ANSWERED (PO, 2026-09-05)

| ID | PO ruling |
|---|---|
| OQ-10 | **Re-run supersedes** the previous plan; US-06 tweaks are **not auto-carried** — admin may re-apply manually; S8 trigger shows a supersede-warning before an in-flight re-run |
| OQ-11 | Flag/removal propagates **immediately** to live rosters and parent views (no re-run; CR-16/D-23 unchanged) |
| OQ-12 | Parent sees **driver name, car model, plate number, driver's phone number** (extends D-15; S12) |
| OQ-15 | **Parent initiates** student registration; admin/school accepts the request into the registry (CR-20-style; S17 queue + S4 branch) |
| OQ-13 | **Suggestion proposed — PO to confirm** (see §3.2) |

### 3.2 OQ-13 — Identifiers & duplicates (explanation + suggestion)

**The question (IR-09/IR-18):** what stable identifier distinguishes students
(for registry, reassignment, flagging, parent↔student linkage)? And what makes
a school/student/driver a "duplicate registration"? Without a stable key,
the registry can't safely re-validate a student on school change (US-02 AC-4),
link parents to the right child (A-10), or reject double-registrations (NFR-09).

**Suggested ruling (PO to confirm / adjust):**
- **Students:** **national ID (کد ملی)** is the unique, immutable key —
  10 digits, format-validated, unique across the registry; used for registry,
  reassignment, flagging, and parent↔student linkage. School student number is
  captured as a display reference only. *(Note: in Iran کد ملی is issued at
  birth, so every student has one.)*
- **Duplicate student** = same کد ملی → reject with "already registered".
- **Schools:** duplicate = same **name + coordinates** (D-26 requires both)
  → reject naming the existing school.
- **Drivers:** **plate number unique** (D-15) + کد ملی unique;
  duplicate on either → reject naming the existing driver.
- **Reassignment/flag/export** all reference the کد ملی, stable across school
  changes (US-02 AC-4 re-validates sex against the new school).

### 3.3 Non-blocking (do not block Gate 2)

- **UX-OQ-22** — admin-home (S2) content: layout proposal exists; confirm to close.
- **UX-OQ-23** — driver credential delivery (OQ-12 ruled content; delivery mechanics remain).
- **UX-OQ-24** — multi-hour run UX (NFR-01/D-22): **needed before Phase 3**, not for Gate 2.

### 3.4 Amendment queue (post-sign-off, Requirements owner)

PO OQ-answers (OQ-10…13/15) + the OQ-12 identity extension must be formalized
into `docs/requirements/discovery.md` (§5 → resolved, D-03…-48 style entries)
via the **formal amendment protocol** (version increment + §6 changelog +
ripple sweep). Locked files were not touched during Phase 2.

## 4. Sign-off

By signing, the Product Owner confirms: UX package approved; Must-story flows
+ screens are walkable and acceptance-criterion-complete per independent pass
v2 (CLEAN); Gate-2 exit conditions met; Phase 3 (Architecture) may start
against this approved UX.

- [x] **OQ-13 suggestion approved** — national ID (کد ملی) as the unique
      student key; duplicates as suggested (2026-09-05, PO)
- [x] **Gate 2 — UX approved** (PO)

Signature: **iman (Product Owner, via chat 2026-09-05)**
Date: **2026-09-05**