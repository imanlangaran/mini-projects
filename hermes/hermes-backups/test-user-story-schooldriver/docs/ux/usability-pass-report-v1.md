# Usability-pass report — v1 (independent verifier)

> **Project:** School Driver Platform — Phase 2 (UX & Prototyping)
> **Procedure:** `usability-pass` — Verifier instructions (`docs/ux/usability-pass-prompt.md`)
> **Verifier:** independent agent context (did NOT author or edit the package; governance §3.7 + Rule 7: author ≠ verifier)
> **Date of pass:** 2026-09-05
> **Inputs read (in procedure order):**
> 1. `plans/2026-08-04_110131-agent-workflow-gov.md` §3.7 (UX/Design role)
> 2. `test-user-story-schooldriver/docs/requirements.md` v1.0 (locked baseline)
> 3. `test-user-story-schooldriver/docs/requirements/discovery.md` v1.0 (locked discovery)
> 4. `test-user-story-schooldriver/docs/ux/` (flows.md, wireframes.html, ux-findings.md, phase2-package-summary.md, usability-pass-pending.md)
> **Constraint compliance:** reviews only — no file in `docs/ux/`, no locked baseline file was edited or amended. This report is the sole new file. All findings cite story ID, AC, and flow/screen location.

---

## 1. Verdict per Must story

### US-01 — Register a school → **FINDINGS** (F1 major, F8 minor, F13 minor)
- AC-1 ✅ satisfiable in `wireframes.html` S3 (form + list). **F13 (minor):** the list renders name/sex/shifts/address only — no coordinates column — so "appears … with all fields intact" is only partially demonstrable for a required field per D-26 (flows §3.1 step 3 vs S3 table, lines 141–145).
- AC-2 ✅ branch defined (flows §3.2; S3 error `sc-shift-err`), but **F8 (minor):** the S3 demo JS (`validateSchool`) never fires the AC-2 error (toggled `false` unconditionally, wireframes.html line 450) — branch asserted, not demonstrable; same for the AC-5 "names the missing component(s)" specificity (only `!addr` is checked, line 449; a missing-coordinates-only submission is not detected — AC-5 requires naming the missing component(s)).
- AC-3 ✅ verified (S3 rows show per-school shift cells).
- **AC-4 → finding F1 (major):** "a school whose shift time is later changed and saved" has **no designed screen**. Flow §3.3 asserts the capability ("School shift times can be changed later") but gives no steps, S3 has no edit affordance on list rows (lines 141–145), and the screen inventory (flows §2) contains **no school edit/view screen** (contrast: S5/S7 exist for student/driver edits). The AC-4 walkthrough requires an undocumented step. Root cause candidate: school edit also touches OQ-10 adjacency, but the edit screen itself is baseline-required (AC-4) — the absence is a finding, not an OQ.
- AC-5/AC-6 ✅ branches defined (flows §3.2; S3) — subject to F8.

### US-02 — Register a student → **FINDINGS** (F2 major, F16 major, F7 minor, F11 minor)
- AC-1 ✅ (S4 form: school → shift → parent address+map → register; flows §4.1 steps 1–5).
- AC-2 ✅ (S4 error line; flows §4.2).
- AC-3 ✅ (required school select; flows §4.2).
- **AC-4 → findings F2 (major) + F16 (major):**
  - **F2:** S5 (wireframes.html lines 190–205) renders the sex field as *auto-filled read-only from the selected school* (`value="دخترانه girls" disabled`). The AC-4 rejection branch ("sex must equal the new school's sex … if either fails, the change is rejected", US-02 AC-4, V4-09) is therefore **unrepresentable/unreachable in the designed UI**: a sex-mismatched school change silently displays the *new* school's sex (the field visibly flips to match), so the user is never shown the mismatch the system is supposed to reject; flows §4.3 describes the fail-closed rule but no screen state demonstrates it). This also silently tilts at an undecided baseline-adjacent point: how the student's sex is represented (stored-and-validated per D-30 vs derived from the school) — recorded as new UX-OQ-26 (§4), not invented here.
  - **F16:** S4's student table rows (lines 171–176) have **no edit/DETAIL affordance**, so S5 (the AC-4 screen) is **unreachable from the designed screens**. The AC-4 flow's first step ("S4 → S5") is an undocumented step; flows §4.3 and ux-findings §2 assume navigation that the wireframes do not provide.
- AC-5 ✅ (enforced server-side; not triggerable via UI — consistent with D-30's "validated, not freely chosen"; author disposition accepted).
- AC-6 ✅ (shift picker limited to the school's shifts per flows §4.2) — **F7 (minor):** the S4 static mock (line 183) lists both "07:00–12:00" and "12:00–19:00" while the selected school (د.فردوسی) has only 07:00–12:00 per S3 — the mock contradicts AC-6's "only that school's shifts" as rendered (flow text corrects it; the prototype does not).
- **F11 (minor):** S4 bakes in "administrator types the parent-provided address" (D-28), i.e. the admin-initiated branch of OQ-15. The OQ is correctly flagged open in flows §4.4, but the alternate branch (parent enters the address during account activation) has **no screen** (S13 is state-only) — a latent "how does the user do X?" if OQ-15 resolves that way.

### US-03 — Register a driver → **FINDINGS** (F3 major, F6 minor, F12 minor, F14 minor)
- AC-1 ✅ (S6 form + S7 record: capacity/origin/identity all visible).
- AC-2 ✅ (`min="1"` + «ظرفیت مثبت» flows §5.2).
- **AC-3 → finding F3 (major):** "when the registry is viewed, each driver keeps their own capacity" — **there is no driver registry (list) screen.** S6 is the create-form only (lines 207–240); S7 is a single-record view (lines 242–262). Flow §5.1 step 1 ("S2 → رانندگان (Drivers) → New driver → S6") names a Drivers list page that exists nowhere in the screen inventory (flows §2 S1–S15), and ux-findings §2 US-03 AC-3 cites "S6 table rows" — S6 has no registry table. AC-3 (and AC-4's "when their record is viewed", plus any navigation to S7) cannot be walked; this is also a screen-inventory gap vs S3/S4 which combine list+form.
- AC-4 ✅ (S7 hint: no school pre-assigned; D-35) — reachability subject to F3.
- AC-5 ✅ (S6 fields; S12 shows plate/model/color after publication).
- AC-6 ✅ («پیام لیست همه فیلدهای کمشده», flows §5.2).
- **AC-7 → D14 (minor):** S7 (line 259) states the guard but shows **no "current assignment count"** anywhere on the record — the admin editing capacity has no visible context for the value the guard compares against; the rejection (when it fires) is not self-explanatory on screen.
- AC-8 ✅ (S7 editable identity + S12 hint; D-25).
- AC-9 ✅ / AC-10 ✅ / AC-11 ✅ (required selects/checkboxes + messages, flows §5.2).
- **AC-12 → F12 (minor):** the S6 "derived window" cell (line 233) renders the **buffered reservation span** «[06:30، 12:30] buffered ±T=30» as the *derived service window*, whereas AC-12/D-42 say the entry "displays its derived service window — the selected shift's start and end". A-15's buffered reservation is different information; the label conflates the two (the ±T hint makes it transparent, but the AC-12 walkthrough reads the wrong value as "the window").
- **AC-13/AC-14 → F6 (minor, see also US-04):** the guarded combination is *demoed as valid*. S6's availability table (lines 233–234) shows one driver simultaneously selecting 07:00–12:00 (to-school) and 12:00–19:00 (from-school). The selecting shift pair's buffered windows [06:30,12:30] ∩ [11:30,19:30] intersect and — per the demo schools (د.فردوسی adopts 07:00–12:00; د.خیام adopts 12:00–19:00) — share **no common adopting school**, so per flows §5.2 AC-14(ii) (CR-26(ii)) this entry must be **REJECTED** — the wireframe shows it as a ready-to-save valid form. AC-14(iii)/(iii) messages themselves are documented in flows §5.2 ✅.

### US-04 — Run annual matching → **FINDINGS** (F4 blocker, F6 minor, F9 minor)
- AC-1 → **F4 (blocker, shared with US-05/US-09):** the success report **S9 (lines 284–302) renders per-run *aggregates* only — school / shift / direction / **student count** / driver / total distance. It contains **no per-student assignment rows** and **no flagged/excluded marker**, although flows §7.1 step 3 asserts "flagged students appear marked excluded (CR-19)" and AC-1's every-non-flagged-student assignment is not verifiable from counts. A walkthrough of AC-1 (and of its excluded-marking) cannot be completed on the designed screen. (Detailed in F4 under US-05.)
- AC-2 ✅ as designed (per-run capacity column) — **but F6 (minor):** S9's own demo data violates it: rows show «42 students / ر. قاسمی (ظرفیت 8)» and «42 / ر. احمدی (ظرفیت 8)» (lines 292–293) — 42 students on a capacity-8 driver in one direction run contradicts AC-2 (at most C students) and US-04 AC-3's single-run/single-driver model. Additionally the same driver قاسمی is allocated both د.فردوسی 07:00–12:00 به م and د.خیام 12:00–19:00 به م (lines 292, 294): buffered windows [06:30,12:30] and [11:30,19:30] intersect at different schools → **CR-26(ii)/AC-14(ii) forbids this allocation** — the "success" report displays a turnaround violation of exactly the kind matching must not produce (and S6 also demoes that selection per F6 in US-03). The prototype's own data contradicts the hard constraints it claims to audit.
- AC-3 ✅ structurally (per-driver-per-school grouping makes CR-26 auditable — but see F6 for the demo data violating it).
- AC-4 ✅ (automatic meter, not UI; surfaces as D-22 certificate — author disposition accepted; flows §7.1 step 4 + ux-findings row 4).
- AC-5 ✅ (per-row totals + «گواهی بهینگی: zero gap proven (D-22)» on S9).
- AC-6/AC-7/AC-9/AC-10/AC-11 ✅ (S10: unassigned list + shortfall per school/shift/direction with gender/area/selection causes (lines 304–324); turnaround cause per flows §7.2; blocked assignments listed separately).
- AC-8 ✅ flow-defined («empty or all-excluded report, no failure», flows §7.2) — **but F9 (minor):** the empty/all-excluded report state is **not rendered** in the prototype (S9 has no empty-state card); asserted in flow text only.
- AC-12 ✅ (S9 «تخصیصنشدهها» card, D-40).
- UX-OQ-24 (multi-hour run, D-22 abort) correctly surfaced at S8/flows §7.1 ✅ — not silently resolved.

### US-05 — Review and publish the report → **FINDINGS** (F4 blocker, F9 minor)
- **AC-1 → F4 (blocker):** AC-1 requires "every assignment (student, driver, school, shift, direction) and the per-direction total distances are visible for review". Flows §6.1 step 2 claims "S9 — report lists every assignment …", but the S9 wireframe (lines 284–302) shows only aggregate summary rows (student *count* 42, driver, total distance) — **no individual assignments are visible**, so the administrator cannot review *who* is assigned *where* — the core act this story exists for cannot be performed on the designed screen. This is the report-content gap; until the layout is decided (inline listing vs drill-down/filter/pagination at NFR-01's 500-student scale), AC-1 is not satisfiable. Recorded as **UX-OQ-25** (§4) for the PO, then the author must rework S9. It also breaks US-04 AC-1's excluded-marking and US-09 AC-1's "appears in the run's report marked flagged/excluded" (no marker anywhere on S9).
- AC-2 ✅ flow-level (published-state gate on S12/S14; flows §6.2) — empty/pre-publication rendering: see F9.
- AC-3 ✅ (S11 Publish + Export = both channels per CR-10).
- AC-4 ✅ (S10 has **no** publish affordance — publication structurally blocked on failure; S11 gloss; flows §6.2).
- AC-5 ✅ (S11 D-27 block message lists re-run/tweak/revert; flows §6.2) — static-warning state-dependency already noted by the author (minor accepted).
- **F9 (minor):** pre-publication states are asserted in gloss/hint text (S12 line 347, S14 line 410) but no empty-state rendering exists in the prototype — the "no assignment information" state is described, not designed.

### US-07 — Driver views roster per shift and direction → **PASS** (cross-cutting minor F9 applies)
- AC-1 ✅ (S14: to-school pickup order+times; from-school school-departure (shift end, A-02) + drop-off order+times — lines 388–409; D-39).
- AC-2 ✅ (export button; same content asserted; A-04).
- AC-3 ✅ (flows §9.2 + S14 warn line 410: no fabricated roster; CR-24).
- AC-4 ✅ flow-represented («empty roster with a friendly empty state; never shows another driver's students»; NFR-04) — the *rendering* of the empty state is missing from the prototype (F9 minor, cross-cutting; flows §9.2 defines the branch, so the story is walkthrough-able from the flow).
- Actor consistency ✅ (driver-only screen; role tag; NFR-04).

### US-08 — Parent views child's assignment → **FINDINGS** (F5 major, F9 minor)
- AC-1 ✅ (S12: per child — name, school, shift, driver per direction, plate/model/color; D-02; two-child separation AC-4 also ✅ line 363).
- AC-2 ✅ (export button, same info; A-04).
- AC-3 ✅ flow-level (S12 gloss; published-state gate) — rendering: F9 minor.
- AC-4 ✅ (S12 second card; A-06).
- AC-5 ✅ (S13 active card; flows §10.1).
- **AC-6 → finding F5 (major):** "the administrator/school accepts the request" — **no admin screen exists for it.** Flows §10.1 says "acceptance happens on the admin side, **S2→parents**", but S2 (lines 111–134) has no parents section/queue — no quick action, no status row (status table covers schools/students/drivers/last-run only) — and no other admin screen in the inventory accepts parent requests. US-08 AC-6's walkthrough dead-ends at an undocumented step. (Adjacent OQ-12 credential delivery is correctly surfaced on S13/flows §10.1 ✅, not resolved.)
- AC-7 ✅ (S13 pending card: can sign in, no assignment info; NFR-04).

### US-09 — Flag a student for exclusion → **FINDINGS** (F4 blocker, applies to AC-1)
- Happy path ✅ (S4 flag toggle; flows §8.1 step 1–2) — and the pass-required **failure path (flag → re-run)** is present: S10 «پرچم دانشآموزان» → S4 filtered to the failing group → re-run → publishable (flows §8.3; AC-4 ✅).
- AC-1 → **F4 (blocker):** "appears in the run's report marked as flagged/excluded" — S9 renders **no flagged/excluded marker** anywhere (flows §7.1 step 3 asserts it; the wireframe does not).
- AC-2 ✅ (S4: «مستثنی» tag + «حذف پرچم» button; flag visible and removable).
- AC-3 ✅ (flows §8.2: unflag → eligible at next run).
- AC-4 ✅ (S10 action + flows §8.3 steps 1–3 with CR-18/V4-11 guardrails).
- OQ-11 (mid-year propagation) correctly surfaced (flows §8.3), not silently resolved ✅.

### US-06 (Should — informational sketch)
Out of the MVP Must set; S15 sketch covers D-48 direction scope and is kept only because it touches S12/S14 views. **Not scored** (procedure covers Must stories); the pass notes it is consistently marked informational, and OQ-10/OQ-11 are re-surfaced there ✅.

---

## 2. Consolidated findings register

| ID | Severity | Story / AC | Location | Finding (one line) |
|---|---|---|---|---|
| F1 | major | US-01 AC-4 | flows §3.3; S3; inventory §2 | No school edit screen/affordance — shift-time change ("later changed and saved") has no designed path |
| F2 | major | US-02 AC-4 | flows §4.3; S5 (lines 190–205) | Sex auto-fills read-only from the *new* school ⇒ AC-4's sex-mismatch rejection unreachable/silently bypassed in the UI |
| F3 | major | US-03 AC-3/AC-4 | flows §5.1 step 1; S6/S7; ux-findings US-03 AC-3 row | No driver registry list screen — "when the registry is viewed" AC-3 (and S7 reachability) have no screen; flow and findings cite a "Drivers list"/"S6 table rows" that don't exist |
| F4 | **blocker** | US-04 AC-1; US-05 AC-1; US-09 AC-1 | flows §6.1/§7.1; S9 (lines 284–302) | Report is aggregate-only (student counts); no per-student assignments visible, no flagged/excluded marker — the review act (US-05 core) and the excluded-marking ACs cannot be walked |
| F5 | major | US-08 AC-6 | flows §10.1; S2 | No admin screen/queue (S2 shows none) to accept parent registration requests — AC-6's "administrator accepts" step has no designed screen |
| F6 | minor | US-03 AC-14(ii); US-04 AC-2/AC-3 | S6 (232–234); S9 (291–295) | Demo data violates the constraints themselves: 42 students on capacity-8 drivers; same driver allocated buffered-overlapping different-school runs (07:00–12:00 ف.ردوسی + 12:00–19:00 خیام) that CR-26(ii)/AC-14 must reject |
| F7 | minor | US-02 AC-6 | S4 (line 183) | Shift picker mock lists a shift that does not belong to the selected school (AC-6 says only that school's shifts) |
| F8 | minor | US-01 AC-2/AC-5 | S3 demo JS (449–450) | Demo detects missing address only (not coordinates); AC-2 error never fires; missing-component specificity not demonstrable |
| F9 | minor | US-05 AC-2; US-07 AC-4; US-08 AC-3; US-04 AC-8 | S12 (347), S14 (410), S9, S3/S4/S6 | Empty/pre-publication/empty-report/empty-registry states asserted in hints only — not rendered in the prototype |
| F10 | minor | NFR-06 (a11y basics) | S3 demo; flows §12 | Error toggling is class-only (no `role="alert"`/`aria-describedby`); flow §12 claims "form errors associated with fields (aria)" — not present in the prototype; screen-reader announcement not demonstrable (NFR-06 spot check; NFRs not re-litigated) |
| F11 | minor | US-02 (D-28/OQ-15 adjacency) | flows §4.4; S4 | Address entry is designed admin-side only; the OQ-15 alternate (parent enters during activation) has no screen — flagged open but one branch baked in |
| F12 | minor | US-03 AC-12 (D-42/A-15) | S6 (line 233) | "Derived service window" rendered as the buffered reservation span [±T] instead of the shift start…end per AC-12/D-42 |
| F13 | minor | US-01 AC-1 (D-26) | S3 (141–145) | List omits coordinates — stored location not verifiable from the list |
| F14 | minor | US-03 AC-7 (D-20) | S7 (259) | No current-assignment-count display beside the capacity field — guard context invisible to the admin |
| F15 | minor | CR-10 scope | S10 (line 322) | "Export failure report" button is an un-requested capability (CR-10 channels cover published assignments; failure-report export is not in the baseline) — PO to confirm or drop |
| F16 | major | US-02 AC-4 | S4 (171–176) → S5 | No edit affordance on student rows — S5 (the AC-4 screen) is unreachable from the designed screens |

**Count:** 16 findings — **1 blocker, 5 major, 10 minor.**

---

## 3. Checks performed (per verifier checklist)
1. **Flow exists & complete:** happy path present for every Must story; US-09 failure path (flag → re-run) present (flows §8.3) ✅ (F1/F3/F5/F16 are missing-screen findings, not missing flows).
2. **AC walkthrough:** walked every AC of US-01…05/07…09 against the flows and screens — findings as registered. Points where the design blocks/confuses/undocumented: F1, F2, F3, F4, F5, F7, F12, F16 (specifics in §1/§2).
3. **Actor consistency:** all screens role-tagged; no role mixing observed; admin/driver/parent separation matches NFR-04 (parent only own children, driver only own rosters — asserted on every list/role screen) ✅.
4. **Edge cases:** failure paths (US-04 AC-6…11, US-05 AC-4/5, US-09) well covered; empty states under-rendered (F9); degenerate-run state flow-defined (AC-8; rendering minor F9).
5. **Baseline fidelity / open OQs:** no silent resolution of open OQs found — OQ-10 (§6.2/§11/§13), OQ-11 (§8.3/§11), OQ-12 (§10.1/S13), OQ-13 (S4/§13), OQ-15 (§4.4; F11 minor), OQ-17 (post-MVP, fixed shifts) all surfaced, not answered. **Exception-classes:** F2 (OQ-adjacent student-sex representation — formally proposed as UX-OQ-26) and F11 (OQ-15 one-branch shape — minor). No baseline contradiction found beyond the demo-data violations (F6), which contradict the *baseline's* CR-26/AC-2 constraints as rendered.
6. **"How does the user do X?" gaps:** F1 (edit school), F3 (view driver registry / open S7), F5 (accept parent request), F16 (open S5) — plus the author's three UX-OQs (22–24) which this verifier **confirms as valid open gaps**.
7. **New open questions:** UX-OQ-25 and UX-OQ-26 proposed below (sequential, never reused; PO confirms).
8. **Accessibility basics (NFR-06):** keyboard-operability (real `<button>`/native inputs, `:focus-visible` outlines), labeled controls, AA-level contrast tokens (checked: ink/muted/accent/danger/warn/ok all ≥4.5:1) ✅; error-association gap = F10 (minor). RTL/NFR-07 (D-13): `dir="rtl"`, Farsi labels & numerals throughout, exported files noted RTL ✅.

---

## 4. New UX-OQ proposals (verifier-proposed; Product Owner confirms)

| ID | Open question | Why it arose | Gate-2 rationale |
|---|---|---|---|
| **UX-OQ-25** | **Report contents & review layout (S9):** must the matching report render every assignment inline (student, driver, school, shift, direction — US-05 AC-1) at the NFR-01 scale (500 students), or is a paginated/filterable/drill-down presentation "visible for review" per AC-1? Where do flagged/excluded student markers render (US-04 AC-1, US-09 AC-1)? | F4 (blocker): S9 as designed cannot satisfy US-05 AC-1 — the review act is the story's core; no screen state shows individual assignments or the flagged/excluded marking | **Blocks Gate-2 exit.** US-05 (Must) has a non-walkable AC-1 until the PO rules on the layout; the author must then rework S9 (and re-pass) |
| **UX-OQ-26** | **Student-sex representation & the school-change UX (S5):** is the student's sex stored-and-validated (per D-30, enabling the AC-4 mismatch rejection) or derived from the school (making the mismatch only data-import/API-reachable)? How must S5 present the AC-4 rejection (the current auto-fill read-only field visually adopts the new school's sex, contradicting the rejection)? | F2 (major): the AC-4 rejection branch is unreachable/misleading in the designed screen; the underlying representation is undecided in the locked baseline's own wording (D-30 vs US-02 AC-4) — this pass cannot invent the answer | **Blocks Gate-2 exit.** US-02 (Must) AC-4 cannot be walked truthfully until resolved and S5 is reworked (re-pass) |

*(The author's three proposals UX-OQ-22/23/24 are confirmed as valid open gaps: UX-OQ-22 non-blocking (layout proposal exists), UX-OQ-23 non-blocking (may fold into OQ-12), UX-OQ-24 non-blocking but needed before Phase 3 (NFR-01/D-22 run UX). Baseline OQs OQ-10…13/15 also remain open and bind Gate-2 exit per the package's own criterion — PO answers only.)*

---

## 5. Overall verdict

**FINDINGS — 16 findings: 1 blocker, 5 major, 10 minor.**

- **Blocker (F4):** the success-report screen (S9) cannot support the report's core purpose — an administrator cannot review individual assignments (US-05 AC-1) and flagged/excluded marking (US-04 AC-1, US-09 AC-1) has no representation. Fix requires a PO ruling (UX-OQ-25) + screen rework.
- **Majors:** F1 (school edit screen absent — US-01 AC-4), F2 + F16 (AC-4 sex-mismatch rejection unreachable AND S5 unreachable — US-02 AC-4), F3 (driver registry list absent — US-03 AC-3/4), F5 (parent-request acceptance screen absent — US-08 AC-6).
- **Minors:** F6–F15 (demo-data constraint violations, mock inconsistencies, empty-state rendering, a11y error-association, OQ-15 branch shape, AC-12 label, AC-1 coordinates column, AC-7 context display, un-requested failure-report export).

**Gate-2 status (verifier's read):** the package is structurally strong (flows per story, AC-branch coverage, OQ surfacing discipline, RTL/a11y basics, honest self-assessment) but **not yet sign-offable**: the blocker alone prevents Gate-2 exit, and the five majors each remove a Must-AC from the walkthrough. Path to green: PO answers UX-OQ-25/26 (+ existing 22…24 and OQ-10…13/15), author reworks S9, S5/S4-nav, school-edit, driver-list, and parent-queue screens, then a re-pass (per procedure step 4) before PO sign-off.

*This report was produced by an independent context; no file in `docs/ux/` (other than this report) and no locked baseline file was modified.*