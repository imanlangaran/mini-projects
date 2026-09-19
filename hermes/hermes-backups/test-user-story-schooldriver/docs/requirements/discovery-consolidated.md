# Requirements Discovery — School Driver Platform (Reader Edition)

> **Derived from baseline v1.1** (`docs/requirements/discovery.md` — BASELINE LOCKED, originally locked 2026-08-25, amended 2026-09-05).
> Clean current-truth prose: resolved questions are folded in, superseded wording is replaced by what stands today. This edition is **not** the governing artifact — `docs/requirements/discovery.md` and `docs/requirements.md` remain authoritative; any conflict resolves in favor of the originals.

---

## 1. Product Intent

A smart transportation platform that efficiently matches drivers with students based on location, time, capacity, and destination, optimizing pickup routes to minimize total driving distance while assigning every eligible student.

| Role | Interaction |
|---|---|
| Student (passenger) | Rides only; does **not** use the dashboard (the parent does) |
| Parent/Guardian | Views their child's assignment; primary need: **driver/vehicle identity** |
| Driver | Sees rosters (students, order, times) via dashboard and exported file |
| Administrator | Registers schools/students/drivers, triggers matching, reviews/publishes reports, tweaks assignments |

**Confirmed: no other stakeholders** (no school secretary, coordinator, or regulator).

---

## 2. Confirmed Requirements (CR-01…26)

- **CR-01** — The system supports multiple schools. Each school is registered by an administrator and has a location (**address and coordinates, both required**), a sex (**single-gender: male or female**), and **one or more shifts**, each with a start time and end time.
- **CR-02** — Each student is registered with a **national ID (کد ملی) as the unique student key** (10-digit, format-validated, unique across the registry), a home location (**address + coordinates, both required**), tied to exactly one school, with a **sex equal to the school's sex** (validated) and **exactly one shift selected from that school's shifts**. Registration is **initiated by the parent** and becomes a student record when the **administrator/school accepts** it (mirrors the CR-20 parent-request pattern). The home address and map-selected location are provided by the parent/guardian; registry, reassignment, flagging, and export key off the کد ملی (D-52).
- **CR-03** — Each driver's record holds: vehicle capacity (per driver); vehicle identity — **plate number, model, color** (editable after publication; parents always see current values); the **driver's name and phone number** (shown to parents, D-51) and **national ID (کد ملی)** (duplicate-check key, D-52); origin — the **driver's home address, captured at registration**; sex (male/female); **one or more service areas** (**predefined zones**, stored/consumed as polygons); and service availability as **DriverShift entries**: selected system-defined shifts plus served direction(s) (pickup at shift start and/or drop-off at shift end, one or both). An entry **never names a school** — availability is school-agnostic. Per-direction service windows **derive from the selected shifts**; no manually entered window field exists at MVP.
- **CR-04** — **No school is bound to a driver.** Matching allocates individual runs; which school's students a driver serves is an output of each allocation. A driver may serve multiple schools across runs, provided every pair of same-day runs satisfies CR-26.
- **CR-05** — The administrator can trigger a matching run at any time via an explicit admin action.
- **CR-06** — Matching assigns every registered student whenever a **feasible assignment exists** — defined per school, per shift, **and per direction run**: every school's students of a given shift can be covered for each direction by the drivers allocated to that school, respecting per-direction capacity, same-day run compatibility (CR-26), gender rule (CR-21), service-area rule (CR-22), and selection-based eligibility (D-47). Flagged students are excluded from the count. When no feasible assignment exists → CR-18.
- **CR-07** — The optimization objective is **minimize total driving distance — the only objective** (no fairness/balance constraints), applied **per direction run**. Distance = **real road distance without traffic**, computed on a **self-hosted open-source routing engine** (no paid routing/geocoding API).
- **CR-08** — **Shift/direction model:** each school shift has a **to-school run** (covers shift start) and a **from-school run** (covers shift end). Each run's distance is **evaluated separately**; to-school and from-school assignments are **independent** (a student may have a different driver per direction). Assignment **decisions** across all runs are made in **one global optimization**, among whose distance-optimal plans a soft same-driver continuity preference applies (never overriding distance).
- **CR-09** — Matching produces a **reviewable report**; the administrator reviews it before anything becomes final.
- **CR-10** — On approval, assignments become visible to parents and drivers via **both dashboard and exported file**.
- **CR-11** — The administrator may tweak individual assignments without re-running matching; tweaks apply immediately on save. Direction scope is selected per tweak (D-48).
- **CR-12** — Drivers receive, per shift and per direction run, their student list with sequence order and times — to-school: pickup order and pickup times; from-school: one school-departure time plus drop-off order and drop-off times — via both dashboard and exported file. Times are informational.
- **CR-13** — **No notifications** and no pickup confirmation/check-in (explicitly out of scope).
- **CR-14** — Student absence: **no reporting mechanism** in the MVP.
- **CR-15** — Driver absence: **no system handling** (admin may intervene outside the system).
- **CR-16** — Mid-year changes: registry update + manual tweaks; matching is **not re-run**, except the admin-triggered capacity re-validation run. No day-of edits by the administrator.
- **CR-17** — MVP scale: **hundreds of students**, one city, mixed driver capacities.
- **CR-18** — When no feasible assignment exists for a shift/direction, matching produces **no partial plan**; it reports the failure with complete data: unassigned students, shortfall per school/shift/direction (including gender, area, and eligibility causes), and blocked assignments. Remedies must respect eligibility: added drivers must be eligible for the failing group; flagging students resolves demand-side failures only. Resolution = add eligible drivers + re-run, or flag students (CR-19).
- **CR-19** — The administrator can **flag a student for exclusion** from matching runs (all shifts/directions); flagged students appear marked in reports; the flag is reversible. Flag and removal **propagate immediately** to live rosters and parent views; matching is not re-run (CR-16/D-23 unchanged) (D-50).
- **CR-20** — Parent accounts are created either **automatically from school-provided data** or **via a parent request accepted by the administrator/school**. Only active accounts can view assignments.
- **CR-21** — **Gender rules:** a male driver transports only male students; a female driver may transport both. All students in one vehicle are of the same sex (car purity follows from single-sex schools).
- **CR-22** — **Service-area rule:** a driver is eligible for a student group only if both the school's location **and** every student's home lie inside the driver's predefined zone(s). Only spatial coverage matters.
- **CR-23** — **Time rule (scoped):** strict containment governs only **explicitly declared windows** (a post-MVP feature). At MVP, eligibility is selection-based — see D-47/CR-03/D-42.
- **CR-24** — **Direction independence:** a student's to-school and from-school assignments are independent; a driver selecting only one direction of a shift serves only that direction.
- **CR-25** — Shift definitions (and any school's adopted set) **may overlap freely**; no validation at definition time. Constraints bind only driver availability selections (US-03 AC-13/14) and allocated runs (CR-26).
- **CR-26** — **Same-day run compatibility:** for any two runs allocated to one driver on one day, ordered in time: (i) clock windows must not overlap; (ii) runs serving **different schools** require gap ≥ 2 × **MIN_TURNAROUND_MINUTES** (system configuration; **MVP value 30**); (iii) consecutive runs at the **same school** need only non-overlap. Intervals are half-open [start, end); boundary touch = non-overlap. Selecting a shift-direction reserves its full buffered window [S − T, E + T]. Declaration-time checks: US-03 AC-13/14; authoritative enforcement during matching feasibility.

---

## 3. Assumptions — status at lock

All Gate-1 assumptions were **confirmed by the product owner on 2026-08-25**:

| ID | Assumption | Status |
|---|---|---|
| A-01 | Annual matching aligned with the school year; admin triggers before the first school day | ✅ Confirmed |
| **A-02** | Dismissal time = **the end time of the relevant shift**; no separate school-level dismissal field at MVP *(restated at Gate 1 from pre-shift-model wording)* | ✅ Confirmed |
| A-03 | Vehicle capacity = passenger seats | ✅ Confirmed |
| A-04 | Exported file mirrors dashboard content per role; format is a Phase-3+ implementation detail | ✅ Confirmed |
| A-05 | Parents see own children; drivers own roster; administrators everything | ✅ Confirmed |
| A-06 | A parent account may link one or more students | ✅ Confirmed |
| A-07 | Shown pickup/drop-off times are route-derived and informational | ✅ Confirmed |
| A-08 | Mid-year school change handled like any mid-year change (registry + tweak) | ✅ Confirmed |
| A-09 | School days only; no holiday/calendar handling in MVP | ✅ Confirmed |
| A-10 | Parent↔student linkage (keyed on the student's کد ملی — D-52) is part of account provisioning data | ✅ Confirmed |
| A-11 | Driver/admin accounts provisioned by school/administrator; all roles authenticate | ✅ Confirmed |
| A-12 | Performance meters measured against a reference environment pinned at **Phase 6** | Expires Phase 6 |
| A-13 | Capacity tracked **per direction run** (confirmed by D-34) | ✅ Confirmed |
| A-14 | Fixed shifts only at MVP; circular shifts post-MVP | ✅ Confirmed |
| A-15 | Selecting a shift-direction reserves the whole buffered window [S−T, E+T] | ✅ Confirmed |
| A-16 | Half-open intervals; exact boundary touch counts as non-overlap | ✅ Confirmed |

---

## 4. Decisions in force (D-01…53, current truth)

*Superseded clauses are omitted; only what stands today is listed. Full history in `discovery.md`.*

- **D-01** Dashboard designed for the parent/guardian, not the student.
- **D-02** Parent's primary information need: driver/vehicle identity — parent-facing identity set: **driver name, car model, plate number, driver's phone number** (D-51).
- **D-03** MVP success metric: only the primary metric (SM-01).
- **D-04** No notifications, no pickup confirmation, no absence reporting, no driver-absence handling (MVP).
- **D-05** No day-of admin edits; per-day driver reports are future.
- **D-06** Optimization has a **single objective** (min total distance). *(The per-shift/per-direction model and time constraints now live in CR-08/CR-23.)*
- **D-07** Capacity is a **hard constraint**. *(Multi-school allocation now governed by D-36/CR-04.)*
- **D-08** No additional matching rules for MVP; driver preference areas post-MVP.
- **D-09** No formal privacy/compliance regime; ordinary security NFRs apply to children's data.
- **D-10** Admin tweaks do not re-trigger matching.
- **D-11** Scale: hundreds of students, one city, mixed capacities (MVP).
- **D-12** Failure handling: infeasible runs blocked with a complete failure report; resolve via drivers+re-run or flagging.
- **D-13** UI language: Persian (Farsi) with full RTL support; single language at MVP.
- **D-14** Parent accounts: auto-created from school data, or requested + accepted.
- **D-15** Vehicle identity fields: plate number, model, color. *(Extended by D-51: identity shown to parents additionally includes the driver's name and phone number.)*
- **D-16** Run performance deliberately relaxed: rare, off critical path. *(Thresholds live in NFR-01.)*
- **D-17** US-08 intentionally merges assignment viewing with account provisioning for MVP.
- **D-18** Delivery channels standardized: dashboard **and** exported file per role.
- **D-19** "Driving distance" = real road distance, without traffic.
- **D-20** Driver capacity edits: cannot drop below the current assignment count on an approved/published plan; rejected with a clear message; re-validation required first.
- **D-21** **Exact optimum at every scale**, asserted over the joint assignment space (one global solve; objective decomposes per direction run). Hours-long runs acceptable; solver cost re-checked at Gate B.
- **D-22** Report records a solver optimality certificate (proven zero gap); >24 h runs abort with documented failure report; publication blocked.
- **D-23** Admin-triggered capacity re-validation run is an explicit exception to "matching is not re-run."
- **D-24** Driver origin = home address, captured at registration — applies to the **to-school** run; the from-school run starts at the school (D-39).
- **D-25** Vehicle identity editable after publication; parents see current values.
- **D-26** School/student locations = address + coordinates, both required.
- **D-27** Registry/capacity change between run completion and approval blocks approval until re-run/tweak/revert.
- **D-28** Location entry: typed address + map selection (admin for schools, parents for homes; the **parent initiates the student registration** — D-53); no paid geocoding assumed.
- **D-29** MOKEAB rules adopted into the MVP: single-sex schools, gender driver rule, car purity, fixed shifts, service areas, service hours, direction independence; full matching + exact-optimality routing.
- **D-30** Schools single-sex; mixed-sex schools out of MVP; student sex validated equal to school's sex; car purity follows.
- **D-31** Service areas consumed as polygons; MVP representation narrowed to predefined zones (see D-43).
- **D-32** Time/direction rules: containment governs explicit windows only (post-MVP); direction independence (CR-24).
- **D-33** Shift model: schools adopt one or more shifts; students select exactly one; separate to-/from-school runs; fixed shifts only at MVP.
- **D-34** Capacity applies **independently to each direction run**.
- **D-35** Availability is **school-agnostic**: drivers select defined shifts + directions; entries never name a school.
- **D-36** Drivers **may serve multiple schools** across runs; school identity is per-run output, never a driver attribute.
- **D-37** Cross-school consecutive runs need gap ≥ 2 × MIN_TURNAROUND_MINUTES (**MVP value 30**, system config); same-school needs only non-overlap.
- **D-38** Shift definitions may overlap freely; conflicts handled only at declaration (US-03) and allocation (CR-26).
- **D-39** From-school run starts at the school at shift end; distance covers school → drop-offs; roster = departure time + drop-off order/times.
- **D-40** Availability is an eligibility envelope: matching may allocate any subset of selections; unused selections reported as *unallocated availability*.
- **D-41** No daily driver limits in MVP beyond CR-26 validity.
- **D-42** Service windows derive from the selected shift; explicit sub-windows post-MVP.
- **D-43** Service-area representation: predefined zones (multi-select); center+radius post-MVP.
- **D-44** Road-network data: self-hosted open-source routing engine; fits the $30/month operating ceiling.
- **D-45** One global optimization; deterministic solver; distance-optimal ties break by maximum same-driver continuity, then stable lexicographic order; continuity never trades away distance.
- **D-46** Build ceiling **$20,000** covering the amendment envelope (58–96 pd ≈ $11,600–19,200, ≈4% headroom); optional solver design spike (~$400–600) as cost-compression lever. *(Originally $18,000; raised after review v6 corrected the high-end conversion error — 96 pd × $200/day = $19,200 exceeded the old ceiling.)*
- **D-47** MVP eligibility for a direction run ⇔ the driver **selected that shift-direction** (plus capacity, gender, area, CR-26). Strict containment governs explicit windows only.
- **D-48** Tweak direction-scope: **admin-selected per tweak** — to-school only / from-school only / **both (default)** — each direction validated against target-driver eligibility and per-direction capacity, whole-day CR-26 preserved; out-of-scope assignments untouched; applied scope recorded.
- **D-49** A new matching run **supersedes** the previous published plan — the old plan stops being published; prior US-06 tweaks are **not automatically carried** into the re-run's plan — the admin may re-apply tweaks manually for any assignment still valid under the new plan. Trigger UX shows a supersede warning on re-trigger (2026-09-05).
- **D-50** Flagging **or removing** a student mid-year **propagates immediately** to live rosters and parent views; matching is **not re-run** (CR-16/D-23 unchanged) (2026-09-05).
- **D-51** Identity shown to parents for a child's assigned driver: **driver's name, car model, plate number, driver's phone number** — extends the D-15/CR-03 identity set (2026-09-05). *(Credential delivery mechanics: UX-OQ-23.)*
- **D-52** Student unique key = **national ID (کد ملی)**: 10-digit, format-validated, unique. Duplicates: student = same کد ملی; school = same name + coordinates (D-26); driver = same plate **or** same کد ملی — each rejected **naming the existing record** (NFR-09). School student number is display-only; assignment/flag/export key off کد ملی (2026-09-05).
- **D-53** **Student registration is initiated by the parent**; the request becomes a student record when the administrator/school accepts it (mirrors the CR-20 parent-request pattern) (2026-09-05).

---

## 5. Open Questions

### Remaining open (non-blocking, triggers named)

| ID | Topic | Trigger |
|---|---|---|

| OQ-17 | Circular-shift rotation semantics | Post-MVP |

*(No open question may be marked resolved without the product owner's explicit answer.)*

### Resolved — index

OQ-01 → D-12/CR-18/CR-19 · OQ-02 → budget (superseded chain → D-46: **$20,000**) · OQ-03 → D-13 · OQ-04 → D-14/CR-20 · OQ-05 → D-15 · **OQ-06 → D-48 (2026-08-25)** · OQ-07 → D-19/D-24 · OQ-08 → D-21 · OQ-09 → D-20/D-25 · **OQ-10 → D-49 · OQ-11 → D-50 · OQ-12 → D-51 · OQ-13 → D-52 · OQ-15 → D-53 (2026-09-05)** · OQ-14(a–d) → D-24/D-25/D-44/D-26+28 · OQ-16 → D-43 · OQ-18 → D-34 · OQ-19 → D-42 · OQ-20 → D-41 · OQ-21 → estimate recorded, ceiling re-baselined, review v5 executed + remediated, Rule-7 settled via confirmation pass (reviews v6/v7)

---

## 6. Success Metrics

| ID | Metric | Threshold |
|---|---|---|
| SM-01 | **Assignment coverage (primary)** | **100% of registered non-flagged students assigned whenever a feasible assignment exists**; CR-18 failure runs and D-22 aborts are judged on report completeness. Flagged students excluded by design (PO-confirmed 2026-08-23). |
| SM-02 | Deferred by D-03 | — |
