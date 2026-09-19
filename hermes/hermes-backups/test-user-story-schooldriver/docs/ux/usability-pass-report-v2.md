# Usability-pass report — v2 (independent verifier, re-pass)

> **Project:** School Driver Platform — Phase 2 (UX & Prototyping)
> **Procedure:** `usability-pass` — Verifier instructions (`docs/ux/usability-pass-prompt.md`)
> **Verifier:** independent agent context (did NOT author or edit the package; governance §3.7 + Rule 7: author ≠ verifier)
> **Date of pass:** 2026-09-05
> **Purpose:** re-pass after the author-fix pass. Verify that v1 findings **F1–F16** are **RESOLVED** in the current package curve and that PO rulings **UX-OQ-25** (paginated + drill-down report layout; flagged/excluded marked in both summary and drill-down) and **UX-OQ-26** (student sex stored-and-validated; S5 AC-4 sex-mismatch rejection) are correctly applied. The same full procedure was re-run (not just the diffs).
> **Inputs read (in procedure order):**
> 1. `plans/2026-08-04_110131-agent-workflow-gov.md` §3.7 (UX/Design role)
> 2. `test-user-story-schooldriver/docs/requirements.md` v1.0 (locked baseline)
> 3. `test-user-story-schooldriver/docs/requirements/discovery.md` v1.0 (locked discovery)
> 4. `test-user-story-schooldriver/docs/ux/` (flows.md, wireframes.html, ux-findings.md, phase2-package-summary.md, usability-pass-pending.md)
> 5. Prior pass: `docs/ux/usability-pass-report-v1.md` (the F1–F16 being re-verified)
> **Constraint compliance:** reviews only — no file in `docs/ux/`, no locked baseline file was edited or amended. This report is the sole new file. All statements cite screen id / flow section / line where determinable.

---

## 1. Verdict per Must story

Every AC of US-01…05/07…09 was walked step-by-step against `flows.md` and `wireframes.html` (independent of the author's `ux-findings.md`, which was read afterwards as a comparison only). Actor consistency, edge/empty/failure states, baseline fidelity, and the no-silent-OQ-resolution rule were checked per story.

| Story | Verdict | Basis |
|---|---|---|
| US-01 Register a school | **PASS** | S3 (list+form) + S16 (edit); all 6 ACs satisfiable |
| US-02 Register a student | **PASS** | S4 (form+list, edit affordance) + S5 (AC-4 rework per UX-OQ-26); all 6 ACs satisfiable |
| US-03 Register a driver | **PASS** | S6 (registry list + form) + S7 (record); all 14 ACs satisfiable |
| US-04 Run annual matching | **PASS** | S8 (trigger) + S9 (report, reworked) + S10 (failure); all 12 ACs satisfiable |
| US-05 Review & publish | **PASS** | S9 (paginated list + drill-down, per UX-OQ-25) + S11 (approve gate); all 5 ACs satisfiable |
| US-07 Driver roster | **PASS** | S14; AC-1…4 satisfiable |
| US-08 Parent view | **PASS** | S12 + S13 + S17; AC-1…7 satisfiable |
| US-09 Flag a student | **PASS** | S4 + S9 (flag marker) + S10 (flag→re-run path); AC-1…4 satisfiable, failure path present |

US-06 (Should) is a sketch, not scored — procedure covers Must stories only; its D-48 scope is consistently marked informational (S15 gloss).

Key walkthrough notes: US-01 AC-4 now has a designed path (S3 row «ویرایش» → S16) and US-02 AC-4 (the S5 school-change re-validation, F2/F16) is walkable with the mismatch message shown and save disabled; US-03 AC-3 is satisfiable via the S6 registry table (F3); US-04/US-05/US-09 report AC-1s are satisfiable via the S9 paginated list + drill-down with flagged/excluded marked in both views (F4/per UX-OQ-25); US-08 AC-6 is satisfiable via S17 (F5).

---

## 2. Disposition of v1 findings F1–F16

Each finding below is confirmed **Resolved** on the strength of direct read of the current wireframes/flows (evidence cited). No finding is marked resolved on the author's word alone.

| ID | Sev (v1) | Status now | Evidence (current package) |
|---|---|---|---|
| **F1** (US-01 AC-4 school edit absent) | major | ✅ **Resolved** | New **S16** (`wireframes.html` lines 488–513) reachable from S3 row «ویرایش» (line 156); shift add/remove reuses AC-2/5/6 via `addShift`/`removeShift`/`validateSchoolEdit` (543–600); next-run semantics on save + OQ-10 surfaced (line 511; flows §3.3). |
| **F2** (US-02 AC-4 sex-mismatch unreachable) | major | ✅ **Resolved** | **S5** rendered with sex as the student's **stored** value (`value="دخترانه girls"`, line 222, independent of school). `s5SchoolChange()` (606–622): changing school to د.خیام (پسرانه) versus stored دخترانه → `s5-sex-err` shows the mismatch message and `s5-save` `disabled=true` (fail-closed, 615–619). Per UX-OQ-26. |
| **F3** (US-03 driver registry list absent) | major | ✅ **Resolved** | **S6** now opens with a driver **registry table** with a per-row capacity column (lines 235–241, AC-3) and per-row «مشاهده پرونده → S7» (238–240). flows §5.1 step 1. |
| **F4** (report aggregate-only; blocker) | blocker | ✅ **Resolved** | **S9 reworked per UX-OQ-25**: `ASSIGN` array of individual assignments (610–661); **paginated list** (`s9Render`/pager, 662–683, page size 6, "1–6 of 25"); **drill-down** per assignment (`s9Detail`, 685–697) showing student/school/shift/direction/driver+vehicle/time/status; **flagged/excluded marked in BOTH** the summary (flagged row, lines 322–331) **and** the drill-down (696) and the paginated row status cell (673–674). US-04 AC-1 / US-05 AC-1 / US-09 AC-1 walkable. Demo data capacity- and CR-26-consistent (see F6). |
| **F5** (US-08 AC-6 parent-request acceptance absent) | major | ✅ **Resolved** | New **S17** (515–525): parent registration requests with Accept/Reject per row, reachable from the S2 parents-request queue badge + «بررسی — Review requests» button (133–136). flows §10.1; CR-20/D-14. |
| **F6** (demo data violates CR-26 / AC-2) | minor | ✅ **Resolved** | S9 summary (325–329): student counts 6,6,7,2,3 — all ≤ capacity 8 (AC-2); no driver serves two different schools (احمدی→د.فردوسی, قاسمی→د.خیام, مهدوی→د.خیام) so no same-day cross-school buffered overlap (AC-3, CR-26). S6 availability (262–271) shows a **valid** single-shift selection with the reject pairing illustrated as a warn, not demoed-as-saved (AC-14(ii)). S12 driver-sex consistent (زهرا/دخترانه←مریم احمدی female; علی/پسرانه←اکبر قاسمی male; 407–417). |
| **F7** (S4 shift picker lists wrong shift) | minor | ✅ **Resolved** | S4 `st-shift` now lists only **07:00–12:00** (line 202), which is the shift of the default selected school د.فردوسی (دخترانه); label states "فقط شیفتهای همان مدرسه — only this school's shifts (AC-6)". flows §4.1 step 3. |
| **F8** (S3 AC-2 never fires; AC-5 no component specificity) | minor | ✅ **Resolved** | `validateSchool()` (567–585): AC-2 branch wired (`shiftErr` toggles on zero shift-rows, 576); AC-5 branch names the missing component explicitly — address AND coordinates / address only / coordinates only (577–580). Same controls in `validateSchoolEdit` (586–600). |
| **F9** (empty/pre-publication/degenerate states not rendered) | minor | ✅ **Resolved** | Rendered where asserted: S9 degenerate empty-report card (355), S12 not-published card (420), S14 empty-roster card (466), S3/S4/S6/S17 empty-registry cards (159, 195, 243, 526). |
| **F10** (error association: no role/aria) | minor | ✅ **Resolved** | Live demo forms wire `role="alert"` **and** `aria-describedby` (S3: sc-sex→sc-sex-err, sc-addr→sc-map-err, 164–180; S4: st-addr→st-addr-err 204–205; S5: s5-sex-err/s5-shift-err 225–226; S6 269; S16 sf-* 497–510). flows §12 claim now true. |
| **F11** (one branch of OQ-15 baked in) | minor | ✅ **Resolved-by-design** (not a code fix; OQ kept open) | The parent-enters-address branch intentionally has **no** screen and OQ-15 is explicitly marked open (flows §4.4; S4 hint line 196). This is the correct handling of an open PO-only question — **not** silently resolved. |
| **F12** (derived window labeled as buffered span) | minor | ✅ **Resolved** | S6 availability table has two distinct columns: "پنجرهٔ خدمت مشتقشده derived service window (شروع…پایان, AC-12/D-42)" and "پنجرهٔ رزرو بافرشده buffered [S−T,E+T] … نه خود پنجره" (265–267). flows §5.1 step 7. |
| **F13** (school list omits coordinates) | minor | ✅ **Resolved** | S3 list gained a «مختصات coordinates (D-26)» column with values (155–157). |
| **F14** (no current-assignment-count context for capacity guard) | minor | ✅ **Resolved** | S7 shows the current assignment count on the approved/published plan ("۷ دانشآموز 2026-08-20") beside the capacity field with the AC-7/D-20 guard text (285). |
| **F15** (un-requested failure-report export) | minor | ✅ **Resolved** | «Export failure report» removed from S10; note confirms "no failure-report export — CR-10 covers published assignments only" (378). flows §6.2/§7.2, ux-findings §3. |
| **F16** (no edit affordance → S5 unreachable) | major | ✅ **Resolved** | S4 rows each carry a «ویرایش — Edit (S5)» button (`onclick="switchTo('S5')"`, lines 191–193), so S5 (AC-4) is reachable. |

**F1–F16 disposition: all 16 Resolved.** No v1 finding is rejected as unresolved.

---

## 3. PO rulings — applied correctly, verified

- **UX-OQ-25 (report layout):** applied as ruled. S9 = paginated list of **all** assignments with drill-down to an individual assignment (student, driver, school, shift, direction + pick-up/drop-off time) plus per-direction totals (gloss 321; list 337–350; drill-down 351–354, 685–697; summary totals 325–329; optimality certificate 332). **Flagged/excluded marked in BOTH the summary** (dedicated flagged row, 330) **and the drill-down** (696) **and** the list status cell (673–674). Demo flagged student سرینا محمودی appears excluded in the list and drill-down.
- **UX-OQ-26 (student-sex representation):** applied as ruled. S5 presents the sex as **stored-and-validated, independent of the school selection** (line 222 gloss+value). School change that would mismatch the stored sex triggers the **AC-4 rejection with the mismatch message** and disables save (225, 615–619); a valid shift of the new school is required (226, 613–614). S4 registration keeps the auto-fill-then-store behavior consistent with "stored-and-validated at registration" (line 201, 104).

---

## 4. New UX-OQ proposals

**None.** The re-pass surfaced **zero genuinely new** undecided questions. The residual items raised on v1 are already captured: UX-OQ-24 (multi-hour run UX — S8 re-trigger while in-flight) and UX-OQ-22/23 remain **open, PO only**, and are honesty surfaced (S2 gloss; S8 warn "cofirmed by PO? — UX-OQ-24 open"; flows §13), **not silently resolved** — which per the procedure is a pass condition, not a finding imperative. Baseline OQs OQ-10…13, OQ-15 also remain surfaced and un-answered (flows §13; S4/S16/S12 hints).

Residual observations carried forward from the author (each confirmed non-blocking, Phase-3 / OQ-scoped, and not a Must-AC blocker):
1. S8 in-flight re-trigger guard — depends on open UX-OQ-24 (flows §7.1).
2. S11 D-27 approve-block warning rendered statically — flows §6.2 defines it as conditional on a post-run registry change (low-fi demo limitation).
3. S10 cause tags are illustrative pending the exact CR-18 fieldset (Phase-3 data model).

These are acknowledged, correctly attributed, and remove no Must AC from a walkthrough.

---

## 5. Checks performed (per verifier checklist)

1. **Flow exists & complete:** happy path present for every Must story; US-09 failure path (flag → re-run) present (flows §8.3; S10→S4→S8). ✅
2. **AC walkthrough:** every AC of US-01…05/07…09 walked against flows + screens — all satisfiable (no sources of block/confusion/undocumented steps found; v1 ones F1–F16 verified gone). ✅
3. **Actor consistency:** all 17 screens role-tagged; no role mixing; admin/driver/parent separation matches NFR-04. ✅
4. **Edge cases:** failure (US-04 AC-6…11, US-05 AC-4/5, US-09), empty/pre-publication/degenerate (US-04 AC-8, US-05 AC-2, US-07 AC-4, US-08 AC-3) rendered. ✅
5. **Baseline fidelity / open OQs:** no silent resolution found — OQ-10…13/15 and UX-OQ-22/23/24 all surfaced, not answered. No baseline contradiction introduced. ✅
6. **"How does the user do X?" gaps:** none new; the previously-flagged gaps (F1/F3/F5/F16) now have screens; UX-OQ-22/23 remain recorded open (PO-only). ✅
7. **New open questions:** none beyond the existing ledger (see §4). ✅
8. **Accessibility basics (NFR-06 spot check, not re-litigating the NFRs):** keyboard-operable native controls, `:focus-visible` outlines (22, 34, 40), labeled fields, AA contrast tokens, `role="alert"` + `aria-describedby` on live demo forms (F10 verified). RTL/NFR-07 confirmed (`dir="rtl"`, line 2, Farsi labels/numerals). ✅

---

## 6. Overall verdict

**CLEAN — zero findings (0 blocker / 0 major / 0 minor newly raised).**

- All v1 findings **F1–F16 → Resolved** (§2).
- Both PO rulings **UX-OQ-25 and UX-OQ-26 correctly applied** in the current package (§3).
- Every Must story (US-01…05, US-07…09) **PASS** on an independent AC walkthrough (§1).
- No new UX-OQ proposals (§4).

**Gate-2 status (verifier's read):** the Phase-2 package is **sign-offable from the usability-pass perspective** — every Must story has an approved-flow-and-screen representation and no open "how does the user do X?" gaps attributable to the design remain. The residual items are correctly typed as open PO questions (UX-OQ-22/23/24) and Phase-3 data/detail items, none of which is a design gap.

Necessary **before Gate-2 exit** (a PO action, not a verifier finding, per the package's own §3 exit criterion): the Product Owner must answer the still-open OQs — **OQ-10, OQ-11, OQ-12, OQ-13, OQ-15** (baseline) and **UX-OQ-22, UX-OQ-23, UX-OQ-24** — and give explicit UX sign-off. Until then the package is "clean on the pass + awaiting PO OQ answers," which is the expected Gate-2 state.

*This report was produced by an independent context; no file in `docs/ux/` (other than this report) and no locked baseline file was modified.*