# Gate-1 Approval Packet — School Driver Platform

> **Project:** Smart transportation platform for school students (daily home ↔ school shuttles)
> **Purpose:** Human approval of the Phase-1 requirement baselines (Gate 1). This packet is the single briefing needed to make that decision; every claim links to the source artifacts, which remain the source of truth.
> **Packet date:** 2026-08-25 · **Packet author:** assistant session (continuation per `HANDOFF.md`)
> **Artifacts:** `docs/requirements.md` — **DRAFT v0.17** · `docs/requirements/discovery.md` — **DRAFT v0.17**
> **UPDATE 2026-08-25 — rulings recorded:** assumptions confirmed (§4.2, incl. A-02 restatement); Rule-7 option (b) exercised (§3); confirmation pass **review v6** executed (`story-review-independent-v6.md`) — verdict CONDITIONAL: **V6-01 (budget arithmetic, Major)** and **V6-02 (OQ-06 trigger conflict, Major)** await product-owner disposition before the v1.0 lock. **Progress:** V6-01 dispositioned 2026-08-25 — option (α): ceiling **$18,000 → $20,000**; corrections applied in v0.18 (NFR-08, D-46, packet §6). V6-02: recommendation delivered (admin-selected-per-tweak, both-directions default + eligibility validation); **awaiting explicit PO confirmation** before OQ-06 is recorded resolved.
> **Rule 7 reminder:** this packet was assembled by the same class of agent that authored the amendments and review v5. The approval decision below belongs exclusively to the human product owner.

---

## 1. Status summary

| Item | State |
|---|---|
| Artifact versions | Both at **DRAFT v0.16** (review-v5 remediation applied 2026-08-23) |
| Review history | Internal review + independent v1…v4 (historical, read-only) + **independent v5: CONDITIONAL PASS**, all findings applied |
| Unresolved findings | **Zero** — V5-01 Major resolved via **D-47**; V5-02…05 mechanical fixes landed in v0.16; V5-06/07 notes carried into this packet (§5–§6) |
| Prior dispositions | All 54 (IR-01…18, V2-01…11, F1…F7, V4-01…14) re-verified genuinely closed by review v5 §3.2 |
| Budget gate | Executed — build ceiling re-baselined $6,000 → $18,000 (D-46, 2026-08-23), then **corrected $18,000 → $20,000 (V6-01, 2026-08-25)**; envelope high end is **$19,200** (96 pd × $200/day); operating $30/month unchanged |
| Open questions | OQ-21 closed. Remaining opens are all **non-blocking with named triggers** (§7) |
| Blockers to Gate 1 | **None** (requirements.md §6, confirmed against discovery statuses) |

**What Gate 1 approves:** the user stories US-01…09 with their acceptance criteria, the MoSCoW prioritization and proposed MVP set, NFR-01…09 (including the re-baselined budget), and the discovery layer CR-01…26 / A-01…16 / D-01…47 / OQ ledger / SM-01…02 — locked together as **v1.0 BASELINE LOCKED**.

---

## 2. Decision digest — D-34 … D-47 (the post-review-v4 amendment layer)

All dated 2026-08-23 except where noted. Full text governs; this is orientation.

| ID | Essence | Key ripples |
|---|---|---|
| **D-34** | Capacity applies **independently per direction run** (to-school / from-school counted separately). Confirms A-13. | Closes V4-07/OQ-18; US-04 AC-2 pointer retargeted (V5-04). |
| **D-35** | Driver availability is **school-agnostic**: driver selects system-defined shifts + served direction(s); the entry never names a school. Resolves the CR-03 ↔ CR-04 contradiction. | Closes V4-01; CR-03/CR-04 rewritten; US-03 AC-13 pins "never names a school". |
| **D-36** | **One-school-per-driver removed**: a driver may serve multiple schools across runs, subject to CR-26 compatibility. Supersedes the clause in D-07 and original CR-04. | CR-03/CR-04 rewritten, CR-06 retargeted to CR-26, US-04 AC-1/AC-3/AC-7, US-06/OQ-06 narrowed, §1 scope updated. |
| **D-37** | Same-day turnaround: cross-school consecutive runs need gap ≥ **2 × MIN_TURNAROUND_MINUTES** (system config, **MVP value 30**); same-school back-to-back needs only non-overlap. Codified in **CR-26**. | Basis of US-03 AC-14 declaration checks and matching feasibility. |
| **D-38** | Shift definitions may **overlap freely**; no validation at definition time. Constraints bind only driver declarations (US-03 AC-13/14) and allocations (CR-26). Codified in **CR-25**. | Enables mixed-shift catalogs across schools. |
| **D-39** | From-school run **starts at the school at shift end**; its distance covers school → drop-offs only. Roster semantics: pickup order/times (to-school), departure time + drop-off order/times (from-school). Closes V4-03. | Direction-scopes D-24; CR-12 and US-07 AC-1 aligned. |
| **D-40** | Availability is an **eligibility envelope**: matching may allocate any subset of selections; unused selections appear in the report as *unallocated availability*. Selection ≠ obligation. | US-04 AC-12. |
| **D-41** | **No daily driver limits** in MVP — any CR-26-valid combination is acceptable regardless of occupied span. | Resolves OQ-20; caps/span rules post-MVP. |
| **D-42** | Service window **derives from the selected shift** at MVP; explicit per-direction sub-windows are post-MVP. | Resolves OQ-19; trigger of review-v5's Major (V5-01). |
| **D-43** | Service areas = **predefined zones (multi-select)**, stored/consumed as polygons; center+radius entry post-MVP. Narrows D-31. | Resolves OQ-16; CR-03/CR-22 wording aligned. |
| **D-44** | Road-network data via **self-hosted open-source routing engine** (containerized); no paid routing/geocoding API — stays inside the $30/month operating ceiling. | Resolves OQ-14(c); engine choice is a Phase-3 design decision. |
| **D-45** | **One global optimization** across all schools/shifts/directions; deterministic solver; among distance-optimal plans ties break by (1) maximum same-driver continuity, (2) stable lexicographic order. Continuity **never trades away distance**. | CR-07/CR-08/D-21 coherence (V5-05 wording fix); US-04 AC-4 verification basis. |
| **D-46** | Build ceiling re-baselined **$6,000 → $18,000** (≈90 pd @ $200/day) covering the cumulative amendment envelope: base 30–40 pd + MOKEAB 8–16 pd + driver-allocation 20–40 pd ⇒ ≈58–96 pd (~$11,600–17,200), ~5% headroom. Optional cost lever: **2–3-day solver design spike** (≈$400–600). Operating ceiling unchanged ($30/month). **Amended 2026-08-25 (V6-01):** ceiling now **$20,000** (≈100 pd); envelope high end corrected to **$19,200**; headroom ≈4%. | Gate-B re-check executed; closes the ceiling half of OQ-21; NFR-08 rewritten; arithmetic corrected by review v6 |
| **D-47** | **MVP eligibility semantics**: eligible for a direction run ⇔ the driver **selected that shift-direction**, plus capacity (D-34/A-13), gender (CR-21), area (CR-22), and CR-26 compatibility. CR-23's strict containment governs **explicitly declared windows only** (post-MVP feature). Closes V5-01 Major. | CR-23 scope-restriction annotation; US-03 AC-12 retargeted to derived-window display; US-04 AC-11 replaced with selection-shortfall test. |

---

## 3. Review v5 — verdict and provenance disclosure

**Verdict (story-review-independent-v5.md §1):** *CONDITIONAL PASS — Gate 1 MAY PROCEED* once V5-01 was decided and the mechanical fixes landed. All applicable in cycle v0.15 → v0.16; they were applied and verified in-file during this packet's assembly (V5-01→D-47 cluster; V5-02 US-04 AC-7 preconditions; V5-03 US-03 AC-14 third case; V5-04 four pointer retargets; V5-05 CR-08/D-21 wording).

**Provenance disclosure (quoted intent, review §1 — verbatim source governs):**
> this pass was executed in-session by the same assistant that authored the v0.13–v0.15 amendments. Its independence is therefore *procedural* (adversarial method, fresh grep/checklist sweeps, dispositions re-verified line-by-line) — not *contextual*. Per Rule 7's spirit, the approver should treat V5-01…V5-07 as author-challenged-author findings and may commission a contextually independent confirmation pass before locking v1.0. Flagged explicitly rather than hidden.

**⚠️ DECISION REQUIRED FROM THE HUMAN APPROVER (this closes Rule 7 for v1.0):**
- **(a)** Ratify review v5 as-is (human approval + the reproducible-method argument close Rule 7), or
- **(b)** Commission a **contextually fresh confirmation pass** (fresh-context reviewer, same stated method — findings are claimed reproducible from the review's grep/checklist sweeps) before locking v1.0.

> ✅ **Ruling 2026-08-25: option (b).** Executed same day as **review v6** (`story-review-independent-v6.md`). Its own provenance disclosure (review §1): *procedural-only* independence — executed in-session; Appendix A of that review contains a paste-ready brief for a genuinely fresh-context pass whose result would supersede or confirm it. Verdict: CONDITIONAL — two Major dispositions required (V6-01, V6-02). Notably, V6-01 corrects an arithmetic error that review v5 had explicitly attested as verified.

The residual-risk note (review §5) adds: V5-01 was the same defect shape as v4's catch — a later amendment silently stranding earlier criteria — caught because the reviewer swept interactions between consecutive amendments. Standing rule reaffirmed: **every amendment gets a ripple pass over criteria derived from the words it changed.**

---

## 4. Carried confirmations

### 4.1 SM-01 — primary success metric — ✅ already confirmed
Confirmed by the product owner 2026-08-23: 100% coverage of registered non-flagged students whenever a feasible assignment exists; flagged students excluded by design ("this is the whole purpose of flagging"); CR-18 failure runs and D-22 aborts are judged on **report completeness**, not coverage. No action required; carried into the baseline.

### 4.2 Assumptions expiring at Gate 1 — ⚠️ require your "confirm" (or amendment)

Per discovery §3, the following expire at Gate 1. Confirming them here is part of the lock. (A-13 is already confirmed via D-34; **A-12 expires at Phase 6**, not here.)

| ID | Assumption (short) | Recommendation |
|---|---|---|
| A-01 | Annual matching aligned with school year; admin triggers before first school day | Confirm |
| **A-02** | *"A school's dismissal time is part of the school record"* | ✅ **Resolved 2026-08-25** — restated as *"dismissal time = the end time of the relevant shift; no separate school-level dismissal field exists at MVP"* and confirmed; applied in discovery.md (supersession annotation vs. CR-01/D-33) |
| A-03 | Vehicle capacity = passenger seats | Confirm |
| A-04 | Exported file mirrors dashboard content per role; format is Phase 3+ | Confirm |
| A-05 | Access control scoping (parent own children / driver own roster / admin all) | Confirm |
| A-06 | Parent account ↔ one or more students | Confirm |
| A-07 | Pickup/drop-off times informational, route-derived | Confirm |
| A-08 | Mid-year school change handled via CR-16 registry update + tweak | Confirm |
| A-09 | School days only; no calendar/holiday handling in MVP | Confirm |
| A-10 | Parent↔student linkage part of provisioning data | Confirm |
| A-11 | Driver/admin accounts provisioned by school/administrator | Confirm |
| A-14 | Fixed shifts only at MVP; circular shifts deferred (OQ-17) | Confirm |
| A-15 | Selecting a shift-direction reserves the whole buffered window [S−T, E+T] | Confirm |
| A-16 | Half-open intervals [start, end); exact boundary touch = non-overlap | Confirm |

**A-02 flagged (raised at packet time per handoff):** as literally written it predates the shift model. Since D-33/CR-01, a school carries **one or more shifts, each with its own start/end**, and a student is tied to exactly one shift — there is no single school-level dismissal field anymore. Proposed restatement for your confirmation: *"Dismissal time = the end time of the relevant shift; no separate school-level dismissal field exists at MVP."* If you prefer a different disposition (e.g., strike A-02 as fully absorbed by CR-01/D-33), say so at approval — either way it is recorded before the lock.

---

## 5. Notes carried from review v5 (acknowledge — no file change required)

- **V5-06 (estimate provenance):** the +20–40 pd delta behind the $18k ceiling was produced by the same agent that priced the scope. Its dominant term (allocation core, 7–15 pd) assumes an off-the-shelf exact engine (CP/MIP class) can encode CR-26 pairwise turnaround + D-45 lexicographic tie-breaks without custom search — plausible, **unverified until the optional design spike runs**. Recorded explicitly in NFR-08 (v0.16). The spike doubles as its verification.
- **V5-07 (traceability convention):** matrix rows mirror story trace lines verbatim; US-07 omits D-39 because CR-12 realizes it (established convention). Re-affirmed here for the record.

---

## 6. Budget status at Gate 1

| Ceiling | Value | Status |
|---|---|---|
| Build | **$20,000** (≈100 pd @ $200/day) | Re-baselined $6,000 → $18,000 (PO 2026-08-23, D-46); **corrected $18,000 → $20,000 2026-08-25 (V6-01)** |
| Envelope estimate | 58–96 pd ≈ **$11,600–19,200** | Corrected per V6-01 (v5's "$17,200 / ~5%" attestation was arithmetically wrong); ≈4% headroom at $20,000 |
| Operating | **$30/month** hosting + tools (≈$400/yr incl. domain) | Approved 2026-08-15; self-hosted routing (D-44) fits inside |
| Optional lever | Solver design spike, 2–3 days, ≈$400–600 | Pulls actuals toward range floor; verifies the NFR-08 solver-formulation assumption |
| Re-check triggers | Gate B before Phase-3 spend on any new scope change; again at release (Gate 7) | Standing |

---

## 7. Remaining open questions — all non-blocking, triggers named

| ID | Topic (short) | Trigger |
|---|---|---|
| OQ-06 | Direction-scope of a US-06 tweak | Before US-06 is built or baselined as Should |
| OQ-10 | Plan lifecycle across runs; post-publication shift-time changes | Before implementing plan supersession / shift editing |
| OQ-11 | Mid-year flag/removal propagation to live views | Before mid-year flows are implemented |
| OQ-12 | Driver person identity shown to parents; parent credential delivery | Before parent-account UX implementation |
| OQ-13 | Stable identifiers & duplicate-registration rules | Before registry implementation |
| OQ-15 | Student registration flow (who creates the record; when home location must exist) | Phase 2 flow design; affects US-02 wording later |
| OQ-17 | Circular-shift rotation semantics | Post-MVP |

None may be marked resolved without your explicit answer in-session (standing rule).

---

## 8. Queued immediately after the lock

1. **Version bump** in both artifacts to **v1.0 BASELINE LOCKED**, §6 changelog entry in each, full ripple sweep over every AC/CR citing changed wording (amendment protocol; stranded-criteria defect class V4-08/V5-01 is this project's recurring failure mode).
2. **Reader Edition**: generate `docs/requirements/requirements-consolidated.md` and `docs/requirements/discovery-consolidated.md` folding resolved OQs and supersession annotations into clean current-truth prose. Originals stay untouched as the audit trail. Headers cite: *"Derived from baseline v1.0."*
3. *(Optional)* Authorize the **solver design spike** (D-46 lever) — also verifies the NFR-08 estimate assumption (§5 above).

---

## 9. Approval decision

Choose one:

- **[ ] APPROVE — lock v1.0** (optionally with the A-02 restatement from §4.2): both artifacts bump to v1.0 BASELINE LOCKED; queued tasks proceed.
- **[ ] APPROVE AFTER CONFIRMATION PASS — commission a contextually independent review v6** (same method as v5, fresh context) before locking; findings triaged, then lock.
- **[ ] REJECT — with findings:** state them; remediation cycle begins; Gate 1 re-submitted.

Signature: ____________________ Date: ____________

> ✅ **Exercised 2026-08-25: APPROVE AFTER CONFIRMATION PASS.** All §4.2 assumptions confirmed unchanged except A-02 (restated as above). Review v6 executed and **fully remediated in v0.18**: V6-01 corrected (ceiling $20,000 / envelope high end $19,200); V6-02 settled by PO answer — OQ-06 → **D-48** (tweak direction-scope: admin-selected per tweak, both-default), US-06 AC-5 added; V6-03…05 mechanical batch applied. Verification review v7: **PASS** (zero new findings). **LOCKED: both artifacts at v1.0 BASELINE LOCKED — 2026-08-25.** Post-lock queue: Reader Edition (`*-consolidated.md`).
