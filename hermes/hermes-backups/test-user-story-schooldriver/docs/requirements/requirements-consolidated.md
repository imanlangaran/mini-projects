# Requirements — School Driver Platform (Reader Edition)

> **Derived from baseline v1.1** (`docs/requirements.md` — BASELINE LOCKED, originally locked 2026-08-25, amended 2026-09-05).
> This edition folds resolved open questions and supersession annotations into clean current-truth prose for readers. It is **not** the governing artifact: for the audit trail, change history, and formal citation, consult `docs/requirements.md` and `docs/requirements/discovery.md`; any conflict resolves in favor of the originals. Changes require a formal amendment to the baseline first.

---

## 1. Scope in one paragraph

A system where an administrator registers schools (single-sex, with shifts), accepts **parent-initiated student registrations** (home addresses, sex validated against the school, one shift), and registers drivers (capacities, vehicle identity, sex, service areas, service hours per shift and direction); triggers an annual matching run that assigns every student to a driver per shift and direction while minimizing total driving distance per direction run (hard capacity, gender, service-area, and time-window constraints; no school pre-assigned — matching allocates runs per school and a driver may serve multiple schools subject to the same-day turnaround rule, CR-26); reviews and publishes the resulting plan; and fine-tunes assignments mid-year without re-running matching. Parents view their child's assigned driver/vehicle identity; drivers view per-shift, per-direction rosters (students, pickup order, times) — via dashboard and exported file. No notifications, no pickup tracking, no same-day handling.

---

## 2. User Stories

### US-01 — Register a school
**As an** administrator, **I want to** register each school with its name, location, sex (single-gender), and one or more shifts, **so that** students can be tied to the correct school, gender rules can be enforced, and per-shift run times are derived correctly.

- **AC-1:** Given a school with name, location, sex, and at least one shift (start + end time), when the administrator submits the registration, then the school appears in the school list with all fields intact.
- **AC-2:** Given a school record submitted without a shift, when the administrator submits it, then the submission is rejected with a message indicating at least one shift is required.
- **AC-3:** Given two schools registered with different shift times, when the administrator views the list, then each school shows its own shift times (times do not overwrite each other).
- **AC-4:** Given a school whose shift time is later changed and saved, when a matching run completes after that change, then the runs for that school's students use the new shift time.
- **AC-5:** Given a school record missing the address, the coordinates, or both (both required per D-26), when the administrator submits it, then the submission is rejected with a message naming the missing component(s).
- **AC-6:** Given a school record without a sex, or with a value other than male/female, when the administrator submits it, then the submission is rejected with a message that a valid sex is required (D-30).
- **AC-7:** Given a school registration whose name and coordinates match an existing school (duplicate: same name + coordinates per D-26), when the administrator submits it, then it is rejected with a message naming the existing record (D-52, NFR-09).

**Priority:** Must | **Traces to:** CR-01, CR-08, D-30, D-52

---

### US-02 — Register a student
**As an** administrator, **I want to** process a **parent-initiated student registration** (the parent initiates; the student record is created when the administrator/school accepts it — D-53) with a home location (address and coordinates, provided by the parent — D-28), a **national ID (کد ملی) as the unique student key (D-52)**, exactly one school, a sex matching the school's sex, and exactly one shift of that school, **so that** the matcher can plan a pickup at the correct location for the correct school, shift, and gender group.

- **AC-1:** Given a parent-initiated student registration whose home address and coordinates were provided by the parent (typed address + map-selected location per D-28), carrying a **valid 10-digit national ID (کد ملی) (D-52)**, one selected school, and one shift of that school, when the administrator/school accepts it, then the student appears in the registry tied to exactly that school and shift, keyed on the کد ملی.
- **AC-2:** Given a student record missing the home address, the coordinates, or both (both required per D-26), when the administrator submits it, then it is rejected with a message naming the missing component(s).
- **AC-3:** Given a student record without a selected school, when the administrator submits it, then it is rejected with a message that a school is required.
- **AC-4:** Given a student whose school is later changed and saved, when the registry is viewed, then the student is tied to exactly one school (the new one) **and re-validated against the new school** — sex must equal the new school's sex (D-30), and a shift of the new school must be selected (D-33); if either fails, the change is rejected with the AC-5/AC-6 messages.
- **AC-5:** Given a student record whose sex differs from the selected school's sex, when the administrator submits it, then it is rejected with a message that the student's sex must equal the school's sex (D-30).
- **AC-6:** Given a student record without a selected shift, or with a shift that does not belong to the selected school, when the administrator submits it, then it is rejected with a message that a valid shift of that school is required (D-33).
- **AC-7:** Given a student registration whose کد ملی matches an existing student's (duplicate: same national ID), when the administrator submits it, then it is rejected with a message naming the existing record (D-52, NFR-09).

**Priority:** Must | **Traces to:** CR-02, CR-16, CR-21, D-33, D-52, D-53

---

### US-03 — Register a driver with capacity, origin, vehicle identity, sex, service areas, and service availability
**As an** administrator, **I want to** register drivers along with their vehicle capacities, origin (home address), vehicle identity details, sex, service areas, and per-shift/per-direction service availability, **so that** matching plans respect each driver's carrying limit, gender rule, area coverage, time availability, and parents can recognize the vehicle that will pick up their child.

*Scope note: intentionally carries a large acceptance set (driver creation, capacity-edit guard, post-publication identity edits, MOKEAB fields, availability-selection guards, duplicate checks) — accepted as one story; recorded deviation from the 3–7 AC guideline.*

- **AC-1:** Given a driver record with a capacity of 8, an origin (home address), and vehicle identity details, when the administrator submits it, then the driver's record shows capacity 8, the origin, and the identity details.
- **AC-2:** Given a driver record with capacity 0 or missing, when the administrator submits it, then it is rejected with a message that a positive capacity is required.
- **AC-3:** Given drivers registered with capacities 4, 8, and 11, when the registry is viewed, then each driver keeps their own capacity.
- **AC-4:** Given a registered driver, when their record is viewed before any matching run, then no school is shown as pre-assigned (the school is determined by matching).
- **AC-5:** Given a driver record that includes vehicle identity details — plate number, model, and color (OQ-05, resolved) — plus the **driver's name and phone number** (D-51), when the administrator submits it, then the details are stored with the driver's record and appear in the parent's view after publication (US-08).
- **AC-6:** Given a driver record submitted without plate number, model, color, the **driver's name, the driver's phone number, the driver's national ID (کد ملی — D-52)**, or origin (home address), when the administrator submits it, then it is rejected with a message listing the missing fields, and no partial record is saved.
- **AC-7:** Given a driver whose capacity edit would drop below their current assignment count on an approved/published plan, when the administrator saves the edit, then the edit is rejected with a capacity message and the existing capacity is unchanged (D-20).
- **AC-8:** Given a driver whose vehicle identity is edited after publication, when the administrator saves the edit and a parent opens the dashboard, then the parent sees the **current** identity (D-25).
- **AC-9:** Given a driver record without a sex, or with a value other than male/female, when the administrator submits it, then it is rejected with a message that a valid sex is required (D-29).
- **AC-10:** Given a driver record without at least one service area (one or more predefined zones — D-43), when the administrator submits it, then it is rejected with a message that at least one service zone is required (D-31).
- **AC-11:** Given a driver recorded with a shift-direction availability entry (DriverShift) that has no direction selected (neither to-school nor from-school), when the administrator saves it, then it is rejected with a message that at least one direction is required (CR-24).
- **AC-12:** Given a driver with one or more selected shifts saved, when the availability entry is viewed, then each entry displays its **derived service window** — the selected shift's start and end (D-42/D-47); no manually entered window field exists at MVP.
- **AC-13:** Given a driver availability entry that names no selected shift, when the administrator saves it, then it is rejected with a message that at least one shift must be selected; an entry consists solely of selected shifts plus served direction(s) and never names a school (D-35, CR-03).
- **AC-14:** Given a driver who selects two shifts with overlapping clock windows, when the administrator saves the entry, then it is rejected (impossible under every school allocation — CR-26(i)); given two shifts whose raw windows are disjoint but whose buffered windows [S − T, E + T] intersect **and whose sets of adopting schools share no common school**, when the administrator saves the entry, then it is likewise **rejected** (impossible under every allocation — CR-26(ii)); and given such a buffered-intersect pair sharing at least one common school, when the administrator saves the entry, then it is accepted with a warning that the two runs are compatible only if both are allocated to a common school of the two shifts (at least one shared adopting school), with T read from configuration (MIN_TURNAROUND_MINUTES — D-37).
- **AC-15:** Given a driver registration whose plate number or کد ملی matches an existing driver's (duplicate: same plate **or** same national ID), when the administrator submits it, then it is rejected with a message naming the existing record (D-52, NFR-09).

**Priority:** Must | **Traces to:** CR-03, CR-04, CR-21, CR-22, CR-23, CR-24, CR-25, CR-26, D-02, D-51, D-52

---

### US-04 — Run annual matching (per shift and direction)
**As an** administrator, **I want to** trigger a matching run that assigns every student to a driver for each shift and direction, minimizing total driving distance per direction run, **so that** the school year starts with a complete, efficient, compliant pickup plan.

*Scope note: intentionally carries an extended acceptance set — the core capability, feasibility/failure/degenerate paths, and the gender/area/time constraints. Accepted as one story; recorded deviation from the 3–7 AC guideline.*

- **AC-1:** Given a registry where a **feasible assignment exists** (per school and shift: the shift's students can be covered by the drivers allocated to that school, respecting per-driver capacity, same-day run compatibility (CR-26), gender rule CR-21, service-area rule CR-22, and selection-based eligibility D-47), when the administrator triggers matching, then every registered non-flagged student is assigned to exactly one driver **for each of the shift's directions**, and flagged students appear marked as excluded (CR-19).
- **AC-2:** Given a driver with capacity C for a direction, when matching completes, then that driver is assigned at most C students **for that direction run** (A-13, confirmed as D-34).
- **AC-3:** Given students tied to different schools, when matching completes, then each run assigned to a driver serves students of exactly one school, and every pair of same-day runs allocated to that driver satisfies the compatibility rules (CR-26: non-overlap; ≥ 2 × MIN_TURNAROUND_MINUTES gap between runs of different schools; back-to-back allowed within one school) — a driver may serve multiple schools across runs (D-36).
- **AC-4:** Given a small dataset whose optimal plan is known (verified by exhaustive search), when matching runs, then the report's total distance equals that optimal value **for each direction run**. The **exact-optimality guarantee applies at every scale** (D-21); small-instance exhaustive verification is the acceptance meter for the guarantee.
- **AC-5:** Given the report after matching, when the administrator opens it, then it shows the total driving distance **per direction run** and, for at-scale runs, the recorded optimality evidence (certificate of proven zero gap per D-22).
- **AC-6:** Given a registry where **no feasible assignment exists** for a shift or direction (e.g., global capacity is sufficient but one school's students exceed what the drivers that can serve that school can carry, or no eligible driver exists due to gender/area/selection rules), when the administrator triggers matching, then no partial plan is produced for publication; instead the run reports the failure with the complete data: the list of unassigned students, the shortfall per school/shift/direction (including gender, area, and eligibility causes), and the assignments that could not be made (CR-18).
- **AC-7:** Given the turnaround dataset (School A: 1 student with shift 07:00–12:00; School B: 1 student with shift 12:00–19:00; a single driver available for both shifts, capacity ≥ 1, of the same sex as both schools' students (D-30), whose predefined zones cover both schools and both homes (CR-22/D-43), and who selected both shifts with the needed directions (D-47) — total capacity exceeds total demand, yet the A-from-school run ends 12:00 and the B-to-school run starts 12:00 at a **different school** with a 0-minute gap < 2 × MIN_TURNAROUND_MINUTES), when the administrator triggers matching, then the run fails exactly as described in AC-6 (no invalid plan is produced; the report names the CR-26 turnaround cause).
- **AC-8:** Given a degenerate registry (zero students, zero drivers, or every student flagged for exclusion), when the administrator triggers matching, then the run completes with an empty or all-excluded report and raises no failure.
- **AC-9:** Given a girls-only school shift and a male driver who is the only driver covering it, when the administrator triggers matching, then the run reports the shift as infeasible with a gender-cause shortfall (CR-21) — a male driver is never assigned female students (AC-9a: no assignment violates the gender rule; verified for all pairs in the report).
- **AC-10:** Given a student whose home or school lies outside every candidate driver's service area, when the administrator triggers matching, then those drivers are not assigned to that student (CR-22) and, if no eligible driver remains, the run reports the area-cause shortfall per AC-6.
- **AC-11:** Given a shift-direction that **no driver selected** (MVP eligibility is selection-based — D-47), when matching runs and students demand that direction, then no driver is allocated to it and the run reports the shortfall per AC-6 with cause "no eligible driver selected this shift-direction."
- **AC-12:** Given a driver whose selected (shift, direction) entries exceed what matching allocates, when a successful run completes, then the driver keeps only the allocated runs and the report lists the unused selections as **unallocated availability** — no error is raised (selection is capability, not obligation — D-40).

**Priority:** Must | **Traces to:** CR-05, CR-06, CR-07, CR-08, CR-21, CR-22, CR-23, CR-24, CR-26, D-40, D-47

---

### US-05 — Review and publish the matching report
**As an** administrator, **I want to** review the matching report and explicitly approve it before anything goes live, **so that** parents and drivers only ever see finalized assignments.

- **AC-1:** Given a completed matching run, when the administrator opens the report, then every assignment (student, driver, school, shift, direction) and the per-direction total distances are visible for review.
- **AC-2:** Given a report that has not been approved, when a parent or driver views the dashboard, then no assignment information is shown.
- **AC-3:** Given a reviewed report, when the administrator approves it, then assignments become visible to the corresponding parents and drivers (dashboard and exported file).
- **AC-4:** Given a matching run that failed to assign every student for some shift or direction, when the administrator reviews the failure report, then the unassigned students and the shortfall per school/shift/direction are clearly flagged, and publication of any partial plan is blocked until the failure is resolved (add drivers + re-run, or flag students — CR-18/CR-19).
- **AC-5:** Given a registry or capacity change made after a matching run completed but before the report is approved, when the administrator attempts to approve the report, then approval is blocked with a message stating the report no longer matches the registry and directing the administrator to re-run matching (D-23), tweak assignments (CR-16), or revert the change (D-27).

**Priority:** Must | **Traces to:** CR-09, CR-10, D-27

---

### US-06 — Tweak assignments without re-running matching
**As an** administrator, **I want to** change one student's assigned driver and have it take effect immediately, **so that** I can respond to mid-year changes without disturbing the rest of the plan.

Each tweak carries a **direction scope chosen per tweak**: to-school only, from-school only, or both (**default**) — validated per direction (D-48). A **new matching run supersedes** the previous published plan — the old plan stops being published; prior tweaks are **not automatically carried** into the re-run's plan — the administrator may re-apply them manually for any assignment still valid under the new plan (D-49); the trigger screen shows a supersede warning before an in-flight re-run.

- **AC-1:** Given an approved plan, when the administrator reassigns a student to a different driver and saves, then the change is stored immediately.
- **AC-2:** Given a saved reassignment, when the affected parent and drivers view their dashboards, then the parent sees the new driver, the new driver's roster includes the student, and the previous driver's roster no longer lists the student.
- **AC-3:** Given a reassignment that would put the target driver over capacity, when the administrator attempts to save it, then the change is rejected with a capacity message and no assignment changes.
- **AC-4:** Given a saved reassignment, when other students' assignments are inspected, then none of them changed (the tweak did not re-run matching).
- **AC-5:** Given a reassignment whose administrator-selected direction scope is **to-school only**, when it is saved, then the student's from-school assignment is unchanged and the to-school assignment is validated against the target driver's eligibility and capacity for that direction (D-47, D-34, CR-21, CR-22, CR-26); from-school-only scoping is symmetric; scope **both** applies the change to both directions.

**Priority:** Should | **Traces to:** CR-11, CR-16, D-48, D-49

---

### US-07 — Driver views roster per shift and direction
**As a** driver, **I want to** see, for each shift and direction I serve, my assigned students with pickup order and times, **so that** I know exactly whom to pick up, in what order, and when — for the to-school run and the from-school run.

- **AC-1:** Given a published plan, when the driver opens the dashboard, then the roster shows, per shift and per direction: the to-school run's students in pickup order, each with a pickup time; and the from-school run's school-departure time plus its students in drop-off order, each with a drop-off time (D-39).
- **AC-2:** Given a published plan, when the driver exports the roster file, then the file contains the same students, order, and times as the dashboard.
- **AC-3:** Given a published plan where a driver serves only the to-school direction of a shift, when the driver views the dashboard, then only the to-school roster is shown for that shift (no from-school roster is fabricated) (CR-24).
- **AC-4:** Given a driver with no assignments in a run, when the driver opens the dashboard, then the roster is empty and shows no other driver's students.

**Priority:** Must | **Traces to:** CR-08, CR-12, CR-24

---

### US-08 — Parent views child's assignment (driver/vehicle identity)
**As a** parent/guardian, **I want to** see my child's assigned driver and vehicle identity, **so that** I can recognize who is coming to pick up my child.

*Scope note: intentionally merges assignment viewing (AC-1…4) with parent account provisioning/activation (AC-5…7) for the MVP; split deferred pending growth (D-17).*

- **AC-1:** Given a published assignment for my child, when I open the dashboard, then I see my child's name, school, shift, assigned driver (per direction) with the **driver's name and phone number**, and vehicle identity — **car model, plate number, and color** — (identity set per OQ-05/CR-03/D-15, extended by **D-51**).
- **AC-2:** Given a published assignment for my child, when I export the assignment file, then it contains the same driver/vehicle identity information.
- **AC-3:** Given my child's assignment has not been published, when I open the dashboard, then no assignment information is shown.
- **AC-4:** Given a parent with two children assigned to different drivers, when I open the dashboard, then each child's assignment is shown separately.
- **AC-5:** Given a parent whose account was auto-created from school-provided data, when they sign in, then the account is active and they can view their child's assignment.
- **AC-6:** Given a parent without an account, when they request account registration and the administrator/school accepts the request, then the account becomes active and the parent can view the assignment.
- **AC-7:** Given a parent whose registration request has not yet been accepted, when they attempt to sign in, then they cannot access any assignment information.

**Priority:** Must | **Traces to:** CR-10, CR-20, D-02, D-51

---

### US-09 — Flag a student for exclusion from assignment
**As an** administrator, **I want to** flag a student so they are excluded from a matching run, **so that** I can resolve capacity failures or handle students who don't need transport without corrupting the plan.

Flagging **or removing** a student mid-year propagates immediately to live rosters (US-07) and parent views (US-08); matching is **not re-run** (D-50).

- **AC-1:** Given a student flagged as excluded, when a matching run executes, then the student is not assigned to any driver and appears in the run's report marked as flagged/excluded.
- **AC-2:** Given a flagged student, when the administrator views the registry, then the flag is visible on the student's record and can be removed.
- **AC-3:** Given a student whose flag was removed, when a later matching run executes, then the student is eligible for assignment again.
- **AC-4:** Given a failed run (insufficient capacity), when the administrator flags one or more students and re-runs matching, then the new run completes with all remaining (unflagged) students assigned, and it can then be published (CR-18 flow).

**Priority:** Must | **Traces to:** CR-18, CR-19, D-50

---

## 3. MoSCoW Prioritization

| ID | Story | Priority | Rationale |
|---|---|---|---|
| US-01 | Register a school | **Must** | Without schools, nothing can be matched. No workaround. |
| US-02 | Register a student | **Must** | Core data; the service is useless without the registry. |
| US-03 | Register a driver (capacity, identity, sex, areas, availability) | **Must** | Capacity, gender, area, and time are hard constraints; identity is the parent's primary need. |
| US-04 | Run annual matching | **Must** | The core promise (assignment + optimization). |
| US-05 | Review and publish report | **Must** | Prevents un-finalized plans reaching parents/drivers. |
| US-06 | Tweak assignments mid-year | **Should** | Workaround exists (manual handling); litmus test → Should. Direction-scope semantics fixed by D-48; re-run supersession fixed by D-49. |
| US-07 | Driver views roster | **Must** | Driver cannot operate without knowing whom/order/when. |
| US-08 | Parent views assignment | **Must** | The parent's stated primary need (driver/vehicle identity). |
| US-09 | Flag a student for exclusion | **Must** | The mandatory resolution path for failed runs (CR-18/CR-19). |

**MVP (confirmed at Gate 1):** US-01, US-02, US-03, US-04, US-05, US-07, US-08, US-09.
**Out of MVP (in scope of this release cycle):** US-06 (Should).

> Allocation note: the Must set is genuinely Must-heavy by the litmus test (9 small stories; delivery is useless without any Must item, including the failure-resolution path). T-shirt estimates: US-01 S, US-02 S, US-03 S, US-04 L, US-05 S, US-06 S, US-07 M, US-08 M, US-09 S.

---

## 4. Non-Functional Requirements (NFRs)

### NFR-01 — Matching run performance
- **Scale/Meter:** Hours from trigger to complete report; timed against 500 students / 50 drivers / 10 schools / 2 shifts, one city (reference environment per A-12).
- **Goal:** ≤ 3 h. **Stretch:** ≤ 1 h. **Fail (> contractual bound, Gate 7):** > 24 h → abort with documented failure report, publication blocked (D-22).
- **Rationale:** runs occur once or twice a year, off the critical path (D-16); exact optimality at all scales was chosen by the product owner (D-21).

### NFR-02 — Dashboard responsiveness
95th percentile over 100 consecutive loads. **Goal:** ≤ 3 s. **Fail:** > 8 s.

### NFR-03 — Export file generation
Largest dataset export. **Goal:** ≤ 10 s. **Fail:** > 60 s.

### NFR-04 — Access control & data protection
Parents see only their own children's assignments; drivers only their own rosters; administrators all. Authentication required for all roles; children's addresses sensitive. **Goal:** 0 exposures. **Fail:** any exposure.

### NFR-05 — Availability
Core hours 05:30–09:00 and 12:00–14:30 local (re-validate against the shift model at Phase 6 — D-33). **Goal:** ≥ 99%. **Wish:** 99.9%. **Fail:** < 97%.

### NFR-06 — Accessibility
WCAG 2.1 AA on text legibility and keyboard navigation of main flows (register, review, view roster, view assignment). **Fail:** unreadable at 200% zoom or non-keyboard-operable core flows.

### NFR-07 — Localization (RTL)
Persian (Farsi), full RTL layout support across dashboards and exported files (OQ-03 → D-13). **Fail:** LTR-only rendering breaking RTL anywhere.

### NFR-08 — Budget (Budget gate) — APPROVED
- **Build ceiling:** **$20,000** (≈100 person-days at the $200/day estimation basis).
- **Ceiling basis (D-46):** cumulative amendment envelope — base build 30–40 pd + MOKEAB amendment 8–16 pd + driver-allocation amendments 20–40 pd ⇒ ≈ 58–96 pd (**~$11,600–19,200**); the $20,000 ceiling covers the stacked high end with ≈4% headroom.
- **Cost-compression lever (optional):** a 2–3-day solver design spike (model formulation + tie-break strategy, ≈$400–600), expected to pull actual spend toward the range floor; actuals re-checked at release (Gate 7). *(Executed 2026-08-31 — see `spikes/solver-design/`.)*
- **Estimate assumption:** the dominant range term (allocation core, 7–15 pd) assumes an off-the-shelf exact engine (CP/MIP class) can encode CR-26's pairwise turnaround and D-45's lexicographic tie-breaks without custom search — plausible, unverified until the optional design spike runs; the spike doubles as its verification.
- **Operating ceiling:** **$30/month** hosting + tools (≈$400/year incl. domain).
- **Re-check trigger (Gate B):** any scope change re-enters this check before Phase 3 spend and again at release (Gate 7).

### NFR-09 — Robustness (error handling)
Every invalid submission rejected with a clear message and no partial state. **Fail:** data corruption or silent acceptance.
**Duplicates (D-52):** duplicate registrations — student with the same **کد ملی**, school with the same **name + coordinates** (D-26), driver with the same **plate number or کد ملی** — are rejected with a message **naming the existing record**.

---

## 5. Traceability Matrix

| Story | Confirmed requirements |
|---|---|
| US-01 | CR-01, CR-08, D-30, D-52 |
| US-02 | CR-02, CR-16, CR-21, D-33, D-52, D-53 |
| US-03 | CR-03, CR-04, CR-21, CR-22, CR-23, CR-24, CR-25, CR-26, D-02, D-51, D-52 |
| US-04 | CR-05, CR-06, CR-07, CR-08, CR-21, CR-22, CR-23, CR-24, CR-26, D-40, D-47 |
| US-05 | CR-09, CR-10, D-27 |
| US-06 | CR-11, CR-16, D-48, D-49 |
| US-07 | CR-08, CR-12, CR-24 |
| US-08 | CR-10, CR-20, D-02, D-51 |
| US-09 | CR-18, CR-19, D-50 |

Coverage check: CR-13 (no notifications), CR-14 (no absence reporting), CR-15 (no driver-absence handling), and CR-17 (scale) are explicitly out of story scope by decision — recorded in `discovery.md` as decisions/NFR inputs, not stories.
