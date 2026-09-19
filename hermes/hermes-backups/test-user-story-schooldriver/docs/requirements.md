# Requirements — School Driver Platform

> **Project:** Smart transportation platform for school students (daily home ↔ school shuttles)
> **Phase:** 1 — Requirements (user stories, MoSCoW, NFRs)
> **Status:** **v1.1 — BASELINE LOCKED** (originally locked 2026-08-25, Gate 1; **amended 2026-09-05** — five PO rulings applied, see §6). Supersedes all DRAFT versions and v1.0; any further change requires a formal amendment (version increment + §6 changelog entry + ripple sweep over affected criteria).
> **Companion artifact:** `docs/requirements/discovery.md` (confirmed requirements, assumptions, decisions, open questions)

---

## 1. Scope in one paragraph

A system where an administrator registers schools (single-sex, with shifts), accepts **parent-initiated student registrations** (home addresses, sex validated against the school, one shift), and registers drivers (capacities, vehicle identity, sex, service areas, service hours per shift and direction); triggers an annual matching run that assigns every student to a driver per shift and direction while minimizing total driving distance per direction run (hard capacity, gender, service-area, and time-window constraints; no school pre-assigned — matching allocates runs per school and a driver may serve multiple schools subject to the same-day turnaround rule, CR-26); reviews and publishes the resulting plan; and fine-tunes assignments mid-year without re-running matching. Parents view their child's assigned driver/vehicle identity; drivers view per-shift, per-direction rosters (students, pickup order, times) — via dashboard and exported file. No notifications, no pickup tracking, no same-day handling.

---

## 2. User Stories

### US-01 — Register a school
**As an** administrator,
**I want to** register each school with its name, location, sex (single-gender), and one or more shifts,
**so that** students can be tied to the correct school, gender rules can be enforced, and per-shift run times are derived correctly.

**Acceptance criteria:**
- AC-1: Given a school with name, location, sex, and at least one shift (start + end time), when the administrator submits the registration, then the school appears in the school list with all fields intact.
- AC-2: Given a school record submitted without a shift, when the administrator submits it, then the submission is rejected with a message indicating at least one shift is required.
- AC-3: Given two schools registered with different shift times, when the administrator views the list, then each school shows its own shift times (times do not overwrite each other).
- AC-4: Given a school whose shift time is later changed and saved, when a matching run completes after that change, then the runs for that school's students use the new shift time.
- AC-5: Given a school record missing the address, the coordinates, or both (both required per D-26), when the administrator submits it, then the submission is rejected with a message naming the missing component(s).
- AC-6: Given a school record without a sex, or with a value other than male/female, when the administrator submits it, then the submission is rejected with a message that a valid sex is required (D-30).
- AC-7: Given a school registration whose name and coordinates match an existing school (duplicate: same name + coordinates per D-26), when the administrator submits it, then it is rejected with a message naming the existing record (OQ-13 → D-52, NFR-09).

**Priority:** Must | **Traces to:** CR-01, CR-08, D-30, D-52 | **Source:** Discovery session 2026-08-15

---

### US-02 — Register a student
**As an** administrator,
**I want to** process a **parent-initiated student registration** (the parent initiates; the student record is created when the administrator/school accepts it — D-53) with a home location (address and coordinates, provided by the parent — D-28), a **national ID (کد ملی) as the unique student key (D-52)**, exactly one school, a sex matching the school's sex, and exactly one shift of that school,
**so that** the matcher can plan a pickup at the correct location for the correct school, shift, and gender group.

**Acceptance criteria:**
- AC-1: Given a parent-initiated student registration whose home address and coordinates were provided by the parent (typed address + map-selected location per D-28), carrying a **valid 10-digit national ID (کد ملی) (D-52)**, one selected school, and one shift of that school, when the administrator/school accepts it, then the student appears in the registry tied to exactly that school and shift, keyed on the کد ملی.
- AC-2: Given a student record missing the home address, the coordinates, or both (both required per D-26), when the administrator submits it, then it is rejected with a message naming the missing component(s).
- AC-3: Given a student record without a selected school, when the administrator submits it, then it is rejected with a message that a school is required.
- AC-4: Given a student whose school is later changed and saved, when the registry is viewed, then the student is tied to exactly one school (the new one) **and re-validated against the new school** — sex must equal the new school's sex (D-30), and a shift of the new school must be selected (D-33); if either fails, the change is rejected with the AC-5/AC-6 messages (V4-09).
- AC-5: Given a student record whose sex differs from the selected school's sex, when the administrator submits it, then it is rejected with a message that the student's sex must equal the school's sex (D-30).
- AC-6: Given a student record without a selected shift, or with a shift that does not belong to the selected school, when the administrator submits it, then it is rejected with a message that a valid shift of that school is required (D-33).
- AC-7: Given a student registration whose کد ملی matches an existing student's (duplicate: same national ID), when the administrator submits it, then it is rejected with a message naming the existing record (OQ-13 → D-52, NFR-09).

**Priority:** Must | **Traces to:** CR-02, CR-16, CR-21, D-33, D-52, D-53 | **Source:** Discovery session 2026-08-15

---

### US-03 — Register a driver with capacity, origin, vehicle identity, sex, service areas, and service availability
**As an** administrator,
**I want to** register drivers along with their vehicle capacities, origin (home address), vehicle identity details, sex, service areas, and per-shift/per-direction service availability,
**so that** matching plans respect each driver's carrying limit, gender rule, area coverage, time availability, and parents can recognize the vehicle that will pick up their child.

*Scope note (F5/v3 + MOKEAB D-29): US-03 intentionally carries a large acceptance set — driver creation (AC-1…6), the capacity-edit guard (AC-7, D-20), the post-publication identity edit (AC-8, D-25), the MOKEAB fields (AC-9…12: sex, service areas, shift-direction availability), and the availability-selection guards (AC-13/AC-14, v0.13 amendment D-35…D-38). Accepted as one story; recorded deviation from the 3–7 range.*

**Acceptance criteria:**
- AC-1: Given a driver record with a capacity of 8, an origin (home address), and vehicle identity details, when the administrator submits it, then the driver's record shows capacity 8, the origin, and the identity details.
- AC-2: Given a driver record with capacity 0 or missing, when the administrator submits it, then it is rejected with a message that a positive capacity is required.
- AC-3: Given drivers registered with capacities 4, 8, and 11, when the registry is viewed, then each driver keeps their own capacity.
- AC-4: Given a registered driver, when their record is viewed before any matching run, then no school is shown as pre-assigned (the school is determined by matching).
- AC-5: Given a driver record that includes vehicle identity details — plate number, model, and color (OQ-05, resolved) — plus the **driver's name and phone number** (OQ-12 → D-51), when the administrator submits it, then the details are stored with the driver's record and appear in the parent's view after publication (US-08).
- AC-6: Given a driver record submitted without plate number, model, color, the **driver's name, the driver's phone number, the driver's national ID (کد ملی — D-52)**, or origin (home address), when the administrator submits it, then it is rejected with a message listing the missing fields, and no partial record is saved.
- AC-7: Given a driver whose capacity edit would drop below their current assignment count on an approved/published plan, when the administrator saves the edit, then the edit is rejected with a capacity message and the existing capacity is unchanged (D-20).
- AC-8: Given a driver whose vehicle identity is edited after publication, when the administrator saves the edit and a parent opens the dashboard, then the parent sees the **current** identity (D-25).
- AC-9: Given a driver record without a sex, or with a value other than male/female, when the administrator submits it, then it is rejected with a message that a valid sex is required (D-29).
- AC-10: Given a driver record without at least one service area (one or more predefined zones — D-43), when the administrator submits it, then it is rejected with a message that at least one service zone is required (D-31).
- AC-11: Given a driver recorded with a shift-direction availability entry (DriverShift) that has no direction selected (neither to-school nor from-school), when the administrator saves it, then it is rejected with a message that at least one direction is required (CR-24).
- AC-12: Given a driver with one or more selected shifts saved, when the availability entry is viewed, then each entry displays its **derived service window** — the selected shift's start and end (D-42/D-47); no manually entered window field exists at MVP. *(Retargeted v0.16, review v5 V5-01 — the former missing-window rejection folds into AC-13, since windows derive from selection; CR-23 containment applies to explicit windows only, post-MVP.)*
- AC-13: Given a driver availability entry that names no selected shift, when the administrator saves it, then it is rejected with a message that at least one shift must be selected; an entry consists solely of selected shifts plus served direction(s) and never names a school (D-35, CR-03).
- AC-14: Given a driver who selects two shifts with overlapping clock windows, when the administrator saves the entry, then it is rejected (impossible under every school allocation — CR-26(i)); given two shifts whose raw windows are disjoint but whose buffered windows [S − T, E + T] intersect **and whose sets of adopting schools share no common school**, when the administrator saves the entry, then it is likewise **rejected** (impossible under every allocation — CR-26(ii)); and given such a buffered-intersect pair sharing at least one common school, when the administrator saves the entry, then it is accepted with a warning that the two runs are compatible only if both are allocated to a common school of the two shifts (at least one shared adopting school), with T read from configuration (MIN_TURNAROUND_MINUTES — D-37). *(Third case added v0.16, review v5 V5-03.)*
- AC-15: Given a driver registration whose plate number or کد ملی matches an existing driver's (duplicate: same plate **or** same national ID), when the administrator submits it, then it is rejected with a message naming the existing record (OQ-13 → D-52, NFR-09). *(Added v1.1, D-52.)*

**Priority:** Must | **Traces to:** CR-03, CR-04, CR-21, CR-22, CR-23, CR-24, CR-25, CR-26, D-02, D-51, D-52 | **Source:** Discovery session 2026-08-15

---

### US-04 — Run annual matching (per shift and direction)
**As an** administrator,
**I want to** trigger a matching run that assigns every student to a driver for each shift and direction, minimizing total driving distance per direction run,
**so that** the school year starts with a complete, efficient, compliant pickup plan.

*Scope note (V2-10 + MOKEAB D-29): US-04 intentionally carries an extended acceptance set — the core capability, feasibility/failure/degenerate paths (IR-01, IR-17), and the new gender/area/time constraints (CR-21/22/23). Accepted as one story; recorded deviation from the 3–7 range.*

**Acceptance criteria:**
- AC-1: Given a registry where a **feasible assignment exists** (per school and shift: the shift's students can be covered by the drivers allocated to that school, respecting per-driver capacity, same-day run compatibility (CR-26), gender rule CR-21, service-area rule CR-22, and time rule CR-23), when the administrator triggers matching, then every registered non-flagged student is assigned to exactly one driver **for each of the shift's directions**, and flagged students appear marked as excluded (CR-19).
- AC-2: Given a driver with capacity C for a direction, when matching completes, then that driver is assigned at most C students **for that direction run** (A-13, confirmed as D-34).
- AC-3: Given students tied to different schools, when matching completes, then each run assigned to a driver serves students of exactly one school, and every pair of same-day runs allocated to that driver satisfies the compatibility rules (CR-26: non-overlap; ≥ 2 × MIN_TURNAROUND_MINUTES gap between runs of different schools; back-to-back allowed within one school) — a driver may serve multiple schools across runs (D-36).
- AC-4: Given a small dataset whose optimal plan is known (verified by exhaustive search), when matching runs, then the report's total distance equals that optimal value **for each direction run**. The **exact-optimality guarantee applies at every scale** (D-21); small-instance exhaustive verification is the acceptance meter for the guarantee.
- AC-5: Given the report after matching, when the administrator opens it, then it shows the total driving distance **per direction run** and, for at-scale runs, the recorded optimality evidence (certificate of proven zero gap per D-22).
- AC-6: Given a registry where **no feasible assignment exists** for a shift or direction (e.g., global capacity is sufficient but one school's students exceed what the drivers that can serve that school can carry, or no eligible driver exists due to gender/area/time rules), when the administrator triggers matching, then no partial plan is produced for publication; instead the run reports the failure with the complete data: the list of unassigned students, the shortfall per school/shift/direction (including gender, area, and time causes), and the assignments that could not be made (CR-18).
- AC-7: Given the turnaround dataset (School A: 1 student with shift 07:00–12:00; School B: 1 student with shift 12:00–19:00; a single driver available for both shifts, capacity ≥ 1, **of the same sex as both schools' students (D-30), whose predefined zones cover both schools and both homes (CR-22/D-43), and who selected both shifts with the needed directions (D-47)** — total capacity exceeds total demand, yet the A-from-school run ends 12:00 and the B-to-school run starts 12:00 at a **different school** with a 0-minute gap < 2 × MIN_TURNAROUND_MINUTES), when the administrator triggers matching, then the run fails exactly as described in AC-6 (no invalid plan is produced; the report names the CR-26 turnaround cause). *(Dataset retargeted v0.13/D-36; eligibility preconditions added v0.16, review v5 V5-02 — the fixture must fail on turnaround alone, not gender/area.)*
- AC-8: Given a degenerate registry (zero students, zero drivers, or every student flagged for exclusion), when the administrator triggers matching, then the run completes with an empty or all-excluded report and raises no failure.
- AC-9: Given a girls-only school shift and a male driver who is the only driver covering it, when the administrator triggers matching, then the run reports the shift as infeasible with a gender-cause shortfall (CR-21) — a male driver is never assigned female students (AC-9a: no assignment violates the gender rule; verified for all pairs in the report).
- AC-10: Given a student whose home or school lies outside every candidate driver's service area, when the administrator triggers matching, then those drivers are not assigned to that student (CR-22) and, if no eligible driver remains, the run reports the area-cause shortfall per AC-6.
- AC-11: Given a shift-direction that **no driver selected** (MVP eligibility is selection-based — D-47), when matching runs and students demand that direction, then no driver is allocated to it and the run reports the shortfall per AC-6 with cause "no eligible driver selected this shift-direction." *(Replaced v0.16, review v5 V5-01 — the former boundary-containment test presupposed explicit windows and moves with CR-23's scoped form to post-MVP.)*
- AC-12: Given a driver whose selected (shift, direction) entries exceed what matching allocates, when a successful run completes, then the driver keeps only the allocated runs and the report lists the unused selections as **unallocated availability** — no error is raised (selection is capability, not obligation — D-40).

**Priority:** Must | **Traces to:** CR-05, CR-06, CR-07, CR-08, CR-21, CR-22, CR-23, CR-24, CR-26, D-40, D-47 | **Source:** Discovery session 2026-08-15

---

### US-05 — Review and publish the matching report
**As an** administrator,
**I want to** review the matching report and explicitly approve it before anything goes live,
**so that** parents and drivers only ever see finalized assignments.

**Acceptance criteria:**
- AC-1: Given a completed matching run, when the administrator opens the report, then every assignment (student, driver, school, shift, direction) and the per-direction total distances are visible for review.
- AC-2: Given a report that has not been approved, when a parent or driver views the dashboard, then no assignment information is shown.
- AC-3: Given a reviewed report, when the administrator approves it, then assignments become visible to the corresponding parents and drivers (dashboard and exported file).
- AC-4: Given a matching run that failed to assign every student for some shift or direction, when the administrator reviews the failure report, then the unassigned students and the shortfall per school/shift/direction are clearly flagged, and publication of any partial plan is blocked until the failure is resolved (add drivers + re-run, or flag students — CR-18/CR-19).
- AC-5: Given a registry or capacity change made after a matching run completed but before the report is approved, when the administrator attempts to approve the report, then approval is blocked with a message stating the report no longer matches the registry and directing the administrator to re-run matching (D-23), tweak assignments (CR-16), or revert the change (D-27).

**Priority:** Must | **Traces to:** CR-09, CR-10, D-27 | **Source:** Discovery session 2026-08-15

---

### US-06 — Tweak assignments without re-running matching
**As an** administrator,
**I want to** change one student's assigned driver and have it take effect immediately,
**so that** I can respond to mid-year changes without disturbing the rest of the plan.

**Acceptance criteria:**
- AC-1: Given an approved plan, when the administrator reassigns a student to a different driver and saves, then the change is stored immediately.
- AC-2: Given a saved reassignment, when the affected parent and drivers view their dashboards, then the parent sees the new driver, the new driver's roster includes the student, and the previous driver's roster no longer lists the student.
- AC-3: Given a reassignment that would put the target driver over capacity, when the administrator attempts to save it, then the change is rejected with a capacity message and no assignment changes.
- AC-4: Given a saved reassignment, when other students' assignments are inspected, then none of them changed (the tweak did not re-run matching).
- AC-5: Given a reassignment whose administrator-selected direction scope is **to-school only**, when it is saved, then the student's from-school assignment is unchanged and the to-school assignment is validated against the target driver's eligibility and capacity for that direction (D-47, D-34, CR-21, CR-22, CR-26); from-school-only scoping is symmetric; scope **both** applies the change to both directions. *(Added v0.18, D-48.)*
- *(Direction-scope resolved by **D-48** (2026-08-25): chosen per tweak — to-school only / from-school only / **both (default)** — validated per direction; see AC-5. The former "may a reassignment change the driver's school" question was dissolved by D-36 — drivers may serve any mix of schools subject to CR-26.)*
- *(Re-run vs tweaks resolved by **D-49** (2026-09-05): a new matching run **supersedes** the previous published plan — the old plan stops being the published one; prior US-06 tweaks are **not automatically carried** into the re-run's plan — the administrator may re-apply tweaks manually for any assignment still valid under the new plan; the trigger screen shows a supersede warning before an in-flight re-run.)*

**Priority:** Should | **Traces to:** CR-11, CR-16, D-48, D-49 | **Source:** Discovery session 2026-08-15

---

### US-07 — Driver views roster per shift and direction
**As a** driver,
**I want to** see, for each shift and direction I serve, my assigned students with pickup order and times,
**so that** I know exactly whom to pick up, in what order, and when — for the to-school run and the from-school run.

**Acceptance criteria:**
- AC-1: Given a published plan, when the driver opens the dashboard, then the roster shows, per shift and per direction: the to-school run's students in pickup order, each with a pickup time; and the from-school run's school-departure time plus its students in drop-off order, each with a drop-off time (D-39).
- AC-2: Given a published plan, when the driver exports the roster file, then the file contains the same students, order, and times as the dashboard.
- AC-3: Given a published plan where a driver serves only the to-school direction of a shift, when the driver views the dashboard, then only the to-school roster is shown for that shift (no from-school roster is fabricated) (CR-24).
- AC-4: Given a driver with no assignments in a run, when the driver opens the dashboard, then the roster is empty and shows no other driver's students.

**Priority:** Must | **Traces to:** CR-08, CR-12, CR-24 | **Source:** Discovery session 2026-08-15

---

### US-08 — Parent views child's assignment (driver/vehicle identity)
**As a** parent/guardian,
**I want to** see my child's assigned driver and vehicle identity,
**so that** I can recognize who is coming to pick up my child.

*Scope note (D-17): this story intentionally merges assignment viewing (AC-1…4) with parent account provisioning/activation (AC-5…7) for the MVP — the account lifecycle is small and is the precondition for any viewing. A split into a separate account story is deferred; revisit if the account flow grows.*

**Acceptance criteria:**
- AC-1: Given a published assignment for my child, when I open the dashboard, then I see my child's name, school, shift, assigned driver (per direction) with the **driver's name and phone number**, and vehicle identity — **car model, plate number, and color** — (identity set per OQ-05/CR-03/D-15, extended by **OQ-12 → D-51**).
- AC-2: Given a published assignment for my child, when I export the assignment file, then it contains the same driver/vehicle identity information.
- AC-3: Given my child's assignment has not been published, when I open the dashboard, then no assignment information is shown.
- AC-4: Given a parent with two children assigned to different drivers, when I open the dashboard, then each child's assignment is shown separately.
- AC-5: Given a parent whose account was auto-created from school-provided data, when they sign in, then the account is active and they can view their child's assignment.
- AC-6: Given a parent without an account, when they request account registration and the administrator/school accepts the request, then the account becomes active and the parent can view the assignment.
- AC-7: Given a parent whose registration request has not yet been accepted, when they attempt to sign in, then they cannot access any assignment information.

**Priority:** Must | **Traces to:** CR-10, CR-20, D-02, D-51 | **Source:** Discovery session 2026-08-15

---

### US-09 — Flag a student for exclusion from assignment
**As an** administrator,
**I want to** flag a student so they are excluded from a matching run,
**so that** I can resolve capacity failures or handle students who don't need transport without corrupting the plan.

**Acceptance criteria:**
- AC-1: Given a student flagged as excluded, when a matching run executes, then the student is not assigned to any driver and appears in the run's report marked as flagged/excluded.
- AC-2: Given a flagged student, when the administrator views the registry, then the flag is visible on the student's record and can be removed.
- AC-3: Given a student whose flag was removed, when a later matching run executes, then the student is eligible for assignment again.
- AC-4: Given a failed run (insufficient capacity), when the administrator flags one or more students and re-runs matching, then the new run completes with all remaining (unflagged) students assigned, and it can then be published (CR-18 flow).

**Priority:** Must | **Traces to:** CR-18, CR-19, D-50 | **Source:** OQ-01 resolution, 2026-08-15

---

## 3. MoSCoW Prioritization

| ID | Story | Priority | Rationale (litmus test) |
|---|---|---|---|
| US-01 | Register a school | **Must** | Without schools, nothing can be matched. No workaround. |
| US-02 | Register a student | **Must** | Core data; the service is useless without the registry. |
| US-03 | Register a driver (capacity, identity, sex, areas, availability) | **Must** | Capacity, gender, area, and time are hard constraints; identity is the parent's primary need. No registry → no plan. |
| US-04 | Run annual matching | **Must** | The core promise (assignment + optimization). |
| US-05 | Review and publish report | **Must** | Prevents un-finalized plans reaching parents/drivers. |
| US-06 | Tweak assignments mid-year | **Should** | Workaround exists (manual/paper handling); painful but usable without. Litmus test → Should. |
| US-07 | Driver views roster | **Must** | Driver cannot operate without knowing whom/order/when. |
| US-08 | Parent views assignment | **Must** | The parent's stated primary need (driver/vehicle identity). |
| US-09 | Flag a student for exclusion | **Must** | The mandatory resolution path for failed runs (CR-18/CR-19, OQ-01). Without it, an infeasible run dead-ends. |

**MVP (proposed Must set — provisional, final only after human confirmation):**
US-01, US-02, US-03, US-04, US-05, US-07, US-08, US-09.
**Out of MVP (but in scope of this release cycle):** US-06 (Should).

> ⚠️ Allocation note: the Must set here is large relative to the 60/20/20 guideline (the skill recommends ≤60% of effort as Must). This requirement set is small (9 stories) and genuinely Must-heavy by the litmus test — the delivery is useless without any of the Must items, including the failure-resolution path. Rough T-shirt estimates for the planning phase: US-01 S, US-02 S, US-03 S, US-04 L, US-05 S, US-06 S, US-07 M, US-08 M, US-09 S. The human is the final authority on the MVP set.

---

## 4. Non-Functional Requirements (NFRs)

### NFR-01 — Matching run performance
- **Scale:** Hours from admin trigger to a complete, reviewable report (all shifts and directions).
- **Meter:** Timed run against a reference dataset of 500 students / 50 drivers / 10 schools / 2 shifts, one city (reference environment per A-12).
- **Goal:** ≤ 3 hours. **Stretch:** ≤ 1 hour. **Fail:** > 24 hours.
- **Contract status:** Goal/Stretch are targets; **Fail is the contractual bound** (Gate 7 acceptance).
- **Fail-breach behavior (D-22):** a run exceeding 24 h is aborted, a documented failure report is produced, publication is blocked, and the administrator may re-run or adjust inputs.
- **Rationale (decisions D-16 + D-21, 2026-08-15):** matching runs only once or twice a year and is not on the critical path for parents or drivers; the product owner chose **exact optimality at all scales** (D-21), which can take hours on the reference dataset — an overnight run is acceptable. The **Fail** threshold exists to catch pathological behavior (a run that never terminates or degenerates far beyond expectation).

### NFR-02 — Dashboard responsiveness
- **Scale:** Seconds from opening a dashboard page to usable content.
- **Meter:** Automated check, 95th percentile over 100 consecutive loads.
- **Goal:** ≤ 3 seconds. **Fail:** > 8 seconds.
- **Source:** Parents and drivers use dashboards daily.

### NFR-03 — Export file generation
- **Scale:** Seconds from requesting an export to a downloadable file.
- **Meter:** Timed export of the largest dataset (500 students, full plan).
- **Goal:** ≤ 10 seconds. **Fail:** > 60 seconds.

### NFR-04 — Access control & data protection
- **Scale:** Fraction of cross-account data exposures in tests.
- **Meter:** Access-control test suite; manual review.
- **Goal:** 0 exposures. **Fail:** any exposure.
- **Rule:** A parent sees only their own children's assignments; a driver sees only their own roster; an administrator sees all. Authentication required for all roles; children's addresses are treated as sensitive.

### NFR-05 — Availability
- **Scale:** Percent of uptime during school-day core hours.
- **Core hours:** 05:30–09:00 and 12:00–14:30 local (to be re-validated against the school shift model at Phase 6 — D-33).
- **Meter:** Uptime monitoring over the school year.
- **Goal:** ≥ 99% during core hours. **Fail:** < 97%. **Wish:** 99.9%.
- **Rationale:** The transport windows are when parents/drivers actually depend on the system.

### NFR-06 — Accessibility
- **Scale:** WCAG 2.1 conformance level on the three dashboards (parent, driver, admin).
- **Meter:** Automated scan + manual spot check of the main flows.
- **Goal:** AA on text legibility and keyboard navigation of the main flows (register, review, view roster, view assignment). **Fail:** text not readable at 200% zoom or core flows not keyboard-operable.

### NFR-07 — Localization (RTL)
- **Scale:** UI language(s) and text-direction support at MVP.
- **Goal:** 1 language — **Persian (Farsi)** — with **full RTL layout support** (text direction, alignment, and numerals rendered correctly across all dashboards and reports). (OQ-03, resolved → D-13.)
- **Fail:** LTR-only rendering that breaks RTL text/alignment in any of the three dashboards or the exported files.
- **Meter:** Visual/manual check of every screen + exported file in Farsi.

### NFR-08 — Budget (Budget gate) — APPROVED
- **Build ceiling:** **$20,000** (≈100 person-days at the $200/day estimation basis). **Re-baselined by product owner 2026-08-23 (D-46 — Gate-B re-check executed); corrected $18,000 → $20,000 on 2026-08-25 (V6-01, review v6 — see ceiling-basis note).** Supersedes the original **$6,000** ceiling (approved 2026-08-15, OQ-02), which priced the pre-amendment scope only.
- **Ceiling basis (D-46):** cumulative amendment envelope — base build 30–40 pd + MOKEAB amendment 8–16 pd (V4-13) + driver-allocation amendments 20–40 pd (estimate of 2026-08-23) ⇒ ≈ 58–96 pd (**~$11,600–19,200**); the $20,000 ceiling covers the stacked high end with ≈4% headroom. *(Correction, v0.18/V6-01, 2026-08-25: the formerly stated high-end conversion "~$17,200" under the $18,000 ceiling — with "~5% headroom" — was arithmetically wrong: 96 pd × $200/day = $19,200 exceeded that ceiling. Review v5 §3.1's "arithmetic checks out" attestation is corrected by review v6 V6-01.)*
- **Cost-compression lever (optional, D-46):** a 2–3-day solver design spike (model formulation + tie-break strategy, ≈$400–600) is expected to pull actual spend toward the range floor; actuals are re-checked against the ceiling at release (Gate 7).
- **Operating ceiling:** **$30/month** hosting + tools (≈$400/year incl. domain). **Approved 2026-08-15.**
- **Amendment note (V4-13, historical):** the MOKEAB scope amendment (D-29…D-33) added an estimated **+8–16 person-days (~$1,600–3,200)**; retained as part of the envelope-growth audit trail.
- **Amendment note (v0.13/v0.14, historical — estimated 2026-08-23):** the driver-allocation amendments add an estimated **+20–40 person-days (~$4,000–8,000** at the $200/day basis**)**: availability-model rework 3–5.5, allocation-core reformulation (global solve + CR-26 constraints) 7–15, NFR-01 performance re-validation 2–5, determinism/tie-break phases 2–4, from-school geometry + rosters 2–5, report additions 1–2, routing-engine self-hosting ops 1–2, regression/tests/docs 2–4. Assumptions: off-the-shelf exact solver engine (per D-21 Gate-B note); routing *integration* inside base scope (only self-hosting ops counted).
- **Estimate assumptions (review v5 V5-06):** the dominant range term (allocation core, 7–15 pd) assumes an off-the-shelf exact engine (CP/MIP class) can encode CR-26's pairwise turnaround and D-45's lexicographic tie-breaks **without custom search** — plausible, unverified until the optional design spike runs; the spike doubles as its verification.
- **Re-check trigger (Gate B):** any scope change re-enters this check before Phase 3 spend and again at release (Gate 7).

### NFR-09 — Robustness (error handling)
- **Scale:** Behavior on invalid input (missing fields, capacity 0, duplicate registration attempts).
- **Meter:** Error-path test suite.
- **Goal:** Every invalid submission is rejected with a clear message and causes no partial state. **Fail:** data corruption or silent acceptance.
- **Duplicates (OQ-13 → D-52):** duplicate registrations — student with the same **کد ملی**, school with the same **name + coordinates** (D-26), driver with the same **plate number or کد ملی** — are rejected with a message **naming the existing record**.

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

Coverage check: CR-13 (no notifications), CR-14 (no absence reporting), CR-15 (no driver-absence handling), and CR-17 (scale) are **explicitly out of story scope by decision** — they are recorded in `discovery.md` as decisions/NFR inputs, not as stories (a story would contradict the confirmed decision).

---

## 6. Baseline Status

- **Status:** **v1.1 — BASELINE LOCKED** (originally locked 2026-08-25, Gate 1; **amended 2026-09-05**). (v1.0 → v1.1: **authorized amendment, 2026-09-05 — five PO rulings applied; provenance: PO iman, chat** — OQ-10 → **D-49** (a new matching run supersedes the previous published plan — the old plan stops being published; US-06 tweaks not auto-carried — the admin may re-apply manually; supersede warning on re-trigger per the UX package; ripple: US-06 note + trace), OQ-11 → **D-50** (flag/removal propagates to live rosters and parent views immediately; no matching re-run — CR-16/D-23 unchanged; ripple: CR-19, US-09 trace), OQ-12 → **D-51** (driver identity to parents = driver name, car model, plate number, driver's phone number — extends the D-15/CR-03 identity set and the CR-10/US-08 parent view; ripple: US-03 AC-5/AC-6, US-08 AC-1, D-02, D-15, CR-03), OQ-13 → **D-52** (student unique key = national ID (کد ملی), 10-digit, format-validated, unique; duplicates — student same کد ملی, school same name + coordinates (D-26), driver same plate or same کد ملی — each rejected naming the existing record (NFR-09); assignment/flag/export key off کد ملی; ripple: CR-02, CR-03, A-10, US-01 AC-7 (new), US-02 AC-7 (new), US-03 AC-6/AC-15 (new), NFR-09), OQ-15 → **D-53** (student registration initiated by the parent; becomes a student record when the administrator/school accepts — mirrors the CR-20 parent-request pattern; ripple: US-02 intro/AC-1, CR-02, D-28, §1 scope paragraph). Traceability matrix extended (US-01/02/03/06/08/09 rows). Reader Edition regenerated to track v1.1 (`requirements-consolidated.md` + `discovery-consolidated.md`, headers cite "Derived from baseline v1.1"). **Verification pending:** independent amendment review pass to be commissioned by the dispatcher (Rule 7 — author ≠ verifier).) (v0.18 → v1.0: **Gate-1 lock executed** — verification review v7: PASS, zero new findings; Gate-1 conditions discharged: assumptions confirmed, build ceiling $20,000 approved post-correction, OQ-06 closed via D-48.) (v0.17 → v0.18: **review-v6 remediation, PO dispositions 2026-08-25** — V6-01 budget-arithmetic correction (ceiling $18,000 → $20,000 ≈100 pd @ $200/day; envelope high end corrected to $19,200 = 96 pd × $200/day; headroom ≈4%; NFR-08/D-46 amended in place; review v5 §3.1 attestation corrected); V6-02 resolved by PO answer: OQ-06 → **D-48** (tweak direction-scope selected per tweak: to-school only / from-school only / both-default, validated per direction), US-06 gains AC-5, trace line + matrix row extended with D-48, trigger lines aligned ("before US-06 build" no longer gates the lock); V6-03 mechanical: A-01…A-11/A-14…A-16 expiry cells set to ✅ Confirmed (Gate 1, 2026-08-25); V6-04 AC-14 warning wording ("a common school"); V6-05 US-08 AC-1 "(OQ-05, resolved)". Ripple sweep executed over all changed wording.) Previous — v0.16 → v0.17: **product owner Gate-1 rulings, 2026-08-25** — A-02 restated as "dismissal time = end time of the relevant shift" and confirmed (ripple sweep: no other artifact text cites dismissal time); A-01/A-03…A-11/A-14…A-16 confirmed unchanged at Gate 1; Rule-7 disposition: review v5 ratified-with-condition, a **contextually fresh confirmation pass (review v6)** commissioned before lock; SM-01 prior confirmation stands. No story/CR/NFR wording changed in this cycle.) Previous: v0.15 → v0.16 review-v5 remediation (PO, 2026-08-23) — V5-01 Major resolved via **D-47** (selection-based MVP eligibility; CR-23 scope-restricted to explicit windows; US-03 AC-12 retargeted to derived-window display; US-04 AC-11 replaced with selection-shortfall test), V5-02 (US-04 AC-7 eligibility preconditions), V5-03 (US-03 AC-14 third case: buffered conflict with no common school = reject), V5-04 (stale pointers: CR-07→D-44, D-31→D-43, US-04 AC-2→D-34), V5-05 (CR-08 evaluated-separately/decided-globally wording + D-21 decomposition clause), V5-06 (NFR-08 solver-assumption clause), matrix US-04 row + D-47; OQ-21 closed (review executed; Rule-7 ratification carried into the Gate-1 packet). Previous: v0.14 → v0.15 Gate-B ceiling re-baseline ($6,000 → $18,000, D-46). Earlier: v0.13 → v0.14 PO decision batch (D-39/D-34/D-40…45; SM-01 confirmed; five OQ closures) atop the v0.12 → v0.13 driver-allocation amendment and v0.11 → v0.12 review-v4 fixes.)
- **Next step (post-lock queue):** Reader Edition generated and tracking v1.1 (see changelog above); the locked originals remain untouched as the audit trail. Optional: solver design spike (D-46 lever) — **✅ DONE 2026-08-31**. Any change to the locked artifacts requires a formal amendment.
- **Blockers to Gate 1:** none — all formerly-blocking questions resolved (OQ-07/08/09 on 2026-08-15; OQ-14(c)/D-44 and OQ-16/D-43 on 2026-08-23).
- **Open non-blocking:** OQ-17 (post-MVP). *(Resolved and removed from this list: OQ-06 → D-48 (2026-08-25); OQ-10 → D-49, OQ-11 → D-50, OQ-12 → D-51, OQ-13 → D-52, OQ-15 → D-53 (all 2026-09-05).)*