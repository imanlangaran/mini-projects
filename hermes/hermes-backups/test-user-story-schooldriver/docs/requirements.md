# Requirements — School Driver Platform

> **Project:** Smart transportation platform for school students (daily home ↔ school shuttles)
> **Phase:** 1 — Requirements (user stories, MoSCoW, NFRs)
> **Status:** DRAFT v0.10 — not approved. Pending final human approval (Gate 1).
> **Companion artifact:** `docs/requirements/discovery.md` (confirmed requirements, assumptions, decisions, open questions)

---

## 1. Scope in one paragraph

A system where an administrator registers schools, students (with home addresses), and drivers (with vehicle capacities); triggers an annual matching run that assigns every student to a driver while minimizing total morning driving distance (hard capacity constraint, one school per driver, school chosen by matching); reviews and publishes the resulting plan; and fine-tunes assignments mid-year without re-running matching. Parents view their child's assigned driver/vehicle identity; drivers view their roster (students, pickup order, times) and the reversed noon return — via dashboard and exported file. No notifications, no pickup tracking, no same-day handling.

---

## 2. User Stories

### US-01 — Register a school
**As an** administrator,
**I want to** register each school with its name, location, and dismissal time,
**so that** students can be tied to the correct school and noon-return times are derived correctly.

**Acceptance criteria:**
- AC-1: Given a school with name, location, and dismissal time, when the administrator submits the registration, then the school appears in the school list with all three fields intact.
- AC-2: Given a school record submitted without a dismissal time, when the administrator submits it, then the submission is rejected with a message indicating the dismissal time is required.
- AC-3: Given two schools registered with different dismissal times, when the administrator views the list, then each school shows its own dismissal time (times do not overwrite each other).
- AC-4: Given a school whose dismissal time is later changed and saved, when a matching run completes after that change, then the noon plan for that school's students uses the new dismissal time.
- AC-5: Given a school record missing the address, the coordinates, or both (both required per D-26), when the administrator submits it, then the submission is rejected with a message naming the missing component(s).

**Priority:** Must | **Traces to:** CR-01, CR-08 | **Source:** Discovery session 2026-08-15

---

### US-02 — Register a student
**As an** administrator,
**I want to** register a student with a home location (address and coordinates, provided by the parent — D-28) and exactly one school,
**so that** the matcher can plan a pickup at the correct location for the correct school.

**Acceptance criteria:**
- AC-1: Given a student record whose home address and coordinates were provided by the parent (typed address + map-selected location per D-28) and one selected school, when the administrator submits it, then the student appears in the registry tied to exactly that school.
- AC-2: Given a student record missing the home address, the coordinates, or both (both required per D-26), when the administrator submits it, then it is rejected with a message naming the missing component(s).
- AC-3: Given a student record without a selected school, when the administrator submits it, then it is rejected with a message that a school is required.
- AC-4: Given a student whose school is later changed and saved, when the registry is viewed, then the student is tied to exactly one school (the new one).

**Priority:** Must | **Traces to:** CR-02, CR-16 | **Source:** Discovery session 2026-08-15

---

### US-03 — Register a driver with capacity, origin, and vehicle identity
**As an** administrator,
**I want to** register drivers along with their vehicle capacities, their origin (home address), and vehicle identity details,
**so that** matching plans within each driver's real carrying limit, routes can start from the driver's real origin, and parents can recognize the vehicle that will pick up their child.

*Scope note (F5, v3 review): US-03 intentionally carries 8 acceptance criteria — driver creation (AC-1…6), the capacity-edit guard (AC-7, D-20), and the post-publication identity edit (AC-8, D-25). Accepted as one story; recorded deviation from the 3–7 range.*

**Acceptance criteria:**
- AC-1: Given a driver record with a capacity of 8, an origin (home address), and vehicle identity details, when the administrator submits it, then the driver's record shows capacity 8, the origin, and the identity details.
- AC-2: Given a driver record with capacity 0 or missing, when the administrator submits it, then it is rejected with a message that a positive capacity is required.
- AC-3: Given drivers registered with capacities 4, 8, and 11, when the registry is viewed, then each driver keeps their own capacity.
- AC-4: Given a registered driver, when their record is viewed before any matching run, then no school is shown as pre-assigned (the school is determined by matching).
- AC-5: Given a driver record that includes vehicle identity details — plate number, model, and color (OQ-05, resolved) — when the administrator submits it, then the details are stored with the driver's record and appear in the parent's view after publication (US-08).
- AC-6: Given a driver record submitted without plate number, model, color, or origin (home address), when the administrator submits it, then it is rejected with a message listing the missing fields, and no partial record is saved.
- AC-7: Given a driver whose capacity edit would drop below their current assignment count on an approved/published plan, when the administrator saves the edit, then the edit is rejected with a capacity message and the existing capacity is unchanged (D-20).
- AC-8: Given a driver whose vehicle identity is edited after publication, when the administrator saves the edit and a parent opens the dashboard, then the parent sees the **current** identity (D-25).

**Priority:** Must | **Traces to:** CR-03, CR-04, D-02 | **Source:** Discovery session 2026-08-15

---

### US-04 — Run annual matching
**As an** administrator,
**I want to** trigger a matching run that assigns every student to a driver and minimizes total morning driving distance,
**so that** the school year starts with a complete, efficient pickup plan.

*Scope note (V2-10): US-04 intentionally carries 8 acceptance criteria — the core capability plus its feasibility/failure/degenerate paths (IR-01, IR-17). Accepted as one story; recorded deviation from the 3–7 range.*

**Acceptance criteria:**
- AC-1: Given a registry where a **feasible assignment exists** (every school's students can be covered by the drivers allocated to that school, respecting per-driver capacity and one-school-per-driver), when the administrator triggers matching, then every registered student who is not flagged for exclusion is assigned to exactly one driver in the resulting report, and flagged students appear marked as excluded (CR-19).
- AC-2: Given a driver with capacity C, when matching completes, then that driver is assigned at most C students.
- AC-3: Given students tied to different schools, when matching completes, then every student assigned to a given driver belongs to a single school (one school per driver).
- AC-4: Given a small dataset whose optimal morning plan is known (verified by exhaustive search), when matching runs, then the report's total morning distance equals that optimal value. The **exact-optimality guarantee applies at every scale** (D-21); small-instance exhaustive verification is the acceptance meter for the guarantee.
- AC-5: Given the report after matching, when the administrator opens it, then it shows the total driving distance of the morning plan and, for at-scale runs, the recorded optimality evidence (certificate of proven zero gap per D-22).
- AC-6: Given a registry where **no feasible assignment exists** (e.g., global capacity is sufficient but one school's students exceed what the drivers that can serve that school can carry), when the administrator triggers matching, then no partial plan is produced for publication; instead the run reports the failure with the complete data: the list of unassigned students, the capacity shortfall per school, and the assignments that could not be made.
- AC-7: Given the per-school imbalance dataset (School A: 20 students, School B: 10 students; two drivers of capacity 15 each — total capacity 30 ≥ 30 students, yet infeasible under one-school-per-driver), when the administrator triggers matching, then the run fails exactly as described in AC-6 (no invalid plan is produced).
- AC-8: Given a degenerate registry (zero students, zero drivers, or every student flagged for exclusion), when the administrator triggers matching, then the run completes with an empty or all-excluded report and raises no failure.

**Priority:** Must | **Traces to:** CR-05, CR-06, CR-07 | **Source:** Discovery session 2026-08-15

---

### US-05 — Review and publish the matching report
**As an** administrator,
**I want to** review the matching report and explicitly approve it before anything goes live,
**so that** parents and drivers only ever see finalized assignments.

**Acceptance criteria:**
- AC-1: Given a completed matching run, when the administrator opens the report, then every assignment (student, driver, school) and the total distance are visible for review.
- AC-2: Given a report that has not been approved, when a parent or driver views the dashboard, then no assignment information is shown.
- AC-3: Given a reviewed report, when the administrator approves it, then assignments become visible to the corresponding parents and drivers (dashboard and exported file).
- AC-4: Given a matching run that failed to assign every student, when the administrator reviews the failure report, then the unassigned students and the capacity shortfall are clearly flagged, and publication of any partial plan is blocked until the failure is resolved (add drivers + re-run, or flag students — CR-18/CR-19).
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
- *(Interaction with the one-school-per-driver rule (CR-04) on manual reassignment: pending OQ-06.)*

**Priority:** Should | **Traces to:** CR-11, CR-16 | **Source:** Discovery session 2026-08-15

---

### US-07 — Driver views roster for the morning and noon runs
**As a** driver,
**I want to** see my assigned students with pickup order and times for the morning, and my noon return as the reverse,
**so that** I know exactly whom to pick up, in what order, and when.

**Acceptance criteria:**
- AC-1: Given a published plan, when the driver opens the dashboard, then the roster shows the students assigned to them in pickup order, each with a pickup time.
- AC-2: Given a published plan, when the driver exports the roster file, then the file contains the same students, order, and times as the dashboard.
- AC-3: Given a published plan, when the driver views the noon return, then the return order is the reverse of the morning order and is anchored to the school's dismissal time.
- AC-4: Given a driver with no assignments in a run, when the driver opens the dashboard, then the roster is empty and shows no other driver's students.

**Priority:** Must | **Traces to:** CR-08, CR-12 | **Source:** Discovery session 2026-08-15

---

### US-08 — Parent views child's assignment (driver/vehicle identity)
**As a** parent/guardian,
**I want to** see my child's assigned driver and vehicle identity,
**so that** I can recognize who is coming to pick up my child.

*Scope note (D-17): this story intentionally merges assignment viewing (AC-1…4) with parent account provisioning/activation (AC-5…7) for the MVP — the account lifecycle is small and is the precondition for any viewing. A split into a separate account story is deferred; revisit if the account flow grows.*

**Acceptance criteria:**
- AC-1: Given a published assignment for my child, when I open the dashboard, then I see my child's name, school, assigned driver, and vehicle identity (plate number, model, color — OQ-05).
- AC-2: Given a published assignment for my child, when I export the assignment file, then it contains the same driver/vehicle identity information.
- AC-3: Given my child's assignment has not been published, when I open the dashboard, then no assignment information is shown.
- AC-4: Given a parent with two children assigned to different drivers, when I open the dashboard, then each child's assignment is shown separately.
- AC-5: Given a parent whose account was auto-created from school-provided data, when they sign in, then the account is active and they can view their child's assignment.
- AC-6: Given a parent without an account, when they request account registration and the administrator/school accepts the request, then the account becomes active and the parent can view the assignment.
- AC-7: Given a parent whose registration request has not yet been accepted, when they attempt to sign in, then they cannot access any assignment information.

**Priority:** Must | **Traces to:** CR-10, CR-20, D-02 | **Source:** Discovery session 2026-08-15

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

**Priority:** Must | **Traces to:** CR-18, CR-19 | **Source:** OQ-01 resolution, 2026-08-15

---

## 3. MoSCoW Prioritization

| ID | Story | Priority | Rationale (litmus test) |
|---|---|---|---|
| US-01 | Register a school | **Must** | Without schools, nothing can be matched. No workaround. |
| US-02 | Register a student | **Must** | Core data; the service is useless without the registry. |
| US-03 | Register a driver with capacity and vehicle identity | **Must** | Capacity is the hard constraint; identity is the parent's primary need. No registry → no plan. |
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
- **Scale:** Hours from admin trigger to a complete, reviewable report.
- **Meter:** Timed run against a reference dataset of 500 students / 50 drivers / 10 schools, one city (reference environment per A-12).
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
- **Core hours:** 05:30–09:00 and 12:00–14:30 local.
- **Meter:** Uptime monitoring over the school year.
- **Goal:** ≥ 99% during core hours. **Fail:** < 97%. **Wish:** 99.9%.
- **Rationale:** The morning window is when parents/drivers actually depend on the system.

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
- **Build ceiling:** **$6,000** (≈30–40 person-days, ~20% contingency included). **Approved by product owner 2026-08-15 (OQ-02).**
- **Operating ceiling:** **$30/month** hosting + tools (≈$400/year incl. domain). **Approved 2026-08-15.**
- **Re-check trigger (Gate B):** any scope change re-enters this check before Phase 3 spend and again at release (Gate 7).

### NFR-09 — Robustness (error handling)
- **Scale:** Behavior on invalid input (missing fields, capacity 0, duplicate registration attempts).
- **Meter:** Error-path test suite.
- **Goal:** Every invalid submission is rejected with a clear message and causes no partial state. **Fail:** data corruption or silent acceptance.

---

## 5. Traceability Matrix

| Story | Confirmed requirements |
|---|---|
| US-01 | CR-01, CR-08 |
| US-02 | CR-02, CR-16 |
| US-03 | CR-03, CR-04, D-02 |
| US-04 | CR-05, CR-06, CR-07 |
| US-05 | CR-09, CR-10 |
| US-06 | CR-11, CR-16 |
| US-07 | CR-08, CR-12 |
| US-08 | CR-10, CR-20, D-02 |
| US-09 | CR-18, CR-19 |

Coverage check: CR-13 (no notifications), CR-14 (no absence reporting), CR-15 (no driver-absence handling), and CR-17 (scale) are **explicitly out of story scope by decision** — they are recorded in `discovery.md` as decisions/NFR inputs, not as stories (a story would contradict the confirmed decision).

---

## 6. Baseline Status

- **Status:** DRAFT v0.10 — not approved. (v0.9 → v0.10: F4 closed → D-27 + US-05 AC-5; F6 closed → D-28 (parent/admin map-based location entry) + CR-02 + US-02 + OQ-15; OQ-14(d) now fully resolved.)
- **Next step:** human approval → baseline locked and versioned (v1.0) + Gate 1.
- **Blockers to Gate 1:** none — OQ-07 and OQ-09 resolved (remainder (c) of OQ-14: road-data source/cost — close before Phase 3); OQ-08 resolved.
- **Open non-blocking:** OQ-06 (one-school-per-driver under tweaks — must close before US-06 baseline), OQ-10…13 (plan lifecycle, mid-year propagation, driver identity/credentials, identifiers/duplicates), OQ-14(c) (road-network data source & cost — close before Phase 3), OQ-15 (student-registration flow — Phase 2).