# UX Flows — School Driver Platform (Phase 2)

> **Project:** Smart transportation platform for school students (daily home ↔ school shuttles)
> **Phase:** 2 — UX & Prototyping (flows, wireframes, usability-readiness)
> **Status:** Author draft — **pass v1 run** (2026-09-05 → `docs/ux/usability-pass-report-v1.md`,
> findings F1–F16). **Author-fix pass applied** (this revision): every finding addressed,
> PO rulings **UX-OQ-25/26** applied → **re-pass v2: CLEAN — 0 findings**
> (`usability-pass-report-v2.md`); **Gate 2 signed by the PO 2026-09-05** (`gate2-packet.md`).
> Author-side self-assessment: `docs/ux/ux-findings.md`.
> **Basis (locked, consumed as-is):** `docs/requirements.md` v1.0 + `docs/requirements/discovery.md` v1.0.
> Blocker note: **the baseline is not amended here. ** Any apparent contradiction is recorded
> as a finding/OQ, never edited.
> **UI language:** Persian (Farsi), full RTL (NFR-07, D-13). All screen labels below are
> given in Farsi with English glosses; the prototype (`wireframes.html`) renders RTL.
> **Accessibility (NFR-06):** every flow is keyboard-operable; text legible at 200% zoom;
> every control has a label. Indicated per screen.

---

## 1. Roles & entry points

| Role | Entry | Sees what | Defined by |
|---|---|---|---|
| Administrator (school staff) | Login (account provisioned by school, A-11) | everything (NFR-04): schools, students, drivers, matching, reports, flags | CR-01…19, US-01…06, 09 |
| Driver | Login (account provisioned by school, A-11) | only their own rosters (NFR-04) | CR-12, US-07 |
| Parent/Guardian | Login (auto-created from school data **or** registration request accepted by admin — CR-20/D-14) | only their own children's assignments (A-06, NFR-04) | CR-10, CR-20, US-08 |

Auth by role is the pre-condition for every flow (NFR-04: 0 cross-account exposure).
A parent with an unaccepted registration request can sign in but sees **no assignment
information** (US-08 AC-7) — see §6.

---

## 2. Screen inventory (wireframe IDs)

| ID | Screen | Role | Stories served |
|---|---|---|---|
| S1 | Login (role-aware) | all | all |
| S2 | Admin home | admin | US-01…06, 09 (**UX-OQ-22** — home content is an open question, see §8); **parents-request queue entry → S17** (US-08 AC-6, CR-20/D-14) |
| S3 | Schools list + register school form (+ per-row **ویرایش Edit → S16**) | admin | US-01 |
| S4 | Students list + register student form (+ per-row **ویرایش Edit → S5**) | admin | US-02, US-09 (flag) |
| S5 | Student edit (school change re-validation; **stored sex** per UX-OQ-26, AC-4 mismatch rejection with message) | admin | US-02 AC-4 |
| S6 | **Driver registry (list + per-row capacity, AC-3)** + register driver form (sections: capacity, origin, identity, sex, areas, availability); row actions → S7 | admin | US-03 |
| S7 | Driver record view / edit (capacity guard **with current-assignment count**, identity edit after publication) | admin | US-03 AC-4/7/8 |
| S8 | Matching: trigger + run status | admin | US-04, NFR-01/D-22, **UX-OQ-24** |
| S9 | Matching report (success) — **paginated assignment list + drill-down to an individual assignment; flagged/excluded marked in BOTH summary and drill-down (UX-OQ-25)** + per-direction totals + optimality evidence + unallocated availability + degenerate empty-report card (AC-8) | admin | US-04 AC-1/2/3/5/8/12, US-05 AC-1, US-09 AC-1 |
| S10 | Failure report (CR-18) — unassigned + shortfall per school/shift/direction (gender/area/time causes) + blocked assignments | admin | US-04 AC-6/7/9/10/11, US-05 AC-4, US-09 AC-4 |
| S11 | Report review & approve (publication gate) | admin | US-05 |
| S12 | Parent dashboard (child's assignment) + export | parent | US-08 |
| S13 | Parent account state (pending/active) | parent | US-08 AC-5/6/7 |
| S14 | Driver roster (per shift per direction, order+times) + export | driver | US-07 |
| S15 | Tweak assignment (informational sketch — Should story, out of MVP) | admin | US-06 (Should) |
| S16 | School edit (name/address+map/shift rows; saved → next run uses new times) | admin | US-01 AC-4 |
| S17 | Parent registration requests queue (accept/reject) | admin | US-08 AC-6 (CR-20/D-14) |

---

## 3. Flow: US-01 — Register a school (Must)

**Actor:** administrator. **Happy path first.**

### 3.1 Happy path
1. S2 → open **مدارس (Schools)** → **ثبت مدرسه جدید (New school)** → S3.
2. Enter **نام مدرسه (name)**.
3. **نشانی (address)** — type the address **and** select the location on the embedded simple
   map (D-28: admin types address + map-select; coordinates come from the map selection).
   Both address and coordinates are required (D-26, AC-5).
4. Select **جنسیت (sex)**: دخترانه (girls) or پسرانه (boys) — single-gender only (D-30, AC-6).
5. Add **شیفتها (shifts)**: one or more rows, each with start time + end time (D-33, AC-1);
   "add another shift" appends a row; a row can be removed (so that at least one stays, AC-2);
6. Submit → **success**: school appears in the list with all fields intact (AC-1).

### 3.2 Branches (validation)
- **AC-2** — no shift (all rows removed / none entered): block submit; inline message
  «حداقل یک شیفت لازم است» (at least one shift required).
- **AC-5** — address or coordinates missing: block submit; message names the missing
  component(s) — «نشانی و موقعیت روی نقشه الزامی است» with the specific missing field.
- **AC-6** — sex missing/invalid: block submit; «جنسیت معتبر (دخترانه/پسرانه) لازم است».
- **AC-3** — list renders each school's own shift times (no cross-school overwriting):
  verified on S3 list rows.

### 3.3 Post-registration edit (school edit screen — F1 fixed)
1. S3 — each list row has a **ویرایش (Edit)** affordance → **S16 (school edit)**.
2. S16 — edit name / address + map coordinates; **shift rows add/remove** with the same
   validation branches as the register form (AC-2/AC-5/AC-6 reusable); **sex read-only**
   (single-gender; a change would ripple student re-validation — out of AC-4 scope).
3. Save → school updated; the change takes effect at the **next** matching run (AC-4:
   runs for that school's students use the new shift time). If a plan is already
   **published**, the shift change can make published rosters stale — surfaced here as
   **OQ-10** input (see §8; does not silently resolve it).

---

## 4. Flow: US-02 — Register a student (Must)

**Actor:** administrator (the home address/location is provided by the **parent** — D-28;
**who initiates the flow is OQ-15** (open — see §8).

### 4.1 Happy path
1. S2 → **دانشآموزان (Students)** → **ثبت دانشآموز جدید (New student)** → S4.
2. Select **مدرسه (school)** — required (AC-3); on selection, **sex auto-fills from the
   school's sex** and is read-only (D-30). Per **UX-OQ-26 ruling (PO, 2026-09-05): the sex
   is stored-and-validated** — independent of the school selection — so a later school
   change (S5) can present the AC-4 mismatch rejection. At registration auto-fill is the
   only valid value; AC-5 is also enforced by the validation layer (API/direct input).
3. Select **شفت (shift)** — picker lists **only that school's shifts** (D-33, AC-6).
4. **نشانی منزل (home address)** — parent-provided: typed address + map-selected location,
   both required (D-26/D-28, AC-2).
5. Submit → success: student in the registry tied to exactly that school and shift (AC-1).

### 4.2 Branches (validation)
- **AC-2** — missing address/or coordinates: block; message names the missing part.
- **AC-3** — no school selected: block; «انتخاب مدرسه الزامی است».
- **AC-6** — no shift, or a shift not belonging to the selected school: block;
  «شیفت معتبر آن مدرسه الزامی است».

### 4.3 Edit school (AC-4, V4-09; F2/F16 fixed — UX-OQ-26 applied)
1. S4 — each student row has an **ویرایش (Edit)** affordance → **S5** (reachable).
2. S5 — **sex is the student's stored sex** (read-only, independent of the school
   selection — UX-OQ-26 ruling), NOT re-derived from the school. Changing the school
   re-validates immediately:
   - stored sex ≠ new school's sex → **AC-4 rejection shown with the mismatch message**
     («جنسیت ثبت‌شدهٔ دانش‌آموز (دخترانه) با جنسیت مدرسهٔ جدید (پسرانه) مغایر است — تغییر رد شد»),
     save disabled (fail-closed; AC-5 message form);
   - a **shift of the new school** must be selected (else AC-6 message).
Both fail-closed before save.

### 4.4 Relationship to matching & flags
- Registry updates feed the next matching run (CR-16 mid-year changes go through registry
  update + tweak, not re-run). **OQ-15** binds here: must home location exist before the
  student can appear in a run? (open — PO only).
- **OQ-13** (stable student identifier / duplicate rules) binds the list and the
  parent↔student linkage on S4/S12 — open, not silently resolved.

---

## 5. Flow: US-03 — Register a driver (Must)

**Actor:** administrator. **Happy path first** (form is intentionally long; scope note in baseline).

### 5.1 Happy path
1. S2 → **رانندگان (Drivers)** → S6. The **driver registry list** (per-row capacity, AC-3)
   is the first block; **ثبت راننده جدید (New driver)** opens the form below it; a row's
   **مشاهده پرونده (View record)** opens **S7**.
2. **ظرفیت (capacity)** — positive integer, e.g. 8 (AC-1; AC-2 zero/missing → error).
3. **مبدا (origin)** — driver's **home address** + map-selected coordinates, both required
   (D-24, D-26; AC-6 missing → error lists missing fields).
4. **مشخصات وسیله (vehicle identity)** — **پلاک (plate), مدل (model), رنگ (color)** (D-15,
   AC-5): stored; shown to parents after publication. All three required (AC-6).
5. **جنسیت (sex)** — مذکر (male) / مونث (female) (D-29, AC-9).
6. **مناطق خدماتی (service areas)** — multi-select of **predefined zones** (از پیش تعریفشده،
   D-43, AC-10); ≥1 required (AC-10 error if empty).
7. **دسترسی شیفت (availability: DriverShift entries)** — for each system-defined shift the
   driver serves: check **به مدرسه (to-school)** and/or **از مدرسه (from-school)** flags
   (CR-03/D-35, AC-11 needs ≥1 direction; AC-13 needs ≥1 shift; **no school is named** —
   school-agnostic, D-35/AC-4). Multiple shifts can be selected.
   - Each entry **displays its derived service window** = the shift's start…end (D-42/D-47,
     AC-12) — read-only, no manual window field at MVP; the **buffered reservation span
     [S−T, E+T]** is shown as a separate, clearly-labelled hint — it is NOT the window
     itself (F12 fixed).
8. Save → **staged**.
- **AC-3** — the registry list on S6 keeps each driver's own capacity (per-row column —
  never overwritten; F3 fixed).

### 5.2 Validation branches
- **AC-2** — capacity 0/missing: «ظرفیت مثبت لازم است».
- **AC-6** — missing plate/model/color/origin: message lists **all** missing fields; no
  partial record is saved.
- **AC-9** — sex missing/invalid: «جنسیت معتبر لازم است».
- **AC-10** — no service zone: «حداقل یک منطقه خدماتی الزامی است».
- **AC-11** — a DriverShift entry with no direction flag: «حداقل یک جهت (به مدرسه/از مدرسه) لازم است».
- **AC-13** — availability entry without any shift: «حداقل یک شیفت انتخاب کنید».
- **AC-14** — overlap guard (T = MIN_TURNAROUND_MINUTES = 30, D-37, config):
  - (i) two selected shifts with **overlapping clock windows** → reject (impossible under
    every allocation) — «تداخل زمانی شیفتها (غیرممکن تحت هر تخصیص)».
  - (ii) raw windows disjoint but **buffered** windows [S−T, E+T] intersect **and** the two
    shifts' adopting schools share **no common school** → reject (impossible — CR-26(ii)).
  - (iii) same buffered intersect but **≥1 common adopting school** → accept with warning:
    «این دو شیفت تنها در صورت تخصیص به یک مدرسه مشترک سازگارند» (compatible iff both runs
    allocated to a common school; CR-26(ii) third case, V5-03).

### 5.3 Post-registration edits
- **AC-7 (D-20)** — capacity edit that would drop **below the driver's current assignment
  count on an approved/published plan** → rejected with capacity message; existing capacity
  unchanged (S7).
- **AC-8 (D-25)** — vehicle identity editable **after publication**; parents see the
  **current** identity (S7 → reflected on S12 next load).
- **AC-4** — before any matching run, the driver record shows **no school** (no
  pre-assigned school; school is an output of matching).

---

## 6. Flow: US-05 — Review and publish the report (Must)

(the publish gate is the **consumer-facing** moment; US-04 produces the report — §7 covers
authoring; this section is the gate. Order in the doc follows story numbers; both must be
walked in the pass.)

**Actor:** administrator.

### 6.1 Happy path
1. S8 → run completed → S9 (success report) or S10 (failure report).
2. **S9** — per **UX-OQ-25 ruling (PO, 2026-09-05)**: a **paginated list of all assignments**
   (student, driver, school, shift, direction; page size chosen by the admin — paging is
   required at the NFR-01 500-student scale) **with drill-down to an individual assignment**,
   plus the **total driving distance per direction run** (AC-1). **Flagged/excluded students
   are marked in BOTH the summary and the drill-down view** (US-04 AC-1, US-05 AC-1,
   US-09 AC-1) + at-scale **optimality certificate** (proven zero gap, D-22, AC-5) +
   unallocated availability (AC-12, D-40). A degenerate run renders the **empty-report card**
   with no failure (AC-8 — F9 fixed).
3. **S11 — approve**: confirm dialog «انتشار نتیجهٔ تطبیق؟» → **انتشار (Publish)**.
4. On approve: assignments become visible to the corresponding parents and drivers via
   **both channels: dashboard and exported file** (CR-10, AC-3).

### 6.2 Branches
- **AC-2** — before approval, parent (S12) and driver (S14) dashboards show **no
  assignment information** (published-state gate).
- **AC-4** — failure report (S10): unassigned students + shortfall per school/shift/
  direction are clearly flagged; **publication of any partial plan is blocked** until
  resolved (add eligible drivers + re-run, or flag students — CR-18/CR-19).
- **AC-5 (D-27)** — a registry/capacity change made **after the run completed but before
  approval** → approve blocked: «گزارش دیگر با ثبت همخوانی ندارد; اجرای تطبیق مجدد (یا
  تعدیل/بازگردانی تغییر) الزامی است» — directs re-run (D-23), tweak (CR-16), or revert.
- **OQ-10 input** — if an older plan is published and a re-run is triggered, what do
  parents/drivers see meanwhile? Open (PO only); not silently resolved in the flow.

---

## 7. Flow: US-04 — Run annual matching (Must)

**Actor:** administrator.

### 7.1 Happy path
1. S2 → **تطبیق سالانه (Annual matching)** → S8.
2. Trigger «اجرای تطبیق» → run starts. **Run UX is an open question (UX-OQ-24 — see §8)**
   because NFR-01 allows hours (overnight acceptable, D-21/D-16); the prototype shows a
   non-blocking status view and a last-run log.
3. Completion → S9. Every **non-flagged** student is assigned to exactly one driver **per
   direction** (AC-1); flagged students appear marked **excluded (CR-19) — in the report
   summary AND in the drill-down view** (UX-OQ-25 ruling; US-09 AC-1).
4. Report shows: per-direction total distance (AC-5) + optimality evidence (D-22);
   per-school totals (D-45); **unallocated availability** = selected (shift, direction)
   entries the driver did not get — no error (AC-12, D-40).
5. Capacity respected **per direction run** (AC-2, A-13/D-34); each run serves exactly one
   school; same-day runs of one driver satisfy CR-26 (AC-3) — the report groups runs per
   driver per school so this is auditable.

### 7.2 Failure & degenerate branches
- **AC-6 (CR-18)** — infeasible for a shift/direction: **no partial plan**; S10 with:
  unassigned students list, **shortfall per school/shift/direction incl. gender/area/time
  causes**, blocked assignments. None of it publishable.
- **AC-7** — turnaround case (buffered conflict with no common adopting school, CR-26):
  fails exactly like AC-6 and the report names the **turnaround cause**.
- **AC-9** — a male driver as the only cover of a girls' school shift → gender-cause
  shortfall; no assignment violates gender rule (CR-21).
- **AC-10** — home/school outside every candidate's service areas → area-cause shortfall
  (CR-22).
- **AC-11** — no driver **selected** the shift-direction → «هیچ رانندهای این جهت شیفت را انتخاب نکرده» (D-47, selection-based).
- **AC-8** — degenerate registry (zero students / zero drivers / all flagged): completes
  with an empty or all-excluded report, **no failure raised**; rendered as the empty-report
  card on S9 (F9 fixed).
- **Resolution loop (CR-18 + US-09):** on S10, actions offered: (a) add eligible
  drivers + re-run; (b) flag students for exclusion (US-09) — with the baseline's
  warning that flagging resolves demand-side failures (capacity/coverage) and does **not**
  resolve supply-side eligibility failures unless all affected students are flagged (V4-11).

---

## 8. Flow: US-09 — Flag a student for exclusion (Must)

**Actor:** administrator. **Happy path + failure path (required by the pass checklist).**

### 8.1 Happy path
1. S4 (student registry) — each row has a **پرچم/وضعیت (flag)** toggle; set it → student
   marked **excluded (مستثنی)**. Flag is visible on the record and removable (AC-2).
2. Next matching run: flagged student is **not assigned** to any driver and appears in the
   report marked flagged/excluded (AC-1) — **in both the report summary and the drill-down
   (UX-OQ-25 ruling)**.

### 8.2 Unflag path
- Removing the flag → at the next run the student is **eligible again** (AC-3).

### 8.3 Failure-resolution path (AC-4, CR-18 flow)
1. S10 after a failed run (insufficient capacity) → **پرچم دانشآموز** action opens S4
   filtered to the failing group.
2. Flag one or more students → re-run matching.
3. New run completes with **all remaining (unflagged) students assigned** → can then be
   published (AC-4).
- **OQ-11** binds here: when a student is flagged/removed **mid-year after publication**,
   does the change propagate to live rosters/parent views immediately, at the next run, or
   via an explicit admin tweak? Open (PO only) — the flow stops short of inventing an answer.

---

## 9. Flow: US-07 — Driver views roster per shift and direction (Must)

**Actor:** driver.

### 9.1 Happy path
1. S1 → login → S14.
2. For each served shift: per direction —
   - **to-school**: students **in pickup order**, each with **pickup time**;
   - **from-school**: one **school-departure time** (shift end, A-02/D-39) + students in
     **drop-off order**, each with **drop-off time** (D-39; CR-12).
   Times are informational (A-07).
3. **Export** → file with the same students/order/times (AC-2, A-04; CR-10 both channels).

### 9.2 Branches
- **AC-3** — serves only to-school of a shift → **only** the to-school roster is shown for
  that shift; no from-school roster is fabricated (CR-24).
- **AC-4** — no assignments in a run: empty roster with a friendly empty state;
  never shows another driver's students (NFR-04).
- Pre-publication: no roster shown at all (US-05 AC-2 gate).

---

## 10. Flow: US-08 — Parent views child's assignment (Must)

**Actor:** parent/guardian. (This story merges assignment viewing with account
provisioning/activation for the MVP — D-17.)

### 10.1 Account states
- **AC-5** — auto-created from school-provided data: active on first sign-in (D-14/CR-20).
- **AC-6** — no account: parent requests registration → **S2 shows a parents-request queue
  (badge count) → S17 (admin accept/reject screen)** → active (S13 shows state; CR-20/D-14).
- **AC-7** — request not yet accepted: can sign in, sees **no assignment information**
  (S13 pending state; NFR-04).
- **OQ-12 input** — how parents receive credentials (SMS/email/printed handout) and what
  identifies "the driver" to the parent beyond vehicle identity: **open**, PO only (§8).

### 10.2 Happy path (active account, published assignment)
1. S1 → login → S12.
2. View: **child's name, school, shift, assigned driver per direction, and vehicle
   identity — plate, model, color** (AC-1; D-02 primary need).
   - Two children assigned to different drivers → each child's assignment shown separately
     (AC-4, A-06).
3. **Export** → same information in the file (AC-2).

### 10.3 Branches
- **AC-3** — child's assignment not published: **no assignment information** shown.
- A tweak (US-06, Should) updates the parent view immediately on save (CR-11) — sketch
  only, out of MVP scope set.

---

## 11. Flow: US-06 — Tweak assignments (Should — informational sketch)

Out of the MVP Must set; recorded per D-48 scope rules so the pass can check the flows it
touches (US-07/US-08 views). S15: pick student → pick target driver → pick **direction
scope per tweak — to-school only / from-school only / both (default)** (D-48) → validate
target driver eligibility (D-47) + per-direction capacity (D-34) + whole-day CR-26 →
save → applies immediately (CR-11); out-of-scope directions untouched (AC-5). **OQ-10**
(run vs tweak interaction) and **OQ-11** (mid-year propagation) remain open inputs here.

---

## 12. Cross-cutting concerns

- **Auth/NFR-04** — all roles authenticate (A-11); a parent sees only own children; a driver
  only own roster; admin all. Zero cross-account exposure is a hard UX constraint (every
  list screen is role-filtered server-side; the mockup marks this per screen).
- **RTL/NFR-07 (D-13)** — the whole UI (incl. exported files) is Farsi RTL; numerals Farsi.
- **Accessibility/NFR-06** — AA on text legibility + keyboard nav of main flows (register,
  review, view roster, view assignment): all controls focusable, form errors associated
  with fields (`role="alert"` + `aria-describedby` wired on the live demo forms — S3/S4/S5/
  S6/S16; F10 fixed), contrast ≥ 4.5:1; verified in the prototype.
- **Map entry (D-28)** — address typed + location map-selected everywhere; coordinates
  stored; both required (D-26). No paid geocoding at MVP (D-44 budget note).

---

## 13. Open questions ledger — additions & surfacings (Phase 2)

**Surfaced locked OQs (still OPEN — answered by the PO only, nothing silently resolved here):**
| ID | Where it binds | Effect on Gate 2 |
|---|---|---|
| OQ-10 | re-run vs published plan; shift-time change after publication (US-01 edit, §3.3); report staleness in §6.2 | non-blocking but must be answered before Gate-2 exit («no how does the user do X? gaps») |
| OQ-11 | mid-year flag/removal propagation (US-09 §8.3; US-06 §11) | same |
| OQ-12 | driver identity to parent beyond vehicle + parent credential delivery (US-08 §10.1; S13) | same |
| OQ-13 | student identifier & duplicate rules (US-02 §4.4; S4/S12) | same |
| OQ-15 | student-registration initiation + home-location-before-run requirement (US-02 §4.4) | same |
| OQ-17 | circular shifs (post-MVP — fixed shifts only at MVP, A-14) | none |

**New UX-OQs proposed by the author (sequential after OQ-21; PO confirmation required):**
| ID | Open question | Why it arose | Owner | Status |
|---|---|---|---|---|
| UX-OQ-22 | What is on the **admin home** screen after login (S2)? Baseline has no admin home content | Every admin flow starts at S2; content is undecided — «how does the user do X?» gap | Product owner | 🔶 Open — proposed |
| UX-OQ-23 | How do **drivers receive credentials** (A-11 provisions accounts; OQ-12 covers parents only)? | US-07 entry; same class as OQ-12 | Product owner | 🔶 Open — proposed (may fold into OQ-12) |
| UX-OQ-24 | **Multi-hour run UX** (NFR-01: hours, overnight OK): non-blocking status view vs modal; may the admin navigate away? can a run be re-triggered while one is in flight (and what happens to the older report — OQ-10 adjacency)? | S8; NFR-01/D-22 abort behavior needs a UX shape | Product owner | 🔶 Open — proposed |

**Ruled by the Product Owner (2026-09-05) — applied author-side, still unverified (re-pass):**
| ID | Ruling | Applied to |
|---|---|---|
| UX-OQ-25 | Report layout (S9): **paginated assignment list + drill-down to an individual assignment** is acceptable as «visible for review» per US-05 AC-1 (paginated list of all assignments with drill-down); **flagged/excluded students are marked in BOTH the summary and the drill-down** (US-04 AC-1, US-05 AC-1, US-09 AC-1) | S9 rework (**F4**); flows §6.1/§7.1/§8.1; ux-findings |
| UX-OQ-26 | Student sex is **stored-and-validated** (D-30), **independent of the school selection**; **S5 presents the AC-4 sex-mismatch rejection with the mismatch message** when the school is changed and the stored sex differs | S5 rework (**F2/F16**); flows §4.1/§4.3; ux-findings |

Design choices made **within** the baseline (not new requirements — flagged so the pass can
challenge them): inline resolve-actions on S10 (add driver/flag links); report grouping
per driver per school on S9; published-state gate visibles; empty states on S12/S14.

---

## 14. Author-side self-assessment pointer

Per-AC walkthrough (designed state) with the exact screen/step for every acceptance
criterion: see `docs/ux/ux-findings.md` (author-side, **not** the independent pass).
Independent verification: **pass v1 run** (2026-09-05 → `usability-pass-report-v1.md`,
16 findings); **all findings addressed in this author-fix pass** (F1–F16 + PO rulings
UX-OQ-25/26); **re-pass v2 (2026-09-05): CLEAN — 0 findings**; **Gate-2 sign-off:
2026-09-05** (`gate2-packet.md`).