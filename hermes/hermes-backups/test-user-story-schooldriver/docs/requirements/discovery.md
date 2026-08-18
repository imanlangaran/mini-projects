# Requirements Discovery — School Driver Platform

> **Project:** Smart transportation platform for school students (daily home ↔ school shuttles)
> **Phase:** 1 — Requirements (discovery session)
> **Session date:** 2026-08-15
> **Status:** Discovery complete; pending human review of stories, MoSCoW, NFRs (pre-approval packet)
> **Source of truth:** This artifact. Conversation contents not recorded here do not exist as requirements.

---

## 1. Product Intent (Phase 0 input, approved)

A smart transportation platform that efficiently matches drivers with users based on location, time, capacity, and destination. It optimizes pickup routes to minimize total driving distance while ensuring all users are assigned.

**Target users (confirmed during session):**

| Role | Who they are | System interaction |
|---|---|---|
| Student (passenger) | Child transported daily | Rides only; does **not** use the dashboard (parent does) |
| Parent/Guardian | Checks the dashboard | Views their child's assignment; primary need: **driver/vehicle identity** |
| Driver | Provides transport | Sees roster (students, order, times) via dashboard and exported file |
| Administrator | School staff | Registers schools/students/drivers, triggers matching, reviews/publishes report, tweaks assignments |

**Confirmed: no other stakeholders** (no school secretary, coordinator, or regulator in the loop).

---

## 2. Confirmed Requirements

| ID | Requirement |
|---|---|
| CR-01 | The system shall support multiple schools; each school is registered by an administrator and has a **location — address and coordinates, both required** (D-26), a **sex (single-gender: male or female, D-29/D-30)**, and **one or more shifts**, each with a start time and end time (D-33). |
| CR-02 | Each student shall be registered with a **home location — address and coordinates, both required** (D-26) — tied to exactly one school, with a **sex equal to the school's sex (validated, D-30)**, and **exactly one shift selected from the school's shifts** (D-33). The home address and map-selected location are provided by the **parent/guardian** (D-28). |
| CR-03 | Each driver's vehicle capacity shall be recorded in the system; capacities may differ between drivers. The driver's record shall also include vehicle identity details — **plate number, model, and color** (OQ-05, resolved; editable after publication, D-25) — sufficient for a parent to recognize the vehicle, the driver's **origin (route start): home address, captured at registration** (D-24), the driver's **sex (male or female, D-29)**, **one or more service areas** (polygon and/or center+radius, D-31), and **service availability per shift and direction** (DriverShift: school shift + to-school/from-school flags + service time window, D-32/D-33). |
| CR-04 | A driver shall pick up students from exactly one school; which school is **not predefined** — it is determined by the matching phase. |
| CR-05 | The administrator shall be able to trigger a matching run at any time via an explicit admin action. |
| CR-06 | Matching shall assign every registered student to a driver whenever a **feasible assignment exists** — defined per school, per shift, **and per direction run**: every school's students of a given shift can be covered for each direction by the drivers allocated to that school, respecting each driver's capacity (per direction, A-13), the one-school-per-driver rule (CR-04), the gender rule (CR-21), the service-area rule (CR-22), and the time rule (CR-23) for that direction's eligible driver pool. Flagged students (CR-19) are excluded from the count. Behavior when no feasible assignment exists: see CR-18 (independent review IR-01; retargeted per direction by review V4-02). |
| CR-07 | The optimization objective is **minimize total driving distance** — the *only* objective. No fairness or balance constraints apply. The objective applies **per direction run** (each to-school run and each from-school run, CR-08). Distance = **real road distance without traffic** (D-19); road-network data source and cost: OQ-14(c). |
| CR-08 | **Shift/direction model (D-33, replaces the single-morning-run model):** each school shift has a **to-school run** (covers the shift start) and a **from-school run** (covers the shift end). Each direction run is optimized independently (minimize total distance, CR-07) and **to-school and from-school assignments are independent — a student may have a different driver per direction (D-32)**. The noon run is no longer defined as the reversed morning plan; it is the from-school run of the relevant shift. |
| CR-09 | Matching shall produce a **reviewable report**; the administrator reviews it before anything becomes final. |
| CR-10 | On approval, assignments become visible to parents and drivers via **both channels: dashboard and exported file** (standardized from "and/or" — independent review IR-15; consistent with D-18). |
| CR-11 | The administrator may tweak individual assignments without re-running matching; tweaks apply immediately on save. |
| CR-12 | Drivers shall receive, **per shift and per direction run**, the list of students, the pickup **order**, and **time information** per student, via **both channels: dashboard and exported file** (consistent with D-18). |
| CR-13 | The system shall provide **no notifications** and require **no pickup confirmation/check-in** (explicitly out of scope). |
| CR-14 | Student absence: **no reporting mechanism** in the MVP (possible future feature). |
| CR-15 | Driver absence: **no system handling** — no backup pool, no automatic action (admin may intervene manually outside the system). |
| CR-16 | Mid-year changes (new student, student moves, student leaves): the administrator updates the registry and may tweak assignments manually; **matching is not re-run**, **except an admin-triggered capacity re-validation run (D-23)**; no day-of edits by the administrator. |
| CR-17 | Scale target for MVP: **hundreds of students**, coverage of **one city**, mixed driver capacities. |
| CR-18 | When no feasible assignment exists for a shift or direction (OQ-01, resolved), matching shall **not** produce a partial plan for publication; it shall instead report the failure with complete data — the list of unassigned students, the **shortfall per school/shift/direction** (including gender, area, and time causes), and the blocked assignments. **Remedies must respect eligibility (V4-11):** added drivers must be eligible for the failing group (gender/area/time); flagging students resolves demand-side failures (capacity/coverage) and does not resolve supply-side eligibility failures unless all affected students are flagged. The administrator resolves the failure by adding eligible drivers (then re-running) or by flagging students for exclusion (CR-19). |
| CR-19 | The administrator shall be able to **flag (disable) a student for assignment**; flagged students are excluded from matching runs (all shifts/directions) and are marked as flagged in reports. The flag is reversible. |
| CR-20 | Parent/guardian accounts shall be created in one of two ways (OQ-04, resolved): **automatically from school-provided data**, or **via a parent registration request that becomes active when the administrator/school accepts it**. Only active accounts can view assignments. |
| CR-21 | **Gender rules (D-29, MOKEAB R-1/R-2):** a **male driver may transport only male students**; a **female driver may transport both male and female students**. A student's sex always equals their school's sex; therefore **all students in one service (car) are of the same sex** (car purity — MOKEAB R-3). |
| CR-22 | **Service-area rule (D-31, MOKEAB R-3-location):** a driver is eligible for a student group only if **both** the school's location **and every student's home location** lie inside the driver's service area (one or more polygons and/or center+radius zones, D-31). Only spatial coverage matters — not route or distance. |
| CR-23 | **Time rule (D-32, MOKEAB R-2-time):** a driver is eligible for a direction run only if the driver's service time window **strictly contains** the shift's relevant time for that direction — shift start (to-school) / shift end (from-school). No partial overlaps, no grace periods (MOKEAB strictness). |
| CR-24 | **Direction independence (D-32, MOKEAB R-6):** a student's to-school and from-school assignments are independent; a driver selecting only one direction of a shift serves only that direction. |

---

## 3. Assumptions

| ID | Assumption | Owner | Expiry |
|---|---|---|---|
| A-01 | The annual matching cycle is aligned with the school year; the admin triggers it before the year's first school day. Exact timing not specified. | Product owner | Gate 1 (confirm) |
| A-02 | A school's dismissal time is part of the school record the administrator registers. | Product owner | Gate 1 |
| A-03 | Vehicle capacity = number of passenger seats. | Product owner | Gate 1 |
| A-04 | The exported file contains the same assignment information as the dashboard (per role). File format is an implementation detail (Phase 3+). | Product owner | Gate 1 |
| A-05 | Access control: parents see only their own child's assignment; drivers see only their own roster; administrators see everything. | Product owner | Gate 1 |
| A-06 | A parent/guardian account may be associated with one or more students (e.g., siblings), all visible to that parent. | Product owner | Gate 1 |
| A-07 | Pickup times shown to the driver are derived from the optimized route (distance-driven); they are informational, not contractual. | Product owner | Gate 1 |
| A-08 | A student changing schools mid-year is handled like any other mid-year change (registry update + admin tweak, CR-16). | Product owner | Gate 1 |
| A-09 | The system is used only on school days; no holiday/calendar handling in the MVP. | Product owner | Gate 1 |
| A-10 | Parent↔student linkage (which student(s) belong to a parent's account) is part of the school-provided data used for auto-created accounts, and part of the registration request for parent-requested accounts. (Review pass 5, F5-05.) | Product owner | Gate 1 |
| A-11 | Driver and administrator accounts are provisioned by the school/administrator (all roles authenticate — NFR-04). | Product owner | Gate 1 |
| A-12 | NFR performance meters (NFR-01/02/03) are measured against a **reference environment pinned at Phase 6 (QA)** (hardware/browser/network) — thresholds apply to that environment, not arbitrary machines (independent review IR-06). | Product owner | Phase 6 |
| A-13 | Capacity is tracked **per direction run** of a shift (to-school and from-school counted separately — MOKEAB O-1 recommendation; confirmation via OQ-18). | Product owner | Gate 1 (confirm) |
| A-14 | MVP implements **fixed shifts only**; circular shifts are deferred post-MVP (D-33, OQ-17). | Product owner | Gate 1 (confirm) |

---

## 4. Decisions (made during the session)

| ID | Decision |
|---|---|
| D-01 | Dashboard is designed for the **parent/guardian**, not the student. |
| D-02 | Parent's primary information need: **driver/vehicle identity**. |
| D-03 | Success metric for MVP: **only the primary metric** (SM-01) — supporting metrics (setup speed, efficiency guarantee) deferred. |
| D-04 | No notifications; no pickup confirmation; no absence reporting; no driver-absence handling (MVP). |
| D-05 | No day-of admin edits; per-day driver reports are a future feature. |
| D-06 | Optimization: single objective (min total distance), morning run only, no time constraints. **Partially superseded by D-29/D-32/D-33 (2026-08-15):** the single-objective part stands; "morning run only" is replaced by the per-shift/per-direction model (CR-08); "no time constraints" is replaced by the service-hours containment rule (CR-23). |
| D-07 | Capacity is a **hard constraint**; one school per driver (school chosen by matching). |
| D-08 | No additional matching rules for MVP; **driver preference area** is explicitly post-MVP. |
| D-09 | No formal privacy/compliance regime applies (no regulatory obligations); ordinary security NFRs still apply to children's data. |
| D-10 | Admin tweaks to assignments do not re-trigger matching. |
| D-11 | Scale: hundreds of students, one city, mixed capacities (MVP). |
| D-12 | Failure handling (OQ-01, resolved): infeasible runs are blocked from publication with a complete failure report; admin resolves by adding drivers + re-run, or by flagging students for exclusion. |
| D-13 | UI language: **Persian (Farsi)**, with **RTL layout support** (OQ-03, resolved). Single language at MVP. |
| D-14 | Parent account creation (OQ-04, resolved): auto-created from school-provided data, or parent-requested with admin/school acceptance. |
| D-15 | Vehicle identity fields (OQ-05, resolved): plate number, model, color (+ capacity already captured). |
| D-16 | Matching run performance threshold deliberately relaxed (product owner, 2026-08-15): runs occur only once or twice a year and are not on the critical path. **Superseded by D-21 + NFR-01 v0.6 for thresholds** (Goal ≤ 3 h, Stretch ≤ 1 h, Fail > 24 h); this decision's rationale (rare runs, off critical path) remains the justification. |
| D-17 | US-08 intentionally merges assignment viewing with parent account provisioning/activation for the MVP (independent review IR-16) — account lifecycle is small and is the precondition for viewing; split deferred pending growth. |
| D-18 | Channels standardized: assignments are delivered via **both** dashboard and exported file per role (independent review IR-15; resolves CR-10 "and/or" ambiguity). |
| D-19 | **Distance semantics (OQ-07, resolved 2026-08-15):** "driving distance" = **real road distance, without traffic** (fixed road network; no live-traffic weighting). |
| D-20 | **Driver capacity edits (OQ-09, resolved 2026-08-15):** a driver's capacity may not be reduced below their current assignment count while an approved/published plan exists — the edit is rejected with a clear message; re-validation (re-run matching or reassignment including US-06 flow) is required first. |
| D-21 | **Optimality guarantee (OQ-08, resolved 2026-08-15):** matching must find the **exact optimum** — minimum total driving distance **per direction run** (CR-07/CR-08) — at **every scale**, not only small instances. Because runs occur once or twice a year, run time may extend to hours (NFR-01: Goal ≤ 3 h, Fail > 24 h); an overnight run is acceptable. **Gate B note (V2-11):** the exact-solver choice (free vs licensed) and its compute/licensing cost are re-checked at Gate B before Phase 3 spend (NFR-08 trigger). (Wording retargeted from "morning" to per-direction by review V4-06.) |
| D-22 | **At-scale optimality evidence + fail-breach (V2-06, confirmed 2026-08-15):** the report records a solver **optimality certificate (proven zero gap)** for the produced plan; small-instance exhaustive search (US-04 AC-4) validates solver correctness. A run exceeding 24 h is **aborted** with a documented failure report, publication is **blocked**, and the administrator may re-run or adjust inputs (NFR-01). |
| D-23 | **CR-16 exception (V2-07, product owner 2026-08-15):** an **admin-triggered capacity re-validation run is an explicit exception** to CR-16's "matching is not re-run for mid-year changes" — it is rare, admin-triggered, and required for the D-20 re-validation path. |
| D-24 | **Driver origin (OQ-14(a), resolved 2026-08-15):** the driver's origin (route start) is the **driver's home address, captured at registration**. |
| D-25 | **Vehicle identity edits (OQ-14(b), resolved 2026-08-15):** vehicle identity may be **edited after publication**; parents see the **current** identity. |
| D-26 | **Location fields (OQ-14(d), resolved 2026-08-15 — closes IR-07/IR-08):** school "location" and student "home location/address" are **address + coordinates, both required** at registration. |
| D-27 | **Approval-window rule (F4, v3 review — product owner 2026-08-15):** if a registry or capacity change (student added/moved/removed, driver capacity or school/driver record change) is made **after a matching run completes but before the report is approved**, approval is **blocked** with a message directing the administrator to re-run matching (D-23), tweak assignments (CR-16), or revert the change. The report can only be approved if it matches the registry at approval time. |
| D-28 | **Location data entry (F6, v3 review — product owner 2026-08-15):** school location — the **administrator types the address and selects the location on a simple map in the UI** (coordinates come from the map selection). Student home location — the **parent types the address and selects the location on the map**. No paid geocoding service is assumed in the MVP; any map/tile service cost is part of the OQ-14(c) budget question ($30/month ceiling, Gate B re-check). |
| D-29 | **MOKEAB scope adoption (product owner 2026-08-15):** the following MOKEAB-domain rules are **in the MVP**: single-sex schools, gender driver rule (male→boys only), car purity, school shifts (fixed), driver service areas, driver service hours, and to/from direction independence. Governing model: **full matching + exact-optimality routing** (Branch A) — not the eligibility-filter-only phase. |
| D-30 | **School/student sex (D-29 follow-up):** schools are single-sex (male or female); **mixed-sex schools are out of MVP scope** (V4-14 note, review v4). A student's sex is **always equal to the school's sex and is validated**, not freely chosen. Car purity is implied by single-sex schools + one-school-per-driver (CR-04) and is stated as an explicit rule (CR-21). |
| D-31 | **Service areas in MVP:** a driver's service area may be **one or more predefined zones and/or a center+radius zone**; matching consumes the service area as a polygon regardless of how the driver entered it (representation mode: **OQ-16**). |
| D-32 | **Time + direction rules in MVP:** driver service hours must strictly contain the shift time for the served direction (CR-23 — supersedes D-06's "no time constraints" for shift matching); to/from assignments are independent (CR-24). |
| D-33 | **Shift model in MVP:** each school has one or more shifts (each with start/end); each student selects exactly one shift of their school; matching produces separate to-school and from-school runs per shift. **Fixed shifts only in MVP** — circular-shift rotation semantics deferred (OQ-17). |

---

## 5. Open Questions

| ID | Open question | Owner | Status |
|---|---|---|---|
| OQ-01 | What happens when **not all students can be assigned** (e.g., total capacity < students, or an unreachable home location)? | Product owner | ✅ **Resolved 2026-08-15** → D-12, CR-18, CR-19 |
| OQ-02 | **Budget**: no cost ceiling or effort estimate has been decided. Gate 1 requires "Budget approved". What ceiling (build + monthly hosting) should be recorded? | Product owner | ✅ **Approved 2026-08-15** → **$6,000 build** (≈30–40 person-days incl. contingency) + **$30/month** hosting/tools (NFR-08) |
| OQ-03 | **Target language/locale** for the interface. | Product owner | ✅ **Resolved 2026-08-15** → D-13 (Farsi, RTL) |
| OQ-04 | How are parent accounts created? | Product owner | ✅ **Resolved 2026-08-15** → D-14, CR-20 |
| OQ-05 | What exactly constitutes "vehicle identity" for parents? | Product owner | ✅ **Resolved 2026-08-15** → D-15 (plate, model, color) |
| OQ-06 | When the admin manually reassigns a student (US-06), may the target driver end up serving students of a **different school** than before (i.e., does the tweak also change the driver's school), or is the one-school-per-driver rule (CR-04) fixed by the annual matching run? (Review pass 5, F5-04.) | Product owner | 🔶 **Open — non-blocking** (US-06 is out of the MVP set; needed before US-06 is built or baselined as Should) |
| OQ-07 | **Distance semantics (IR-02):** is "driving distance" straight-line or road-network? May the solution use an external geocoding/routing service, and is its cost compatible with the NFR-08 $30/month ceiling? Where does each route start (driver origin), and are driver origin and school location part of registration data? | Product owner | ✅ **Resolved 2026-08-15** → D-19 (road distance, no traffic) + D-24 (driver origin); geodata source/cost remainder → OQ-14(c) |
| OQ-08 | **Optimality guarantee (IR-03, blocker):** at production scale (500 students / 50 drivers), is exact optimality required, or is a documented heuristic with a stated quality bound acceptable (exact optimum only on small instances, per US-04 AC-4)? | Product owner | ✅ **Resolved 2026-08-15** → **D-21: exact optimum at all scales**; run time may take hours (runs once/twice per year); NFR-01 updated (Goal ≤ 3 h, Fail > 24 h) |
| OQ-09 | **Driver record edits (IR-04):** may a driver's capacity be reduced below their current assignment count on an approved/published plan? What should the system do (reject / block / invalidate the plan)? May vehicle identity be edited after publication? | Product owner | ✅ **Resolved 2026-08-15** → D-20 (reject capacity reduction below assigned count) + D-25 (identity edits allowed); remainder → OQ-14(c) |
| OQ-10 | **Plan lifecycle across runs (IR-11) + post-publication shift edits (V4-10):** while a newer report awaits approval and an older plan is published, what do parents/drivers see? If the admin triggers an occasional re-run, do US-06 tweaks survive it? And: what happens when a **school shift time changes after publication** — do published rosters go stale (documented) or is a D-23-style re-validation run required/permitted when CR-23 containment breaks? | Product owner | 🔶 Open — non-blocking |
| OQ-11 | **Mid-year flag/removal after publication (IR-12):** when a student is flagged or removed mid-year, does the change propagate to live rosters/parent views immediately, at the next run, or via an explicit admin tweak? | Product owner | 🔶 Open — non-blocking |
| OQ-12 | **Driver person identity + parent credentials (IR-14):** what identifies "the driver" to the parent (name only? contact details?) beyond the vehicle identity? How do parents with auto-created accounts receive sign-in credentials (SMS/email/printed handout)? | Product owner | 🔶 Open — non-blocking |
| OQ-13 | **Identifiers & duplicates (IR-09/IR-18):** what stable identifier distinguishes students (for registry, reassignment, flagging, parent↔student linkage)? What makes a school/student/driver a "duplicate registration" (name+address? same plate? school-provided ID)? | Product owner | 🔶 Open — non-blocking |
| OQ-14 | **Remainders of OQ-07/OQ-09 + location definitions:** (a) driver origin at registration — ✅ **Resolved 2026-08-15** → D-24 (driver's home address); (b) vehicle identity editable after publication — ✅ **Resolved 2026-08-15** → D-25 (yes, parents see current); (c) is a free road-network data source (no traffic) acceptable within the $30/month ceiling? — 🔶 **Open — close before Phase 3**; (d) location fields — ✅ **Resolved 2026-08-15** → D-26 (address + coordinates, both required) + D-28 (entry method: admin/parent type address + map selection; closes IR-07/IR-08 and F6) |
| OQ-15 | **Student registration flow (D-28 follow-up, non-blocking):** who creates the student record — the administrator registers the student and the parent supplies the home address/location (e.g., during account activation), or the parent initiates registration? Must the home location exist before the student can appear in a matching run? (Phase 2 flow; affects US-02 wording.) | Product owner | 🔶 Open — non-blocking |
| OQ-16 | **Service-area representation mode (D-31 follow-up, MOKEAB O-2):** do drivers select from **predefined areas** (multi-select), define a **center+radius**, or both? Matching consumes polygons either way. Close before Phase 3. | Product owner | 🔶 Open — close before Phase 3 |
| OQ-17 | **Circular shifts (D-33 follow-up, MOKEAB O-4):** rotation semantics for circular SchoolShifts (firstWeekShiftId vs weekIndex) — deferred; MVP implements **fixed shifts only**. Revisit post-MVP. | Product owner | 🔶 Open — post-MVP |
| OQ-18 | **Capacity semantics with directions (MOKEAB O-1 follow-up):** is capacity per shift (shared across both directions) or per direction run? (Recommended: per direction run — to/from are at different times; confirm.) | Product owner | 🔶 Open — non-blocking |

---

## 6. Success Metrics

| ID | Metric | Threshold | Meter |
|---|---|---|---|
| SM-01 | **Assignment coverage (primary)** | **100% of registered non-flagged students** assigned to a driver **whenever a feasible assignment exists**; runs that terminate in a documented CR-18 failure report **or a D-22 abort report** are evaluated on **report completeness**, not coverage | Inspect the generated report; any unassigned non-flagged student in a feasible run = fail |

> **SM-01 wording note:** reconciled with CR-19/US-09 and CR-18 by the independent review (IR-05) — the previous wording ("100% of registered students… any unassigned student = fail") contradicted the Must-priority flag-exclusion feature and counted designed failure runs as metric failures. **Confirmation requested from the product owner at approval (Q4 in the independent review).**
| SM-02 | (Deferred by D-03 — recorded for future reference) | — | — |
