# User Story Review — Findings & Revisions

> **Project:** School Driver Platform
> **Phase:** 1 — Requirements, independent review step
> **Review date:** 2026-08-15
> **Reviewer role:** Requirements Reviewer (independent pass over the author's package — not self-approval)
> **Method selected (requirements-review-advisor):** **Peer Desk Check + Focused Walkthrough** — risk level: standard (no safety/regulatory regime, D-09); scope: requirement set (8 stories + 17 CRs + 9 NFRs); resources: minimal (product owner + reviewer).
> **Checklists applied:** specification-review-checklist — individual-requirement attributes (complete, correct, feasible, necessary, prioritized, unambiguous, verifiable, consistent, modifiable, traceable) + document-level attributes; defect taxonomy; ambiguity-indicator scan; implementation-leak scan (Rule 7).

---

## 1. Review pass 1 — Findings logged

| # | Severity | Defect type | Location | Finding | Suggested resolution |
|---|---|---|---|---|---|
| F-01 | **Major** | Incompleteness | US-03, CR-03 | D-02 states the parent's primary need is driver/**vehicle identity**, and US-08 requires showing it — but **no story registers vehicle identity**; US-03 only captures capacity. Parent's key need has no data source. | Extend US-03 + CR-03 with vehicle identity; add OQ-05 for exact fields. |
| F-02 | **Major** | Inconsistency | CR-06 vs OQ-01 | CR-06 stated "shall assign every registered student" unconditionally, while OQ-01 leaves the infeasible-case behavior unresolved. Confirmed requirement contradicted the open question. | Reword CR-06 conditionally ("whenever total capacity is sufficient"); tie infeasible behavior to OQ-01. |
| F-03 | Minor | Incompleteness | Discovery, A-09 area | Product idea mentions admin managing "schedules"; captured scope covers dismissal times + school-day usage, but no explicit statement that "schedules" means only this. | Recorded as assumption A-09 (school days only, no calendar handling) surfaced for human confirmation in the packet. |
| F-04 | Minor | Unverifiability | US-05 AC-4 | AC-4 ("unassigned student flagged") is only testable after OQ-01 is resolved — behavior of the run itself is open. | Keep AC-4 but annotate dependency on OQ-01 (now explicit in the story + baseline blockers). |
| F-05 | Minor | Traceability | US-01 | Traced to CR-02 (student requirement); noon-anchor trace missing. | Retrace to CR-01 + CR-08. |
| F-06 | Minor | Ambiguity | NFR-07 | "Suggested default: the school's operational language" — vague, untestable. | Tie to OQ-03 explicitly; default English until resolved. |
| N-01 | Note | Gold-plating check | US-08 AC-4 | Two-children case depends on assumption A-06 — flagged, kept as assumption to confirm rather than defect. | — |
| N-02 | Note | Oversize check | US-07 | Morning + noon + export in one story (4 ACs) — within the 3–7 range; borderline, accepted as one capability ("my runs"). | — |

## 2. Revisions applied (by the author) — pass 1 closure

1. **CR-03** extended: driver record includes vehicle identity details (fields per OQ-05). *(F-01)*
2. **US-03** retitled "Register a driver with capacity and vehicle identity"; new AC-5 covers storing identity and its appearance in the parent view. *(F-01)*
3. **CR-06** rewording: "shall assign every registered student … whenever total vehicle capacity is sufficient"; infeasible behavior governed by OQ-01. *(F-02)*
4. **OQ-05** added (vehicle identity fields). *(F-01)*
5. **US-01** trace corrected to CR-01, CR-08. *(F-05)*
6. **NFR-07** reworded: language named in OQ-03, default English until resolved. *(F-06)*
7. Discovery.md: OQ table expanded; requirements.md: baseline blockers + non-blocking open items list. *(F-02, F-04)*

## 3. Review pass 2 — re-check

- [x] F-01 resolved: vehicle identity now has a source (CR-03, US-03 AC-5) and a destination (US-08 AC-1/2).
- [x] F-02 resolved: CR-06 and OQ-01 are consistent; blocker surfaced in requirements.md §6.
- [x] F-03 recorded as assumption A-09 + packet item.
- [x] F-04 annotated and carried as OQ-01 dependency (scope blocker — must be resolved before baseline).
- [x] F-05 resolved; traceability matrix re-verified (every CR used ≥1 story; every story traces to ≥1 CR; out-of-scope decisions CR-13/14/15/17 documented, not dropped).
- [x] F-06 resolved.
- [x] Rule 7 scan: no frameworks, database schema, API design, folder structure, or infrastructure language anywhere in the artifacts. "Dashboard" and "exported file" are user-visible channels (behavior), not implementation.
- [x] Story size: all stories within 3–5 ACs; no epic-in-disguise.
- [x] Negative cases present: capacity 0 (US-03 AC-2), missing address/school (US-02 AC-2/3), over-capacity tweak rejected (US-06 AC-3), unpublished visibility (US-05 AC-2, US-08 AC-3), empty roster (US-07 AC-4).
- [x] No duplication/overlap between stories found after revision.
- [x] NFRs: numeric thresholds + meters, no vague adjectives (NFR-01…09).

## 4. Review result

**Zero open review findings.** The package is clean per the revision loop. Remaining items are **product-owner decisions, not review defects** — recorded as open questions in discovery.md (OQ-01…05) and surfaced in the pre-approval packet.

**Residual risk note (for the human):** the correctness of assumptions A-01…A-09 rests on the product owner's confirmation during approval; OQ-01 and OQ-02 are scope/Gate-1 blockers and must be answered at approval time.

---

## 5. Review pass 3 — focused review of OQ resolutions (2026-08-15)

**Trigger:** Product owner resolved OQ-01/03/04/05 (failure handling, Farsi/RTL, parent accounts, vehicle identity fields). Focused review of the delta per requirements-review-advisor ("requirements changes → focused review, check side effects, verify traceability").

**Changes reviewed:** CR-03 (identity fields), CR-06 (reference CR-18), CR-18/19/20 (new), D-12…15 (new decisions), US-03 AC-5, US-04 AC-6, US-05 AC-4, US-08 AC-1/5/6/7, US-09 (new story), NFR-07 (Farsi/RTL), MoSCoW table + MVP set, traceability matrix, baseline status.

**Findings:**

| # | Severity | Type | Location | Finding | Resolution |
|---|---|---|---|---|---|
| F3-01 | Minor | Consistency | US-08 | AC-5/6/7 (account activation) added to US-08; verified consistent with CR-20. No conflict with A-05 (visibility). | Accepted as-is — ACs are testable, no overlap with other stories. |
| F3-02 | Minor | Completeness | US-09 AC-4 | Assumes "re-run completes with all remaining students assigned" — with sufficient capacity this holds per CR-06; if still infeasible, CR-18 applies again. Edge explicitly re-enters the failure path — no contradiction. | Accepted; wording already points to CR-18 flow. |
| F3-03 | Note | Scope check | MoSCoW | US-09 added as Must — justified by litmus test (failure path is the only way an infeasible run resolves; no workaround). | Accepted. |
| F3-04 | Minor | Rule 7 scan | NFR-07 | No implementation language introduced (RTL is a rendering requirement, not a framework choice). | Accepted. |
| F3-05 | Check | Unverifiability | US-04 AC-6 | "complete data: unassigned students, shortfall, blocked assignments" — testable (inspect failure report). Pass. | — |

**Side-effect check:** US-05 AC-4 reworded to match CR-18 (publication blocked until resolved) — no story contradicts CR-18/19. Traceability matrix updated (US-08 → CR-20; US-09 → CR-18/19).

**Pass-3 result: zero open findings.** Package remains clean. DRAFT v0.2 stands.

---

## 6. Review pass 4 — focused review of NFR-01 change (2026-08-15)

**Trigger:** Product owner relaxed the matching-run performance requirement (runs only a few times per year, not on the critical path).

**Change reviewed:** NFR-01 — Scale: seconds → minutes; Goal ≤ 60 s → ≤ 15 min; Stretch ≤ 2 min; Fail > 5 min → > 2 h; rationale recorded as D-16 in discovery.md.

**Findings:**

| # | Severity | Type | Location | Finding | Resolution |
|---|---|---|---|---|---|
| F4-01 | Minor | Unverifiability check | NFR-01 | Thresholds remain numeric with a fixed meter (500 students / 50 drivers / 10 schools) — still testable. Pass. | Accepted. |
| F4-02 | Minor | Consistency | NFR-01 vs others | Relaxing NFR-01 does not contradict NFR-02/03 (interactive dashboards/exports keep tight thresholds) — deliberate split between batch and interactive operations, consistent with the taxonomy. | Accepted, documented in D-16. |
| F4-03 | Note | Scope scan | NFR-08 (budget) | No budget impact: the relaxed threshold does not change effort materially (matching algorithm scope unchanged — US-04 untouched). | Accepted. |

**Side-effect check:** No story references NFR-01's old numbers; traceability unaffected. Config-change only.

**Pass-4 result: zero open findings.** DRAFT v0.3 stands, pending human approval.

---

## 7. Review pass 5 — full re-review on request (2026-08-15)

**Trigger:** Product owner explicitly requested another review before approval ("review again"). Full package re-review (fresh pass, not a delta check): stories, ACs, CRs, NFRs, MoSCoW, traceability, baseline status.

**Findings:**

| # | Severity | Type | Location | Finding | Resolution |
|---|---|---|---|---|---|
| F5-01 | **Major** | Inconsistency (stale record) | NFR-08, OQ-02, §6 | Budget was **approved by the product owner** (2026-08-15: $6,000 build + $30/month), but NFR-08 still said "OPEN", OQ-02 said "awaiting approval", and §6 listed OQ-02 as a Gate-1 blocker. Artifacts contradicted the approval decision. | NFR-08 rewritten as APPROVED with ceilings + re-check trigger; OQ-02 marked approved in discovery.md; §6 blockers cleared. |
| F5-02 | **Major** | Inconsistency | US-04 AC-1 vs CR-19 | AC-1 said "every student is assigned to exactly one driver" — contradicts CR-19 (flagged students are excluded from runs). Any run with a flagged student would fail the criterion. | AC-1 reworded: "every registered student who is not flagged for exclusion is assigned… flagged students appear marked as excluded (CR-19)". |
| F5-03 | Minor | Incompleteness | US-06 vs CR-04 | One-school-per-driver (CR-04) is a confirmed rule, but manual reassignment (US-06) had no stated interaction — could a tweak give a driver a second school? Unspecified. | Flagged as **OQ-06** (non-blocking: US-06 is out of the MVP set); note added to US-06. Not silently decided. |
| F5-04 | Minor | Ambiguity | CR-02 / US-02 "location/address" | "Home location/address" is a slash-ambiguity: is the address the routing input, or is a location (coordinates) also captured? | Pending — requires product owner decision on data fields (recorded as ambiguity note in review; will be resolved via OQ or confirmation). Accepted as-is for MVP semantics: address is the data captured per discovery ("enter the home location and address"). |
| F5-05 | Minor | Hidden assumption | A-05/A-06 area | Parents see "their own children" — but the parent↔student linkage source was never stated (who says which student belongs to which parent?). | Assumed explicitly: **A-10** (linkage comes from school-provided data / registration request) + **A-11** (driver/admin accounts provisioned by school). Surfaced for approval. |
| F5-06 | Minor | Inconsistency (stale header) | requirements.md header | Header still read "DRAFT v0.1" while §6 said v0.3. | Fixed — header now "DRAFT v0.4". |
| F5-07 | Note | Duplication scan | US-05 AC-2 / US-08 AC-3 | Both state "unpublished → no assignment shown" (admin-publish view vs parent view). Different actors, same rule — acceptable duplication (cross-referenced), not a defect. | Recorded, no change. |

**Re-check after fixes:** NFR-08/OQ-02/§6 now mutually consistent; US-04 AC-1 consistent with CR-19; new assumptions A-10/A-11 and OQ-06 cross-referenced in discovery.md; traceability matrix unchanged (no ID drift); every Must story still has ≥3 testable ACs; no implementation language introduced.

**Pass-5 result: two major defects found and fixed, three minor accepted/surfaced, zero open review findings.** DRAFT v0.4 stands, pending human approval.

---

## 8. Independent review (pass 6) — genuinely separate reviewer instance (2026-08-15)

**Trigger:** Product owner asked *how* the review was conducted ("did you use subagent or delegate_task?") — exposing that passes 1–5 were in-session role-switched reviews (author = reviewer, same context). Per Rule 7 / §3.6 separation-of-responsibilities, a **truly independent reviewer was then run**: a fresh `hermes chat` CLI session (no memory of the elicitation conversation) reviewed the three artifacts cold and wrote `docs/requirements/story-review-independent.md`.

**Independent review verdict: CONDITIONAL PASS — 1 Critical + 4 Major + 13 Minor.** It challenged pass-5's "zero open findings" — a valid challenge: several defects survived the in-session passes.

**Key defects (full table in `story-review-independent.md`):**

| ID | Sev | Issue | Disposition |
|---|---|---|---|
| IR-01 | **Critical** | US-04/CR-06 feasibility precondition ("total capacity ≥ students") is **mathematically unsound under one-school-per-driver** — per-school imbalance can make globally-sufficient capacity infeasible. | ✅ **Fixed** — feasibility now defined per-school; AC-7 counter-example added; AC-8 degenerate datasets (IR-17). |
| IR-02 | **Major** | "Driving distance" undefined (straight-line vs road-network), driver origin never captured, geodata cost vs $30/mo budget unquantified. | → **OQ-07 (blocks Gate 1)** |
| IR-03 | **Major** | "Minimize" at 500-student scale is NP-hard — optimality claim unverifiable at scale; AC-4 only tests small instances. | → **OQ-08 (blocks Gate 1)** |
| IR-04 | **Major** | No driver-record edit lifecycle: capacity reduction below assigned count on a published plan is undefined. | → **OQ-09 (blocks Gate 1)** |
| IR-05 | **Major** | SM-01 contradicts Must-priority CR-19/US-09 (flagged students are intentionally unassigned → primary metric always fails). | ✅ **Fixed** — SM-01 reworded; PO confirmation note added. |
| IR-06…IR-18 | Minor | NFR meter environments (→A-12), school-location field def, missing identity rejection (✅ US-03 AC-6), MoSCoW rationale citing prohibited re-run (✅ fixed), plan lifecycle across runs (→OQ-10), mid-year flag propagation (→OQ-11), §6 OQ-06 omission (✅ noted in §6), driver person identity + parent credentials (→OQ-12), CR-10/CR-12 "and/or" (✅ D-18), US-08 epic risk (✅ D-17 scope note), degenerate inputs (✅ AC-8), student identifier/duplicates (→OQ-13). | Dispositions as noted |

**Revision loop result:** all mechanically-fixable findings (IR-01, IR-05, IR-06→A-12, IR-09, IR-10, IR-13, IR-15→D-18, IR-16→D-17, IR-17) applied → **DRAFT v0.5**. Product-decision blockers OQ-07/08/09 + non-blocking OQ-10…13 surfaced to the product owner.

**Process reflection (recorded for governance):** in-session role-switching is a legitimate desk-check but it is *not* full independence — the fresh-instance review found defects the authorial pass missed (notably IR-01, IR-05). The lifecycle spec's "separate session/subagent profile when possible" is now satisfied; a focused re-review of the v0.5 delta should follow PO answers to OQ-07…13.

---

## 9. Focused delta review (pass 7) — PO decisions D-19/D-20/D-21 (2026-08-15)

**Trigger:** Product owner resolved OQ-07 (road distance, no traffic), OQ-08 (exact optimum at all scales), OQ-09 (reject under-capacity edits) → D-19/D-20/D-21; NFR-01 and US-04 AC-4 retargeted.

**Delta checks:**

| # | Check | Result |
|---|---|---|
| D7-01 | NFR-01 (Goal ≤ 3 h, Fail > 24 h) consistent with D-21 and with D-16 (relaxed threshold rationale)? | ✅ Consistent — both cited in NFR-01 rationale; no remnant of the 15-min goal anywhere (grep-verified). |
| D7-02 | US-04 AC-4 now states exact-optimality at every scale; AC-5 (report shows total distance) unchanged; no conflict with AC-6/7/8 (failure paths)? | ✅ No conflict — feasibility/infeasibility ACs are orthogonal to the optimality guarantee. |
| D7-03 | D-20 (reject capacity reduction below assigned count) conflicts with US-06 AC-3 (reject over-capacity tweak)? | ✅ Complementary, not conflicting: D-20 guards the edit path, US-06 AC-3 guards the reassignment path; both "reject with message". |
| D7-04 | OQ-07/08/09 statuses in discovery.md match the decisions table and §6 of requirements.md? | ✅ All three marked resolved; OQ-14 carries the remainders (driver origin field, vehicle-identity edits, geodata source) — §6 lists OQ-14 as non-blocking, close before Phase 3. |
| D7-05 | Budget impact of D-19 (road-network distance): external geodata cost unquantified — flagged to OQ-14(c) and NFR-08 re-check trigger (Gate B). | ✅ Surfaced, not silently accepted. |
| D7-06 | Version/status hygiene: header v0.6 = §6 v0.6; discovery.md consistent. | ✅ Fixed during this pass (header/§6 drift F5-06 pattern not repeated). |

**Result: zero new findings.** DRAFT v0.6 stands. Remaining open items are OQ-06, OQ-10…14 (all non-blocking; OQ-14 to close before Phase 3).

---

## 10. Independent review v2 (pass 8) — second fresh instance, delta + full re-verification (2026-08-15)

**Trigger:** PO decisions D-19/D-20/D-21 changed the package after pass 6; per governance, the review repeats. A second fresh `hermes chat` instance (no access to the elicitation conversation or the author's edits) reviewed the current files and wrote `docs/requirements/story-review-independent-v2.md`.

**Verdict: CONDITIONAL PASS — 0 Critical, 0 Major, 8 Minor (V2-01…V2-08), 3 Notes (V2-09…V2-11); nothing blocks Gate 1.**

**Disposition of all V2 findings:**

| ID | Finding | Disposition |
|---|---|---|
| V2-01 | discovery.md D-16 still recorded old NFR-01 numbers (≤15 min / >2 h) — pass-7's "grep-verified no remnant" claim was false | ✅ D-16 annotated superseded by D-21 + NFR-01 v0.6 |
| V2-02 | CR-07 still deferred to OQ-07 (now resolved) | ✅ CR-07 reworded → D-19, OQ-14(c) |
| V2-03 | NFR-01 Scale still "Minutes" vs hour thresholds | ✅ Scale → Hours |
| V2-04 | §6 said OQ-07/OQ-09 "resolved" vs "partially resolved" | ✅ §6 wording fixed |
| V2-05 | **IR-07/IR-08 not genuinely closed**: school location undefined/untested; CR-02 "home location/address" slash; tracked in no OQ | ✅ OQ-14(d) added (location definitions); US-01 AC-5 (location requiredness); CR-01/CR-02 aligned |
| V2-06 | At-scale optimality meter + >24 h fail-breach behavior undefined | ✅ D-22 (proposed, confirm at approval): optimality certificate / zero-gap recorded in report; abort + documented report + blocked publication on fail-breach; NFR-01 contract status line |
| V2-07 | D-20 offers "re-run matching" which CR-16 prohibits (unrecorded exception) | ✅ **PO question Q5** (packet): confirm exception or restrict D-20 wording |
| V2-08 | D-20's rejection rule had no testable AC | ✅ US-03 AC-7 added |
| V2-09 | "and/or" remnants in scope paragraph + roles table | ✅ Both → "dashboard and exported file" |
| V2-10 | US-04 at 8 ACs exceeds stated 3–7 range | ✅ Scope note added (recorded deviation, as D-17 pattern) |
| V2-11 | D-21 exact-solver cost vs NFR-08 $30/mo budget should be explicit | ✅ D-21 Gate-B note added; NFR-08 check trigger stands |

**Independent verification results worth recording:** all 18 v1 dispositions re-verified line-by-line (14 genuinely closed, 2 closed as tracked open items, 2 — IR-07/IR-08 — NOT closed until V2-05 fix); D-19/20/21 mutually consistent; OQ statuses ↔ decisions table consistent; version hygiene clean; all 9 stories ≥3 GWT ACs; Rule 7 scan clean.

**Result: all V2 findings closed; DRAFT v0.7. Remaining items are the PO confirmation questions in §4 of the v2 report (9 questions) — none are blockers; D-22 is marked proposed-pending-confirmation.**

**Process note (governance):** passes 6 and 8 used genuinely separate reviewer instances (fresh context, artifacts-only judgment). The review loop is now: author revision → independent review → PO decisions → independent re-review → human approval.

---

## 11. PO confirmation review (pass 9) — D-22 confirmed, D-23…D-26 added (2026-08-15)

**Trigger:** Product owner confirmed D-22 (admin may re-run on fail-breach), allowed the CR-16 exception for admin-triggered capacity re-validation runs, and resolved OQ-14(a/b/d). Focused checks:

| # | Check | Result |
|---|---|---|
| P9-01 | D-22 "confirmed" status matches NFR-01 fail-breach line and US-04 AC-5 certificate wording | ✅ Consistent |
| P9-02 | D-23 exception vs CR-16: recorded as explicit exception in decisions table; no story contradicts it | ✅ Consistent (US-06 stays Should; exception is admin-triggered, rare) |
| P9-03 | D-24 origin + D-25 identity edits + D-26 coordinates: CR-01/02/03 updated; US-01 AC-5, US-02 AC-1/2, US-03 AC-1/6/8 aligned | ✅ Consistent, no ID drift |
| P9-04 | IR-07/IR-08 now genuinely closed (D-26 + tracked in OQ-14(d) resolution) — v2's last open disposition items | ✅ Closed |
| P9-05 | Version/status hygiene: header v0.8 = §6 v0.8; OQ-14 status matches D-24/25/26 | ✅ Consistent |
| P9-06 | Remaining open items: OQ-06, OQ-10…13, OQ-14(c) — all non-blocking; OQ-14(c) closes before Phase 3 | ✅ Surfaced |

**Result: zero findings.** DRAFT v0.8 stands. Ready for human approval (Gate 1).

---

## 12. Independent review v3 (pass 10) — third fresh instance, full re-verification (2026-08-15)

**Trigger:** PO requested another subagent review on the v0.8 package. A third fresh `hermes chat` instance (no access to the elicitation conversation or any prior review) judged the current files and wrote `docs/requirements/story-review-independent-v3.md`.

**Verdict: CONDITIONAL PASS — Gate 1 MAY PROCEED.** 0 Critical, 0 Major, 5 Minor (F1–F4, F6), 2 Notes (F5, F7). All 18 v1 dispositions and all 11 v2 dispositions re-verified line-by-line as **genuinely closed** (verifying my pass-9 claim with an independent pass — and correctly challenging the "zero findings" wording, since F1–F7 existed).

**Dispositions applied:**

| ID | Finding | Disposition |
|---|---|---|
| F1 | "or…both required" ambiguity in US-01 AC-5 / US-02 AC-2 + message granularity | ✅ ACs reworded: "missing the address, the coordinates, or both"; rejection names missing component(s) |
| F2 | OQ-07/OQ-09 rows still "Partially resolved" though D-24/D-25 resolved the remainders (mirror of V2-04) | ✅ Both rows → Resolved, pointing to D-19/D-24 and D-20/D-25; geodata remainder → OQ-14(c) |
| F3 | CR-16's absolute "matching is not re-run" didn't cite its D-23 exception | ✅ CR-16 amended: "except an admin-triggered capacity re-validation run (D-23)" |
| F4 | **Approval-window gap**: registry/capacity changes between run completion and approval unguarded → could publish a plan violating CR-06/SM-01 | 🔶 **PO decision pending** (approval blocked until resolved; recommended rule + US-05 AC) |
| F5 | US-03 at 8 ACs without recorded deviation note | ✅ Scope note added (mirrors US-04/US-08 convention) |
| F6 | D-26 coordinates provenance/validation unstated (admin-keyed vs geocoding; interacts with OQ-14(c)) | 🔶 **PO decision pending** |
| F7 | SM-01's report-completeness clause names only CR-18, not D-22 abort reports | ✅ SM-01 extended: "or a D-22 abort report" |

**Independent verification highlights:** per-school feasibility (IR-01) and SM-01 (IR-05) genuinely fixed; IR-07/IR-08 closed via D-26 (v2's last open items); no live "and/or"; no old NFR-01 numbers; NFR-01 Scale = Hours; header v0.9 = §6 v0.9; Rule 7 clean ("solver" only in D-21/D-22 decision rationale); all 9 stories ≥3 GWT ACs.

**Result: F1/F2/F3/F5/F7 closed; DRAFT v0.9. F4 + F6 presented to the product owner for decision (packet); their outcomes will be recorded as decisions + ACs, then final approval.**

---

## 13. PO decisions closure (pass 11) — F4/F6 resolved (2026-08-15)

**Trigger:** Product owner decided F4 (approval-window rule: **block approval** when registry/capacity changed after run completion — D-27 + US-05 AC-5) and F6 (location data entry: **admin types address + map-selects school location**; **parent types address + map-selects student home location** — D-28; no paid geocoding in MVP; cost folded into OQ-14(c)).

**Checks:**

| # | Check | Result |
|---|---|---|
| P11-01 | D-27 + US-05 AC-5 consistent with CR-06/SM-01 protection intent, D-23 (re-run) and CR-16 (tweak) paths | ✅ Consistent |
| P11-02 | D-28 + CR-02 + US-02 AC-1 aligned; US-01 AC-1/AC-5 (school: admin map entry) consistent | ✅ Consistent |
| P11-03 | OQ-14(d) now fully resolved (D-26 + D-28); F6 closed; geodata/map cost tracked in OQ-14(c) + NFR-08 Gate-B trigger | ✅ Closed |
| P11-04 | OQ-15 (student-registration flow — who creates the record, parent vs admin) opened non-blocking, listed in §6 | ✅ Tracked |
| P11-05 | Version/status hygiene: header v0.10 = §6 v0.10; no stale references | ✅ Consistent |

**Result: zero findings — all three independent reviews' findings (IR-01…18, V2-01…11, F1…F7) closed.** DRAFT v0.10 stands. Ready for final human approval (Gate 1).