# UX Findings — Author-side self-assessment (Phase 2)

> **Project:** School Driver Platform
> **Phase:** 2 — UX & Prototyping
> **Document type:** author-side self-check, produced by the UX/Design agent (the
> package author). **This is NOT the independent usability pass.**
> **State:** the independent pass **v1 ran** (2026-09-05 → `docs/ux/usability-pass-report-v1.md`,
> findings F1–F16). This file was then **updated by the author-fix pass** — every finding
> addressed and PO rulings **UX-OQ-25/26** applied (author-side, per the report's §5 path).
> **Re-pass v2 ran 2026-09-05: CLEAN — 0 findings** (`usability-pass-report-v2.md`); the
> rows below (author-side walkthrough, post-fix) were confirmed by that independent pass.
> **Scope:** per-AC walkthrough of the designed screens (flows §2–11, `wireframes.html`),
> verifying the design lets a user actually complete each acceptance criterion.
> **Baseline consumed as-is:** `docs/requirements.md` v1.0 + `docs/requirements/discovery.md` v1.0 (locked; no amendments here).

---

## 1. Walkthrough summary

| Story | Priority | Verdict (author-side) | Coverage |
|---|---|---|---|
| US-01 | Must | **Pass** — all ACs satisfiable in S3/S16 | S3, S16 |
| US-02 | Must | **Pass** — all ACs satisfiable in S4/S5 (reworked) | S4, S5 |
| US-03 | Must | **Pass** — all ACs satisfiable in S6 (registry)/S7 | S6, S7 |
| US-04 | Must | **Pass** — happy path + all failure branches in S8/S9 (reworked)/S10 | S8, S9, S10 |
| US-05 | Must | **Pass** — overview + approve + blocks in S9/S11 | S9, S11 |
| US-07 | Must | **Pass** — both directions + empty/per-direction states in S14 | S14 |
| US-08 | Must | **Pass** — parent view + account states in S12/S13/S17 | S12, S13, S17 |
| US-09 | Must | **Pass** — flag/unflag + re-run resolution loop in S4/S9/S10 | S4, S9, S10 |
| US-06 (Should) | Should | **Sketch only** (S15) — out of MVP set | S15 |

Every Must story: happy path present; US-09 also has the flag → re-run failure path
(required by the pass checklist).

---

## 2. Per-AC walkthrough (Must stories)

### US-01 — Register a school (S3)
| AC | Walkthrough | Status |
|---|---|---|
| AC-1 | S3 form: name + address + map-select → coordinates; sex select; ≥1 shift row (start+end); submit → list shows all fields incl. **coordinates column** (F13 fixed) | ✅ |
| AC-2 | No shift (all rows removed): submit blocked; inline «حداقل یک شیفت لازم است» — demo now **runs the AC-2 branch** (add/remove shift rows wired, F8 fixed) | ✅ |
| AC-3 | List table renders each school's own shift times (per-row cells) | ✅ |
| AC-4 | Shift-time edit path: S3 row **ویرایش → S16** (school edit) → save; next matching run uses the new time (F1 fixed) | ✅ (S16) |
| AC-5 | Missing address **or** coordinates: blocked; message **names the missing component(s)** — demo checks address AND coordinates (F8 fixed) | ✅ |
| AC-6 | Sex missing/invalid: blocked; «جنسیت معتبر (دخترانه/پسرانه) لازم است» (required select + `sc-sex-err` wired, F8/F10) | ✅ |

### US-02 — Register a student (S4/S5)
| AC | Walkthrough | Status |
|---|---|---|
| AC-1 | S4: school select → sex auto-fill (read-only, then **stored** — D-30/UX-OQ-26) → shift (only that school's shifts — F7 fixed) → parent address + map-select → submit → registry row (school+shift) | ✅ |
| AC-2 | Address or coordinates missing: blocked with named missing component (error line on S4, `role="alert"`) | ✅ |
| AC-3 | No school: school is a required select; blocked with message | ✅ |
| AC-4 | S5 (reworked): sex shows the student's **stored sex** (NOT re-derived from the school); school change with sex mismatch → **AC-4 rejection with the mismatch message**, save disabled; valid new-school shift required (F2+F16 fixed; UX-OQ-26 applied) | ✅ |
| AC-5 | Sex ≠ school sex: stored-and-validated (D-30); at registration auto-fill prevents via UI; enforced server-side + **demonstrable on S5 school change** (mismatch rejection with message) | ✅ |
| AC-6 | No shift / shift not of school: shift picker lists only that school's shifts (demo consistent — F7 fixed); blocked otherwise | ✅ |

### US-03 — Register a driver (S6/S7)
| AC | Walkthrough | Status |
|---|---|---|
| AC-1 | S6: capacity + origin (home address+map) + identity (plate/model/color) + sex + zones + availability → record row shows all | ✅ |
| AC-2 | Capacity 0/missing: input `min=1` + server check «ظرفیت مثبت لازم است» | ✅ |
| AC-3 | **Registry table on S6** (list) keeps each driver's own capacity (per-row column; F3 fixed) | ✅ |
| AC-4 | Driver record view (S7) before any matching run: **no school shown** (no school field in the form — school-agnostic, D-35); reachable from the S6 registry row «مشاهده پرونده» (F3 fixed) | ✅ |
| AC-5 | Identity fields stored; parent view (S12) shows plate/model/color after publication | ✅ |
| AC-6 | Missing plate/model/color/origin: blocked; message lists all missing fields; no partial save (noted on S6) | ✅ |
| AC-7 | S7 capacity edit below assigned count on approved/published plan → rejected; **current assignment count shown beside capacity** (F14 fixed); existing capacity unchanged (D-20; flows §5.3) | ✅ |
| AC-8 | S7 identity edit after publication → saved; S12 shows current identity (D-25) | ✅ |
| AC-9 | Sex missing/invalid: required select, rejected (D-29) | ✅ |
| AC-10 | No service zone: multi-select, ≥1 required, rejected (D-43) | ✅ |
| AC-11 | DriverShift entry with no direction: checkbox pair, neither checked → blocked «حداقل یک جهت لازم است» (CR-24) | ✅ |
| AC-12 | Derived service window displayed read-only = **shift start…end** (D-42/D-47); the **buffered [S−T,E+T] span is a separate labelled hint**, not the window (F12 fixed) — no manual window field | ✅ |
| AC-13 | Availability without shift: entries only exist per selected shift; blocked «حداقل یک شیفت انتخاب کنید» | ✅ |
| AC-14 | Overlap guard (T=30, D-37): S6 demo shows a **valid selection state** (only 07:00–12:00 selected) and illustrates the reject cases — overlapping clock windows rejected; buffered-intersect w/o common adopting school rejected (as demoed: +12:00–19:00 → رد); buffered-intersect with common school → warning «تنها با مدرسهٔ مشترک سازگار است» (F6 fixed) | ✅ |

### US-04 — Run annual matching (S8/S9/S10)
| AC | Walkthrough | Status |
|---|---|---|
| AC-1 | Trigger (S8) → success report (S9): every non-flagged student assigned per direction; flagged marked excluded **in the summary AND the drill-down view** (F4 fixed; UX-OQ-25 applied) | ✅ |
| AC-2 | Per-direction capacity: report groups per run; capacity column; **demo data capacity-consistent** — no 42-on-capacity-8 rows (F6 fixed) | ✅ |
| AC-3 | One school per run + CR-26 compliance: S9 groups runs per driver per school; **demo data has no same-day different-school buffered overlaps** (F6 fixed) | ✅ |
| AC-4 | Exhaustive-verification small dataset: covered in Phase 3/6 (automatic, not UI); report shows totals | ✅ (not UI-visible by design) |
| AC-5 | Per-direction totals + optimality evidence (certificate, D-22) on S9 | ✅ |
| AC-6 | Infeasible: S10 failure report (list, shortfall per school/shift/direction with gender/area/time causes, blocked assignments) — no partial plan publishable | ✅ |
| AC-7 | Turnaround dataset: S10 names the CR-26 turnaround cause (AC-6 shape) | ✅ |
| AC-8 | Degenerate (0 students / 0 drivers / all flagged): completes with an empty or all-excluded report, no failure — **empty-report card rendered on S9** (F9 fixed; flows §7.2) | ✅ |
| AC-9 | Male-only cover of girls' shift → gender-cause shortfall; no gender-rule violation (S10 cause tags) | ✅ |
| AC-10 | Outside all service areas → area-cause shortfall (S10 cause tags) | ✅ |
| AC-11 | No driver selected the shift-direction → selection-cause shortfall (D-47; S10 cause tag) | ✅ |
| AC-12 | Unallocated availability listed with no error (S9 «تخصیصنشدهها», D-40) | ✅ |

### US-05 — Review and publish (S9/S11)
| AC | Walkthrough | Status |
|---|---|---|
| AC-1 | S9: **paginated assignment list (all assignments, page size) + drill-down to an individual assignment** (student, driver, school, shift, direction) + per-direction totals; flagged/excluded marked in both views (F4 fixed; UX-OQ-25 applied) | ✅ |
| AC-2 | Pre-approval: S12/S14 show no assignment info — **not-published / empty states rendered** (F9 fixed) | ✅ |
| AC-3 | Approve (S11) → visible to parents/drivers via dashboard **and** exported file (CR-10; both buttons on S11) | ✅ |
| AC-4 | Failure report: unassigned + shortfall flagged; publication blocked (S10/S11); **no failure-report export button** (un-requested capability removed — F15) | ✅ |
| AC-5 | Registry changed post-run: approve blocked with D-27 message («گزارش دیگر با ثبت همخوانی ندارد…») | ✅ |

### US-07 — Driver roster (S14)
| AC | Walkthrough | Status |
|---|---|---|
| AC-1 | Per shift per direction: to-school pickup order + times; from-school departure time + drop-off order + times (D-39) | ✅ |
| AC-2 | Export file same students/order/times (A-04; button on S14) | ✅ |
| AC-3 | Only served directions shown; no fabricated roster (CR-24; warning card on S14) | ✅ |
| AC-4 | Empty roster state **rendered on S14** (friendly empty state card; F9 fixed); never others' students (NFR-04) | ✅ |

### US-08 — Parent assignment view (S12/S13)
| AC | Walkthrough | Status |
|---|---|---|
| AC-1 | S12: child name, school, shift, driver per direction, vehicle identity (plate/model/color — D-02/D-15); demo data driver-sex consistent (CR-21) | ✅ |
| AC-2 | Export same info (button on S12) | ✅ |
| AC-3 | Not published → no assignment info — **S12 not-published empty state rendered** (F9 fixed) | ✅ |
| AC-4 | Two children on different drivers shown separately (two cards on S12; A-06) | ✅ |
| AC-5 | Auto-created account active on first sign-in (S13 active state) | ✅ |
| AC-6 | Parent-request account active after admin accepts — **S17 admin accept/reject screen, reachable from the S2 parents-request queue** (F5 fixed; CR-20/D-14) | ✅ |
| AC-7 | Unaccepted request → can sign in, sees no assignment info (S13 pending state) | ✅ |

### US-09 — Flag a student (S4/S10)
| AC | Walkthrough | Status |
|---|---|---|
| AC-1 | Flagged → not assigned; appears marked excluded in the report **summary AND drill-down** (S9; F4 fixed; UX-OQ-25 applied) | ✅ |
| AC-2 | Flag visible on record + removable (S4 «حذف پرچم») | ✅ |
| AC-3 | Unflag → eligible at next run (S4) | ✅ |
| AC-4 | Failed run → flag students → re-run → all remaining assigned → publishable (S10 action → S4 → S8) | ✅ |

---

## 3. Author-side findings (self-check output, post v1-fix pass)

**Blockers:** none remaining author-side. The v1 pass found 1 blocker (**F4** — S9 report
layout); it was reworked per the PO ruling **UX-OQ-25** (paginated assignments + drill-down,
flagged/excluded marked in both views). *Author-side status is provisional until the re-pass.*

**Majors:** none remaining author-side. The v1 pass found 5 majors — **F1** (school edit →
new S16), **F2+F16** (S5 stored-sex mismatch rejection + S4 edit affordance, per UX-OQ-26),
**F3** (driver registry list on S6), **F5** (parent-request accept/reject → new S17) — all fixed.

**Minors / observations (author-side):**
1. **S8 re-run while a run is in flight** — the prototype shows a trigger button with no
   in-flight guard; behavior decided only when UX-OQ-24 is answered (prototype marks OQ).
2. **S11 D-27 block message** — shown as a static warning; a real UI should only show it
   when a change occurred since run completion (state-dependent; Phase 3 detail).
3. **S10 cause tags** are illustrative; the real failure report needs the exact CR-18
   fields list (data model — Phase 3), the UI pattern (per-school/shift/direction
   shortfall table) is what's designed here.
4. **F15 applied** — the un-requested «Export failure report» button was removed from S10
   (CR-10 export channels cover published assignments only; no PO confirmation to keep it).
5. **F11 recorded, not resolved** — OQ-15 stays open (PO only): the alternate branch
   (parent enters the home address during account activation) intentionally has **no
   screen**; per the fix mandate, open OQs must not be invented/answered author-side.
6. **OQ-10/11/12/13/15 surfacings** — deliberately not resolved in the design; listed in
   flows §13. They are inputs to Gate-2 exit.

**Design decisions made within the baseline (flagged for the pass):**
- Inline resolve-actions on S10 (add driver / flag students links) — flows §10.2.
- Report grouping per driver per school on S9; pagination + drill-down per UX-OQ-25.
- Published-state gate on S12/S14.
- Derived-window display with buffered ±T as a separate hint on S6 (F12; AC-12).

---

## 4. New open questions (proposed by the author — PO to confirm)

| ID | Question | Source | Blocks Gate 2? |
|---|---|---|---|
| UX-OQ-22 | Admin home (S2) content after login | S2 is the entry of every admin flow; baseline silent | No (layout proposal exists) |
| UX-OQ-23 | Driver credential delivery | US-07 entry; OQ-12 covers parents only | No |
| UX-OQ-24 | Multi-hour run UX (S8): status view vs modal; re-trigger while in-flight; older report handling (adjacent OQ-10) | NFR-01/D-22 | No (but needed before Phase 3) |

**UX-OQ-25 / UX-OQ-26 — verifier-proposed (pass v1), PO-ANSWERED 2026-09-05, applied
author-side (flows §13).** Both remain *unverified* until the re-pass.
| ID | Question | Ruling | Status |
|---|---|---|---|
| UX-OQ-25 | Report layout (S9): inline vs paginated/drill-down; where flagged/excluded render | Paginated assignment list + drill-down acceptable per US-05 AC-1; flagged/excluded marked in **BOTH summary and drill-down** (US-04/05/09 AC-1) | Answered — applied to S9 rework (F4) |
| UX-OQ-26 | Student-sex representation & S5 school-change rejection | Sex **stored-and-validated** (D-30), independent of school; S5 presents the AC-4 mismatch rejection with the mismatch message | Answered — applied to S5 rework (F2/F16) |

These **proposals** remain open and are PO-only: UX-OQ-22/23/24. Baseline OQs OQ-10…13,
OQ-15 remain open and are re-surfaced in flows §13 (OQ-17 is post-MVP, non-binding).

---

## 5. Author-side overall verdict

**Author-side (post v1-fix pass): READY FOR RE-PASS.** All v1 findings (F1–F16) are
addressed in the package — blocker F4 reworked per **UX-OQ-25**, majors F1/F2/F3/F5/F16
fixed with new/updated screens (S16/S17/S5/S6/S4), minors F6–F15 fixed in the wireframes
and flows — and PO rulings UX-OQ-25/26 applied. **This remains author-side and
unverified**: the re-pass must run in a fresh context (Rule 7 — the author must not
verify its own work) before Gate-2 sign-off.