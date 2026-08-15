# Independent Requirements Review v3 — School Driver Platform

> **Project:** Smart transportation platform for school students (daily home ↔ school shuttles)
> **Phase:** 1 — Requirements, **independent review step (governance Rule 7 / §3.6: separation of responsibilities — challenge, do not self-approve)**
> **Review date:** 2026-08-15 (third independent instance, v3)
> **Reviewer:** Independent Requirements Reviewer (fresh context — did NOT see the elicitation conversation, did NOT participate in any prior review, did NOT see the author's edits; judged the artifacts as they exist NOW)
> **Artifacts reviewed (current state):**
> - `docs/requirements.md` — DRAFT v0.8 (US-01…09, ACs, MoSCoW, NFR-01…09, traceability, §6 baseline)
> - `docs/requirements/discovery.md` — CR-01…20, A-01…12, D-01…26, OQ-01…14, SM-01
> - `docs/requirements/story-review.md`, `story-review-independent.md` (v1), `story-review-independent-v2.md` (v2) — **treated strictly as history.** Every claimed disposition re-verified against the current files; nothing inherited.
> **Method:** Adversarial desk review against the defect taxonomy (ambiguity, incompleteness, inconsistency, infeasibility, unverifiability, duplication, gold-plating, design-in-requirements), plus hidden-assumption scan, scope check, story-size check, AC testability check (≥3 GWT per story), edge-case sweep, CR↔story consistency, Rule 7 implementation-leak scan (keyword grep: api, endpoint, database, schema, json, sql, framework, react, docker, aws, microservice, postgres, elastic, redis, solver, mip).
> **Scope:** (a) internal consistency of the D-22…D-26 decisions and the US-01/02/03 AC changes (the delta since v2); (b) genuine closure of all v1 findings (IR-01…IR-18) and v2 findings (V2-01…V2-11); (c) stale text contradicting any decision; (d) version/status hygiene; (e) readiness for Gate 1.

---

## 1. Verdict

**CONDITIONAL PASS — Gate 1 MAY PROCEED; do not lock baseline v1.0 as-is until the conditions below are applied in this same revision cycle.**

Nothing blocks Gate 1. The v1 Critical/Major defects (IR-01 feasibility criterion, IR-05 SM-01) are genuinely fixed in the current files, all 11 v2 findings are genuinely closed, and the D-22…D-26 decision set plus the US-01/02/03 AC changes are internally consistent — I found **no Major or Critical defect and no new contradiction introduced by the delta**. In particular, the last two dispositions v2 left open (IR-07/IR-08) are now genuinely closed via D-26, verified line-by-line.

However, "zero findings" (pass-9's claim) does not survive a fresh adversarial pass: 5 Minor and 2 Note defects remain, including one real edge-case gap the entire review history missed (F4 — the approval window between run completion and publication is unprotected against registry/capacity edits: D-20's guard only applies once a plan is approved/published, so a pending report that violates the new state could be published, breaking CR-06/SM-01). All findings are fixable by text/status corrections or small recorded PO decisions; none invalidates any acceptance criterion as written.

**Conditions for baseline (v1.0):**
1. Apply the mechanical fixes: F1 (AC wording), F2 (OQ-07/OQ-09 status rows), F3 (CR-16 exception cross-reference), F5 (US-03 scope note), F7 (SM-01 clause).
2. Record PO decisions (or add ACs) for F4 (approval-window validity) and F6 (coordinates provenance/validation).
3. Carry the SM-01 confirmation (v1 Q4 / v2 Q7, still formally outstanding at approval) into the approval packet.

---

## 2. Findings (v3)

| ID | Severity | Defect type | Location | Description | Suggested fix |
|---|---|---|---|---|---|
| F1 | Minor | Ambiguity ("or" + "both" wording) | requirements.md US-01 AC-5 (line 28), US-02 AC-2 (line 41) | D-26 requires address **and** coordinates, both mandatory; the ACs say "without a location (**address or coordinates**, both required…)" / "without a home address **or** coordinates". The "or" here is the exact ambiguity indicator this package hunts elsewhere (IR-08, IR-15/V2-09). The parenthetical rescues the meaning, but a tester could read "either one suffices". The rejection-message spec ("indicating the **missing location field**", singular) also under-specifies which component is named when exactly one is absent. | Reword the Given clauses: "a school record missing the address, the coordinates, or both (both required per D-26)" and "a student record missing the home address, the coordinates, or both…"; make the rejection message name the missing component(s). |
| F2 | Minor | Inconsistency (stale status — mirror of V2-04) | discovery.md OQ-07 (line 117), OQ-09 (line 119) | Both rows remain "🔶 Partially resolved" with "Remaining:" clauses listing items that are since **resolved**: OQ-07 "Remaining: driver origin field…" → D-24 (OQ-14(a) ✅); OQ-09 "Remaining: vehicle-identity edits after publication…" → D-25 (OQ-14(b) ✅). requirements.md §6 now correctly says "OQ-07 and OQ-09 resolved (remainder (c) of OQ-14…)" — so discovery.md contradicts the decisions table it hosts. V2-04 fixed this drift in the opposite direction; it now lives in the OQ rows. | Mark OQ-07 ✅ Resolved 2026-08-15 → D-19 (distance semantics) + D-24 (driver origin); remainder geodata source/cost → OQ-14(c). Mark OQ-09 ✅ Resolved 2026-08-15 → D-20 (capacity-edit rejection) + D-25 (identity edits); remainder → OQ-14(c). |
| F3 | Minor | Inconsistency (absolute rule text vs recorded exception) | discovery.md CR-16 (line 47); compare D-23 (line 100) | CR-16 states "**matching is not re-run**" with no qualifier; D-23 records the admin-triggered capacity re-validation run as an explicit exception. The exception exists only in the decisions table — a reader of CR-16 alone (or of a trace from US-06) sees an absolute prohibition the PO has overridden. The package's own convention is to annotate CRs with their governing decisions (CR-01 "D-26", CR-07 "D-19", CR-10 "D-18"); CR-16 violates that convention. No story contradicts D-23 (P9-02 verified true), but the rule text should cite its exception. | Amend CR-16: "…matching is not re-run, **except an admin-triggered capacity re-validation run (D-23)**; no day-of edits." |
| F4 | Minor | Incompleteness (missing edge case — approval window) | requirements.md US-05 (AC-1…4); discovery.md D-20, CR-06, SM-01 | No rule covers registry/capacity changes made **between run completion and approval**. D-20's guard applies only "while an **approved/published** plan exists" — so reducing a driver's capacity below the pending report's assignment count is unrestricted before approval, and approving then publishes a plan that violates CR-06 (hard capacity) and SM-01 (coverage: a student added after the run is unassigned in the published plan). US-01 AC-4 handles only dismissal-time changes. OQ-10 covers the *two-report* case, not the first-approval window. | PO decision + a US-05 AC: "Given a registry or capacity change made after a matching run completed and before the report is approved, when the administrator approves the report, then approval is blocked with a message that the report no longer matches the registry (re-run per D-23, tweak per CR-16, or revert the change)" — or, alternatively, forbid such edits while a report is pending. |
| F5 | Note | Oversize (deviation unrecorded) | requirements.md US-03 (8 ACs) | US-03 grew from 6 to **8 ACs** (AC-7 D-20 guard, AC-8 D-25 identity edit) and now exceeds the stated 3–7 range with **no scope note**, breaking the package's own recording convention (US-04 note per V2-10; US-08 note per D-17). Content is one coherent capability (driver record lifecycle: create + edit guards), so no split is required — only the recorded deviation. | Add a one-line scope note to US-03 mirroring the US-04 pattern: creation (AC-1…6), capacity-edit guard (AC-7, D-20), post-publication identity edit (AC-8, D-25) — accepted as one story; recorded deviation from the 3–7 range. |
| F6 | Minor | Hidden assumption | discovery.md D-26, CR-01/CR-02; requirements.md US-01 AC-5, US-02 AC-1/2 | D-26 requires address **and coordinates** for every school and student, but nothing states where coordinates come from (admin manually keyed? derived by geocoding?) or how they are validated (coordinates of the wrong city? 0,0?). If the system geocodes, that is a cost component that belongs inside OQ-14(c)'s $30/month question and a "missing coordinates" rejection can never fire (the ACs assume admin-supplied data). If the admin keys them, data-entry burden and accuracy are untested (NFR-09 has no such invalid-value case). | Record a PO decision or assumption: coordinates are supplied/validated how, at what precision; fold any geocoding dependency into OQ-14(c); add a validation note under NFR-09's meter if admin-keyed. |
| F7 | Note | Ambiguity / Incompleteness (metric clause) | discovery.md SM-01 (line 132) | SM-01's report-completeness clause names only "a documented **CR-18** failure report". D-22 introduced a second designed-failure class — the **>24 h abort** produces a "documented failure report" that is not a CR-18 infeasibility report; the primary metric's evaluation basis for such runs is unstated (literal reading: coverage fails, even though the abort is designed behavior). | Extend the clause: "runs that terminate in a documented CR-18 failure report **or a D-22 abort report** are evaluated on report completeness, not coverage." |

**Severity counts: 0 Critical, 0 Major, 5 Minor (F1–F4, F6), 2 Notes (F5, F7).** No finding blocks Gate 1; F4 and F6 need PO words, the rest are text/status corrections.

---

## 3. Verification checklist

### 3.1 (a) D-22…D-26 decision set and US-01/02/03 AC changes — internal consistency, no new contradictions

| Check | Result |
|---|---|
| D-22 (confirmed): optimality certificate for at-scale runs + >24 h abort, documented failure report, publication blocked, admin may re-run/adjust | ✅ Consistent everywhere: discovery D-22 ↔ NFR-01 fail-breach line (requirements.md line 199) ↔ NFR-01 contract-status line (line 198) ↔ US-04 AC-5 ("certificate of proven zero gap") ↔ §6 "D-22 confirmed" ↔ OQ-08 chain. No AC contradicts the abort path (US-04 AC-4/AC-5 are about the normal path; AC-6/7/8 about infeasibility — orthogonal) |
| D-23: admin-triggered capacity re-validation run = explicit exception to CR-16 | ✅ Recorded as explicit exception in the decisions table; D-20's "re-run matching" revalidation option is now legal (V2-07 closed); US-06 AC-4 ("the tweak did not re-run matching") unaffected — the exception covers admin-triggered re-validation, not tweaks; US-06 remains Should. Residual: CR-16's text doesn't cite its own exception → **F3** |
| D-24: driver origin = home address captured at registration | ✅ CR-03, US-03 title/AC-1/AC-6 aligned; US-03 AC-6 makes missing origin a rejection (no partial record) — consistent with "captured at registration". No other origin definition anywhere (no stale "depot"/"base" text) |
| D-25: vehicle identity editable after publication; parents see current | ✅ CR-03, US-03 AC-8, US-08 AC-1 all carry "current" semantics; no text anywhere says parents see the version at publication time. US-03 AC-8's parent-view check is testable |
| D-26: school/student location = address + coordinates, both required | ✅ CR-01/CR-02, US-01 AC-1/AC-5, US-02 AC-1/AC-2 aligned; IR-07/IR-08 genuinely closed (see 3.2); CR-01 now mentions location (v2's CR↔story drift fixed). Residual wording: **F1**; provenance unstated: **F6** |
| US-01 AC-4 (dismissal-time change → noon plan) ↔ CR-08 ↔ US-07 AC-3 | ✅ Coherent: changed dismissal feeds the reversed noon anchor; no contradiction with US-01 AC-2 (requiredness) |
| US-03 AC-7 (D-20 edit guard) ↔ US-06 AC-3 (reassignment guard) | ✅ Complementary, same "reject with message" pattern, different paths (verified D7-03 claim); no AC overlap |
| US-03 AC-8 ↔ US-08 AC-1 | ✅ Consistent cross-story check (edit → current identity visible); no duplication |
| New ACs vs story traces: US-03 now traces (CR-03, CR-04, D-02) unchanged | ✅ No ID drift; matrix row matches story trace line |

### 3.2 (b) v1 findings IR-01…IR-18 — dispositions re-verified against the CURRENT files

| ID | Claimed disposition | Verified status now |
|---|---|---|
| IR-01 (Crit) | Fixed — per-school feasibility; AC-7 counter-example; AC-8 | ✅ **Genuinely closed.** CR-06 defines feasibility per-school; US-04 AC-1 reworded; AC-7 carries the exact A:20/B:10 / 2×15 dataset; AC-8 degenerate cases present |
| IR-02 (Maj) | → OQ-07 → D-19; remainders → OQ-14 | ✅ **Closed.** D-19 (road distance, no traffic); driver origin → D-24; geodata → OQ-14(c); Gate-B trigger in NFR-08. School-location definition → D-26 (the untracked remainder v2 identified is now closed) |
| IR-03 (Maj) | → OQ-08 → D-21; NFR-01/US-04 AC-4 retargeted | ✅ **Closed.** D-21 exact-at-all-scales; NFR-01 Hours/3h/1h/24h; at-scale evidence + fail-breach → D-22 (v2's V2-06 residual fully closed) |
| IR-04 (Maj) | → OQ-09 → D-20; identity edits → OQ-14(b) | ✅ **Closed.** D-20 + US-03 AC-7 (v2's V2-08 residual closed); identity edits → D-25 + US-03 AC-8 |
| IR-05 (Maj) | Fixed — SM-01 reworded; PO confirmation pending | ✅ **Genuinely closed.** SM-01: non-flagged students, feasible runs, CR-18 runs on report completeness; US-04 AC-1 consistent. PO confirmation still formally outstanding at approval (carried to §4). Residual: D-22 abort class not named in SM-01 → **F7** |
| IR-06 | → A-12 | ✅ Closed. A-12 present, reference environment pinned at Phase 6, expiry Phase 6; NFR-01 meter cites it |
| IR-07 | school-location field def (v2: NOT closed) | ✅ **Closed via D-26 / OQ-14(d).** US-01 AC-5 requiredness test; CR-01 aligned; OQ-14(d) ✅ → D-26 (P9-04 claim verified true) |
| IR-08 | slash ambiguity (v2: NOT closed) | ✅ **Closed via D-26.** CR-02/US-02 now "address and coordinates, both required"; no slash remains. Residual wording: **F1** |
| IR-09 | ✅ US-03 AC-6; duplicates → OQ-13 | ✅ Genuinely closed. AC-6 rejects missing plate/model/color (now also origin) with no partial save; duplicate-plate in OQ-13 |
| IR-10 | ✅ fixed | ✅ Genuinely closed. MoSCoW US-06 rationale cites only "manual/paper handling"; no prohibited re-run reference |
| IR-11 | → OQ-10 | ✅ Closed as tracked open item; listed §6 non-blocking (approval-window gap F4 is *not* OQ-10's coverage — see 3.5) |
| IR-12 | → OQ-11 | ✅ Closed as tracked open item; listed §6 |
| IR-13 | ✅ noted in §6 | ✅ Genuinely closed. §6 lists OQ-06 ("must close before US-06 baseline") |
| IR-14 | → OQ-12 | ✅ Closed as tracked open item; listed §6 |
| IR-15 | ✅ D-18 | ✅ Genuinely closed. CR-10/CR-12 "both channels"; US-05 AC-3/US-07 AC-2/US-08 AC-2 consistent; §1 scope paragraph and roles table both "dashboard and exported file" (grep-verified — V2-09's residual is gone; the only "and/or" strings left in discovery.md are historical citations inside CR-10/D-18 explaining the fix) |
| IR-16 | ✅ D-17 scope note | ✅ Genuinely closed. US-08 note present; split deferred explicitly |
| IR-17 | ✅ AC-8 | ✅ Genuinely closed. US-04 AC-8 defines zero-student/zero-driver/all-flagged behavior |
| IR-18 | → OQ-13 | ✅ Closed as tracked open item; listed §6 |

**Tally: 18/18 closed.** 15 genuinely closed; 3 closed as correctly-tracked open items (OQ-10, OQ-11, OQ-12/13 — tracking verified, no change needed). v2's two open dispositions (IR-07/IR-08) are now closed.

### 3.3 (c) v2 findings V2-01…V2-11 — dispositions re-verified against the CURRENT files

| ID | Claimed disposition | Verified status now |
|---|---|---|
| V2-01 | D-16 annotated superseded | ✅ Closed. D-16 now carries "Superseded by D-21 + NFR-01 v0.6" with corrected numbers; no ≤15 min/>2 h remnant anywhere (grep-verified) |
| V2-02 | CR-07 reworded | ✅ Closed. CR-07: "Distance = real road distance without traffic (D-19); road-network data source and cost: OQ-14(c)" |
| V2-03 | NFR-01 Scale → Hours | ✅ Closed. Scale reads "Hours from admin trigger…" |
| V2-04 | §6 wording | ✅ Closed in requirements.md ("OQ-07 and OQ-09 resolved (remainder (c) of OQ-14…)"). **Drift reappeared in the opposite direction** — discovery OQ-07/OQ-09 rows still "Partially resolved" → **F2** |
| V2-05 | OQ-14(d) + D-26 + US-01 AC-5 + CR-01/02 | ✅ Closed. All present; OQ-14(d) ✅ → D-26 "(closes IR-07/IR-08)" |
| V2-06 | D-22 proposed; later **confirmed** | ✅ Closed. D-22 confirmed 2026-08-15 (D-22 row + §6 changelog); NFR-01 contract-status + fail-breach lines; US-04 AC-5 certificate wording. Residual: SM-01 doesn't name the abort class → **F7** |
| V2-07 | D-23 exception recorded | ✅ Closed. D-23 present, PO-approved. Residual: CR-16 text doesn't cite the exception → **F3** |
| V2-08 | US-03 AC-7 added | ✅ Closed. AC-7 present, testable, aligned with D-20 and US-06 AC-3 |
| V2-09 | "and/or" remnants fixed | ✅ Closed. Scope paragraph + roles table now "dashboard and exported file" (grep-verified; see IR-15 row) |
| V2-10 | US-04 scope note | ✅ Closed. Note present, records the 8-AC deviation. **Convention now broken by US-03** (8 ACs, no note) → **F5** |
| V2-11 | D-21 Gate-B note | ✅ Closed. Note present in D-21: solver choice/licensing re-checked at Gate B (NFR-08 trigger) |

**Tally: 11/11 closed.**

### 3.4 (c) Stale-text sweep (grep-verified, current artifacts only)

| Stale text searched | Result |
|---|---|
| "and/or" in requirements.md / discovery.md | ✅ None live. requirements.md: 0 hits. discovery.md: 2 hits — both historical citations inside CR-10/D-18 explaining the IR-15 fix (acceptable, not remnants) |
| "15 min", "60 s", "5 min", "> 2 h", "straight-line" (old NFR-01 era) | ✅ Only OQ-07's question text ("straight-line or road-network?") — that is the recorded question, now marked resolved; D-16 numbers corrected |
| NFR-01 Scale "Minutes" | ✅ Hours |
| "solver"/"mip" Rule-7 terms | ⚠️ "solver" appears in discovery.md D-21 (Gate-B note) and D-22 (certificate wording) — decision-record rationale exactly as V2-11 prescribed, not requirement text; requirements.md clean (0 hits). Accepted; recorded for transparency |
| Old versions ("v0.4/0.5/0.6/0.7") in current artifacts | ✅ None in requirements.md/discovery.md (only the v0.7→v0.8 changelog reference in §6, which is correct) |
| "Remaining:" clauses vs decisions table | ❌ **F2** — OQ-07/OQ-09 rows claim remainders (driver origin field, vehicle-identity edits) that D-24/D-25 have resolved |

### 3.5 (d) Version/status hygiene

| Check | Result |
|---|---|
| requirements.md header "DRAFT v0.8" = §6 "DRAFT v0.8" (F5-06 drift pattern check) | ✅ Verified (line 5 = line 269) |
| §6 changelog "(v0.7 → v0.8: …)" matches the actual delta (D-22 confirmed, D-23…D-26, US-01/02/03 ACs, OQ-14(a/b/d)) | ✅ Verified line-by-line; matches the delta under review |
| story-review.md pass-9 ends at "DRAFT v0.8 stands. Ready for human approval (Gate 1)" | ✅ Consistent with requirements.md status (claim itself challenged in §1/§5) |
| discovery.md status line vs requirements.md "Pending final human approval (Gate 1)" | ✅ Consistent |
| OQ statuses ↔ decisions table | ⚠️ OQ-01…06, 08, 10…13, 14: all consistent. **OQ-07/OQ-09 rows stale → F2** |
| §6 open-non-blocking list (OQ-06, OQ-10…13, OQ-14(c)) | ✅ Complete and accurate; OQ-14(c) "close before Phase 3" appears in both files |
| ID drift (US/CR/A/D/OQ/NFR/SM) | ✅ None; P9-03 claim verified |

### 3.6 General quality re-checks (fresh passes, not inherited)

- **AC structure & testability:** all 9 stories ≥3 GWT; counts US-01:5, US-02:4, **US-03:8 (F5)**, US-04:8 (note ✓), US-05:4, US-06:4, US-07:4, US-08:7 (D-17 note ✓), US-09:4. Every AC names actor/trigger/observable outcome.
- **Negative/edge coverage:** missing dismissal time, missing location (F1 wording), missing school, capacity 0, missing identity/origin, over-capacity tweak, D-20 edit guard, post-publication identity edit, unpublished visibility (both roles), empty roster, infeasible run w/ full data, per-school imbalance, degenerate registry, unaccepted account request — all present. **Gap: approval-window registry drift → F4.**
- **MoSCoW:** 9/9 litmus rationale, no prohibited-workaround citation (IR-10 verified); MVP = Must set, US-06 Should out; Must-heavy flagged with estimates.
- **Traceability:** 9/9 story trace lines = matrix rows; every CR used or explicitly out-of-story-scope (CR-13/14/15/17 with rationale).
- **Rule 7:** requirements.md clean; discovery.md "solver" limited to decision rationale (see 3.4). "Dashboard"/"exported file"/"registry" are user-visible behavior; "certificate of proven zero gap" is report content, not a design choice.
- **Duplication:** none; US-05 AC-2 ↔ US-08 AC-3 same-rule-different-actor acceptable (F5-07 precedent); US-03 AC-7 vs US-06 AC-3 distinct paths.
- **Hidden assumptions:** D-26 coordinate provenance (F6); D-22 assumes abort still yields a usable documented report (acceptable, CR-18 data model covers it); A-01…A-12 all recorded with owners/expiry.
- **Scope boundaries:** CR-13/14/15/17, D-04/05/08/09, "no notifications/pickup tracking/same-day handling" mutually consistent; nothing in the delta (D-22…D-26) contradicts an out-of-scope decision.

---

## 4. Questions for the product owner

1. **Approval-window validity (F4):** If a capacity or registry change is made *after* a matching run completes but *before* approval, may the pending report still be approved? Recommended: block approval with a message (re-run per D-23, tweak per CR-16, or revert), or forbid such edits while a report is pending — which do you confirm? (Add the corresponding US-05 AC.)
2. **Coordinates provenance (F6):** Who supplies the D-26 coordinates for schools/students — administrator manually, or system geocoding from the address? If geocoding, fold its cost into OQ-14(c) ($30/month question); if manual, confirm validation rules (NFR-09) and data-entry burden are in scope.
3. **CR-16 exception visibility (F3):** Confirm D-23's exception should be stated in CR-16's text itself ("…matching is not re-run, except an admin-triggered capacity re-validation run (D-23)") so the rule and its exception live at the same point.
4. **US-03 size (F5):** Accept an 8-AC US-03 with a recorded deviation scope note (as US-04/US-08), or split AC-7/AC-8 into an edit-lifecycle story?
5. **Error-message granularity (F1):** Confirm the location-requiredness rejections must name the specific missing component (address vs coordinates), or that NFR-09's "clear message" meter is the intended specification.
6. **SM-01 confirmation (carried from v1 Q4 / v2 Q7, still formally outstanding):** Confirm the reworded SM-01 (non-flagged students; CR-18 runs on report completeness) — and accept extending it to name D-22 abort reports (F7).
7. **Carried confirmations:** OQ-06 remains open non-blocking, must close before US-06 baseline (v1 Q13); OQ-10…13 open non-blocking; OQ-14(c) to close before Phase 3 — all as recorded in §6.

---

## 5. Residual risk note (for the human approver)

- **Gate 1 may proceed.** No Critical/Major defect; the delta since v2 is sound; every v1 and v2 disposition is genuinely closed in the current files — including the two v2 flagged as not closed (IR-07/IR-08, via D-26).
- **The pass-9 "zero findings" claim is challenged** (as required by Rule 7): it missed F1–F7. None are blockers; F2/F3/F5/F7 are mechanical, F1/F4/F6 need either a small reword or a recorded PO decision.
- **F4 is the item to watch:** it is the only finding that can produce an *invalid published plan* (capacity or coverage broken at approval time), exactly the invariant CR-06/SM-01 exist to protect. Close it as a decision/AC at baseline, not later.
- Later-gate watch items (unchanged): OQ-14(c) geodata source/cost before Phase 3 (with F6's coordinate-provenance dependencies); D-21 solver choice/licensing at Gate B (V2-11 note); OQ-06 before US-06 implementation; D-22 abort-report content detail at design time.