# Independent Requirements Review v2 — School Driver Platform

> **Project:** Smart transportation platform for school students (daily home ↔ school shuttles)
> **Phase:** 1 — Requirements, **independent review step (governance Rule 7 / §3.6: separation of responsibilities — challenge, do not self-approve)**
> **Review date:** 2026-08-15 (second independent instance, v2)
> **Reviewer:** Independent Requirements Reviewer (fresh context — did NOT see the elicitation session, did NOT see the author's edits after the first independent review; judged the artifacts as they are NOW)
> **Artifacts reviewed (current state):**
> - `docs/requirements.md` — DRAFT v0.6 (US-01…09, ACs, MoSCoW, NFR-01…09, traceability, §6 baseline)
> - `docs/requirements/discovery.md` — CR-01…20, A-01…12, D-01…21, OQ-01…14, SM-01
> - `docs/requirements/story-review.md` — **treated strictly as history** (passes 1–7 incl. the prior delta review D7-01…06; NOT assumed correct — every disposition re-verified against the current files)
> - `docs/requirements/story-review-independent.md` — **treated strictly as history** (v1 findings IR-01…IR-18; every disposition re-verified, not trusted)
> **Method:** Adversarial desk review against the requirements defect taxonomy (ambiguity, incompleteness, inconsistency, infeasibility, unverifiability, duplication, gold-plating, design-in-requirements), plus: hidden-assumption scan, scope check, story-size check, AC testability check (≥3 Given/When/Then per story), edge-case sweep, CR↔story consistency check, Rule 7 implementation-leak scan (keyword grep across all artifacts: api, endpoint, database, schema, json, sql, framework, react, docker, aws, microservice, solver, mip — no hits in requirements text).
> **Scope of this pass:** (a) internal consistency of the D-19/D-20/D-21 decisions and the NFR-01/US-04 changes; (b) genuine closure of IR-01…IR-18 in the current files; (c) stale text contradicting the new decisions; (d) version/status hygiene (header v0.6 = §6 v0.6, OQ statuses vs decisions table).

---

## 1. Verdict

**CONDITIONAL PASS — do NOT baseline until the Minor fixes in §2 are applied (none require a new product-owner decision; they are text/tracking corrections).**

The package is materially cleaner than at the v1 review. Every Critical and Major finding of v1 (IR-01 feasibility criterion, IR-05 SM-01) is **genuinely fixed in the current files** (verified line-by-line, not inherited from the review history), and the three product-owner decisions D-19/D-20/D-21 are **internally consistent with each other, with OQ-07/08/09 statuses, with NFR-01, and with US-04 AC-4** — no new contradictions were introduced by the decision set itself. I found **no Major or Critical defect** and no new blocker.

However, the claim of full closure does not hold: **IR-07 and IR-08 are NOT genuinely closed** — their substance is still present in the artifacts (school "location" undefined + untested; CR-02/US-02 "home location/address" slash) and is **tracked in no open question** (OQ-14 covers driver origin, vehicle-identity edits, and geodata source — not location-field definitions). IR-08 is missing from the disposition list in story-review.md §8 altogether, and IR-07's entry ("school-location field def") carries no disposition marker and no destination OQ. Additionally, the pass-7 delta review's "grep-verified: no remnant of the 15-min goal" claim is **false**: discovery.md D-16 still records "Goal ≤ 15 min, Fail > 2 h", directly contradicting NFR-01 and D-21. Several other stale texts survive (CR-07 still defers to OQ-07; NFR-01 Scale says "Minutes"; §6 says OQ-07/OQ-09 "resolved" where discovery.md correctly says "partially resolved"; two "and/or" remnants from IR-15 in the scope paragraph and roles table). None of these are blockers, all are mechanically fixable, and the core acceptance criteria and metric are now sound — hence CONDITIONAL, not FAIL.

---

## 2. Findings (v2)

| ID | Severity | Defect type | Location | Description | Suggested fix |
|---|---|---|---|---|---|
| V2-01 | Minor | Inconsistency (stale record) | discovery.md D-16 | D-16 still records the **old** NFR-01 thresholds: "Goal ≤ 15 min, Fail > 2 h". NFR-01 is now Goal ≤ 3 h / Stretch ≤ 1 h / Fail > 24 h (D-21, OQ-08). A reader of the decisions table sees a decision that contradicts the NFR it claims to document. The pass-7 check D7-01 claimed "no remnant of the 15-min goal anywhere (grep-verified)" — **that claim is false: D-16 is exactly that remnant.** | Update D-16's numbers to Goal ≤ 3 h / Fail > 24 h, or annotate it "superseded by D-21 + NFR-01 v0.6" (keeping D-16's rationale: runs rare, not on critical path). |
| V2-02 | Minor | Inconsistency (stale reference) | discovery.md CR-07 | CR-07 still says "Distance semantics (straight-line vs road-network) and data source: **OQ-07**" — i.e., it defers to an open question that is now resolved (OQ-07 → D-19). The confirmed requirement text contradicts the decision record. | Reword: "Distance = **real road distance without traffic** (D-19); road-network data source and cost: OQ-14(c)." |
| V2-03 | Minor | Inconsistency (stale unit) | requirements.md NFR-01 (Scale) | Scale still reads "**Minutes** from admin trigger to a complete, reviewable report" while Goal is ≤ 3 **hours**, Stretch ≤ 1 hour, Fail > 24 hours. The unit description was not retargeted with the thresholds (pass-4 changed seconds→minutes; pass-7 moved to hours and missed the Scale field). | Change Scale to "Hours (from admin trigger to a complete, reviewable report)". |
| V2-04 | Minor | Ambiguity / Inconsistency (wording) | requirements.md §6 (Blockers) | §6 says "OQ-07 (distance semantics) and OQ-09 (capacity edits) **resolved**" while discovery.md correctly marks both **Partially resolved** with remainders (driver origin field, vehicle-identity edits after publication, geodata source/cost → OQ-14). A Gate-1 reader of requirements.md alone would believe every aspect is decided. | Say "partially resolved (remainders → OQ-14, close before Phase 3)". |
| V2-05 | Minor | Incompleteness (tracking gap — IR-07/IR-08 not genuinely closed) | story-review.md §8; discovery.md OQ table; requirements.md US-01/CR-01, US-02/CR-02 | (i) **IR-08 has no disposition entry at all** in §8's summary, and its substance is unchanged: CR-02/US-02 still say "home location/address" (slash ambiguity) — what is captured and what feeds the distance model is still the implementer's call, tracked in **no** OQ. (ii) **IR-07 is not closed**: school "location" (US-01 AC-1/AC-2, title) is still undefined (address? coordinates?), has no requiredness AC (AC-2 tests only missing dismissal time), and CR-01 does not even mention the location field that US-01 registers (CR↔story drift). §8's entry "school-location field def" carries no marker (✅/→) and no destination OQ. OQ-14 covers driver origin, vehicle-identity edits, geodata source — **not** location-field definitions. | Fold both into OQ-14 (add item (d): define school "location" and student "home location/address" — address vs coordinates, requiredness) or record a PO decision; add a school-location requiredness AC to US-01 mirroring AC-2; align CR-01 with US-01 (mention location). |
| V2-06 | Minor | Unverifiability (residual of IR-03, at-scale meter) | requirements.md US-04 AC-4; NFR-01 | D-21 asserts **exact optimality at every scale**, but AC-4's acceptance meter ("small-instance exhaustive verification") applies only to small instances — there is no stated meter that verifies optimality on the 500/50/10 reference dataset (exhaustive search is impossible there; the prior "15-min" doubt was replaced by a guarantee assertion, not by a verification method). Separately, **behavior on a Fail-breach is undefined**: if a run exceeds 24 h (explicitly possible for hard instances under D-21), no AC, CR-18, or NFR clause says what the user sees, whether the run is abortable, or whether the exact-optimality guarantee admits a documented non-termination outcome. | Record the at-scale verification evidence (e.g., the report must carry a solver **optimality certificate / proven zero-gap** for the produced plan; small-instance exhaustive tests validate the solver's correctness) and define the Fail-breach behavior (abort with a documented report, publication blocked, admin may re-run/adjust) — extend CR-18 semantics or add a decision. Also state that NFR-01 "Goal"/"Stretch" are targets and "Fail" is the contract (needed for Gate 7 acceptance). |
| V2-07 | Minor | Inconsistency (unrecorded exception) | discovery.md D-20 vs CR-16 | D-20 says re-validation after a rejected capacity edit may be "**re-run matching** or reassignment (US-06 flow)". CR-16 states mid-year "**matching is not re-run**". D-20 therefore offers an option CR-16 prohibits, without recording this as an exception. | PO decision: either confirm a capacity-driven re-validation run is an explicit exception to CR-16 (record it), or restrict D-20's revalidation wording to reassignment (US-06) + the next annual run. |
| V2-08 | Minor | Incompleteness / Unverifiability | requirements.md US-03; discovery.md D-20 | D-20's decided behavior — "capacity may not be reduced below current assignment count while an approved/published plan exists → rejected with a message" — is **tested by no AC anywhere**. US-03 covers only creation (AC-1…6); the edit path (the very thing IR-04 was about) has no acceptance criterion. The decided rule exists only as a decision record. | Add a US-03 edit AC: "Given a driver whose capacity edit would drop below their current assignment count on an approved/published plan, when the administrator saves it, then the edit is rejected with a capacity message and the existing capacity is unchanged (D-20)." (Or explicitly list this case under NFR-09's error-path meter.) |
| V2-09 | Note | Inconsistency (stale "and/or") | requirements.md §1 scope paragraph ("…via dashboard and/or exported file"); discovery.md §1 roles table (Driver row) | The channel ambiguity IR-15/D-18 was meant to kill ("and/or") survives in two narrative locations: CR-10/CR-12 were standardized to "both channels", but the scope paragraph and roles table still say "and/or". | Replace with "both" ("dashboard and exported file") in both locations. |
| V2-10 | Note | Oversize check | requirements.md US-04 (8 ACs) | Us-04 now carries **8 ACs** (AC-1…8 after the IR-01 per-school wording, AC-7 counter-example, AC-8 degenerate cases). The project's own stated range (and v1 review) is 3–7; 8 exceeds it. It remains one capability (run matching) with its failure/edge paths — acceptable, but the deviation should be recorded rather than silent, as D-17 did for US-08. | Add a one-line scope note on US-04 (as D-17 did for US-08) or split AC-7/AC-8 into the US-09 failure-flow story; either way record the deviation. |
| V2-11 | Note | Gold-plating/feasibility & budget interaction | NFR-08; discovery.md D-21 | D-21 changed the algorithmic scope (exact optimum at 500/50/10 — NP-hard) relative to pass-4's "US-04 untouched" budget reasoning. No text ties D-21's implications to the budget ceilings: commercial exact solvers can cost well over $30/month licensing, and free solvers carry runtime risk against the new hours-long window. Gate B's re-check trigger formally covers any scope change, so this is not a defect — but it should be made explicit. | Add one line to NFR-08 (or OQ-14): "D-21 exact-optimality solver choice (free vs licensed) and compute implications are re-checked at Gate B before Phase 3 spend." |

**Severity counts: 0 Critical, 0 Major, 8 Minor (V2-01…V2-08), 3 Notes (V2-09…V2-11).**

---

## 3. Verification checklist

### 3.1 (a) The D-19/D-20/D-21 decision set and NFR-01/US-04 changes — internal consistency

| Check | Result |
|---|---|
| D-19 (road distance, no traffic) recorded; matches OQ-07 resolution wording; consistent with CR-07 objective (once V2-02 fixed) and US-04 AC-5 ("total driving distance") | ✅ Consistent (V2-02 is a stale reference, not a substantive conflict) |
| D-20 (reject capacity reduction below assigned count on approved/published plans) recorded; complements US-06 AC-3 (over-capacity reassignment rejected) — same "reject with message" pattern, different guard (edit path vs reassignment path) | ✅ Complementary — D7-03 claim verified true |
| D-20 vs CR-16 "matching is not re-run" | ⚠️ Tension — V2-07 (needs PO word on scope of "re-run matching" as revalidation) |
| D-21 (exact optimum at every scale, hours acceptable) recorded; matches OQ-08 resolution; NFR-01 retargeted Goal ≤ 3 h / Stretch ≤ 1 h / Fail > 24 h exactly as OQ-08 and D-21 state | ✅ Consistent |
| NFR-01 rationale cites D-16 + D-21 and explains the overnight-run expectation; Fail exists to catch pathology | ✅ Coherent, though D-16's recorded numbers are stale (V2-01) and Goal-vs-contract status should be explicit (V2-06) |
| US-04 AC-4 extended with the scale guarantee; still coherent with AC-5 (report shows total distance) and orthogonal to AC-6/7/8 (failure/degenerate paths) | ✅ No conflict — D7-02 verified true |
| US-04 AC-1/AC-6/AC-7 per-school feasibility (IR-01 fix) — wording correct, counter-example dataset (A:20, B:10; two drivers × 15) present, degenerate AC-8 present | ✅ Verified line-by-line |
| No new contradiction introduced by the decision set into SM-01, CR-18/19, US-05, US-09 | ✅ None found |

### 3.2 (b) IR-01…IR-18 dispositions — re-verified against the CURRENT files (not trusted from history)

| ID | Claimed disposition | Verified status in current files |
|---|---|---|
| IR-01 (Critical) | Fixed — per-school feasibility; AC-7 counter-example; AC-8 | ✅ **Genuinely closed.** CR-06 defines feasibility per-school; US-04 AC-1 reworded with the exact IR-01 counter-example in AC-7; AC-8 handles degenerate inputs |
| IR-02 (Major) | → OQ-07 → D-19, remainders → OQ-14 | ✅ **Closed as a decision, with one untracked remainder.** Distance semantics fixed (D-19); driver origin → OQ-14(a); geodata source/cost → OQ-14(c); NFR-08 Gate-B trigger noted. **School-location field definition is not tracked anywhere** (→ folded into V2-05) |
| IR-03 (Major) | → OQ-08 → D-21; NFR-01/US-04 AC-4 retargeted | ✅ **Closed as a decision.** Residual: at-scale verification meter and Fail-breach behavior still unstated (V2-06 — Minor, not a blocker) |
| IR-04 (Major) | → OQ-09 → D-20; vehicle-identity edits → OQ-14(b) | ✅ **Closed as a decision.** Residual: D-20's rejection rule has no testable AC (V2-08), and D-20's "re-run matching" option rubs against CR-16 (V2-07) |
| IR-05 (Major) | Fixed — SM-01 reworded; PO confirmation pending | ✅ **Genuinely closed** (SM-01 now: non-flagged students, CR-18 runs judged on report completeness; US-04 AC-1 consistent). PO confirmation at approval still outstanding (carried to §4 Q7) |
| IR-06 (Minor) | → A-12 | ✅ **Genuinely closed.** A-12 present, reference environment pinned at Phase 6 (QA), expires Phase 6 |
| IR-07 (Minor) | "school-location field def" (no marker, no destination) | ❌ **NOT closed.** School "location" still undefined (US-01 AC-1), no requiredness AC (US-01 AC-2 still tests only dismissal time), CR-01 omits location entirely; tracked in no OQ (V2-05) |
| IR-08 (Minor) | *(absent from §8 disposition list)* | ❌ **NOT closed.** CR-02/US-02 still "home location/address"; slash ambiguity unresolved; tracked in no OQ (V2-05) |
| IR-09 (Minor) | ✅ US-03 AC-6; duplicates → OQ-13 | ✅ **Genuinely closed.** AC-6 rejects missing plate/model/color with no partial save; duplicate-plate definition in OQ-13 |
| IR-10 (Minor) | ✅ fixed | ✅ **Genuinely closed.** MoSCoW US-06 rationale now cites only "manual/paper handling"; no prohibited re-run reference |
| IR-11 (Minor) | → OQ-10 | ✅ **Closed as tracked open item.** OQ-10 open-non-blocking, listed in §6 |
| IR-12 (Minor) | → OQ-11 | ✅ **Closed as tracked open item.** OQ-11 open-non-blocking, listed in §6 |
| IR-13 (Minor) | ✅ noted in §6 | ✅ **Genuinely closed.** §6 now lists OQ-06 explicitly ("must close before US-06 baseline") |
| IR-14 (Minor) | → OQ-12 | ✅ **Closed as tracked open item.** OQ-12 open-non-blocking, listed in §6 |
| IR-15 (Minor) | ✅ D-18 | ✅ **Genuinely closed at the CR/story level** (CR-10/CR-12 "both channels"; US-05 AC-3/US-07 AC-2 consistent). Narrative remnants remain: §1 scope paragraph + Discovery roles table still "and/or" (V2-09) |
| IR-16 (Minor) | ✅ D-17 scope note | ✅ **Genuinely closed.** US-08 carries the D-17 scope note; split deferred explicitly |
| IR-17 (Minor) | ✅ AC-8 | ✅ **Genuinely closed.** US-04 AC-8 covers zero students/drivers and all-flagged with defined behavior |
| IR-18 (Minor) | → OQ-13 | ✅ **Closed as tracked open item.** OQ-13 open-non-blocking, listed in §6 |

**Tally: 14 of 18 genuinely closed as claimed; 2 closed as tracked open items whose tracking is correct (no change needed); IR-07 and IR-08 NOT closed (V2-05).** Also: pass-7's D7-01 "grep-verified no remnant" claim is inaccurate (V2-01); D7-02/03/06 claims verified true; D7-04 mostly true (see V2-04); D7-05 (Gate B surfacing) verified present.

### 3.3 (c) Stale text contradicting the new decisions

| Stale text | Contradicts | Finding |
|---|---|---|
| discovery.md D-16: "Goal ≤ 15 min, Fail > 2 h" | NFR-01 (3 h / 24 h) and D-21 | V2-01 |
| discovery.md CR-07: "…data source: OQ-07" | OQ-07 resolution (→D-19, OQ-14) | V2-02 |
| requirements.md NFR-01 Scale: "Minutes" | Hour-level thresholds | V2-03 |
| requirements.md §6: "OQ-07…resolved; OQ-09…resolved" | discovery.md "Partially resolved" + OQ-14 remainders | V2-04 |
| requirements.md §1 + discovery.md §1: "dashboard and/or exported file" | D-18 / CR-10 / CR-12 ("both channels") | V2-09 |
| Grep sweep for other remnants ("60 s", "5 min", "> 2 h", "straight-line") outside history files | — | No other hits; only D-16 (V2-01) and CR-07 (V2-02) |

### 3.4 (d) Version/status hygiene

| Check | Result |
|---|---|
| requirements.md header "DRAFT v0.6" = §6 "DRAFT v0.6" (F5-06 drift pattern not repeated) | ✅ Verified (header line 5; §6 line 262) |
| §6 changelog "(v0.5 → v0.6: OQ-07 semantic + OQ-08 + OQ-09 resolved → D-19/20/21; NFR-01 retargeted; US-04 AC-4 scale guarantee; IR dispositions in story-review.md §8)" matches actual changes | ✅ Verified (except "OQ-07…resolved" wording, V2-04) |
| story-review.md pass 7 "DRAFT v0.6 stands" consistent with requirements.md | ✅ Verified |
| discovery.md status line ("Discovery complete; pending human review…") consistent with requirements.md "pending final human approval (Gate 1)" | ✅ Verified |
| OQ statuses vs decisions table: OQ-01→D-12/CR-18/19 ✅; OQ-02→NFR-08 ✅; OQ-03→D-13/NFR-07 ✅; OQ-04→D-14/CR-20 ✅; OQ-05→D-15 ✅; OQ-06 open ✅; OQ-07 partially resolved→D-19+OQ-14 ✅; OQ-08 resolved→D-21+NFR-01 ✅; OQ-09 partially resolved→D-20+OQ-14(b) ✅; OQ-10…13 open ✅; OQ-14 open, "close before Phase 3" ✅ (matches §6) | ✅ All 14 consistent |
| OQ-14 text matches §6's summary of it (driver origin, vehicle-identity edits, geodata source/cost — all present in both) | ✅ Verified |

### 3.5 General quality re-checks (repeat of v1 passes, not inherited)

- **AC structure & testability:** all 9 stories ≥3 Given/When/Then (US-01: 4, US-02: 4, US-03: 6, US-04: 8, US-05: 4, US-06: 4, US-07: 4, US-08: 7, US-09: 4); all ACs name actor/trigger/observable outcome; every story ≥3 ✅ (US-04 size: V2-10).
- **Negative/edge coverage:** missing dismissal time, missing address, missing school, capacity 0/missing, missing vehicle identity, over-capacity tweak, unpublished visibility, empty roster, infeasible run with full failure data, per-school imbalance counter-example, degenerate registry, unaccepted account request ✅ (D-20 rejection not covered by any AC — V2-08).
- **MoSCoW:** 9/9 prioritized with litmus rationale; proposed MVP set = exactly the Must set (US-01…05, 07…09; US-06 Should out) ✅; Must-heavy allocation explicitly flagged with t-shirt estimates ✅.
- **Traceability:** every story traces to ≥1 CR/D; every CR used by ≥1 story or explicitly out-of-story-scope (CR-13/14/15/17 with rationale); matrix matches story trace lines; no ID drift after v0.6 ✅ (US-04's AC-level references to CR-18/19 are covered by US-09 — acceptable).
- **Rule 7 implementation-leak scan:** keyword grep (api, endpoint, database, schema, json, sql, framework, react, docker, aws, microservice, solver, mip) over all four artifacts — no design/implementation language in requirements; "dashboard"/"exported file"/"registry" are user-visible behavior; NFR-07 RTL is a rendering requirement; NFR-08 "hosting" is a budget line ✅.
- **Duplication:** no duplicate stories; US-05 AC-2 ↔ US-08 AC-3 cross-role same-rule acceptable; US-04 AC-4/AC-5 distinct (optimality vs display) ✅.
- **Hidden assumptions:** D-19 assumes a road-network data source exists (→OQ-14(c) ✅); D-21 assumes an exact solver is affordable/feasible in budget (V2-11); A-01…A-12 recorded with owners/expiry ✅.
- **Gold-plating:** none found; NFR-05 "Wish 99.9%" correctly labeled ✅.
- **Scope boundaries:** CR-13/14/15/17, D-04/05/08/09, "no same-day handling", "no notifications" mutually consistent; no story contradicts an out-of-scope decision ✅.

---

## 4. Questions for the product owner

1. **Close IR-07/IR-08 (V2-05):** Should OQ-14 be extended with "(d) field definitions: school 'location' and student 'home location/address' — address, coordinates, or both; which are required?" And should school location be mandatory at registration (add the US-01 requiredness AC mirroring AC-2)? (Also: bring CR-01 in line with US-01 — it currently omits location.)
2. **NFR-01 Fail-breach behavior (V2-06):** If a matching run exceeds 24 h (possible under D-21's exactness commitment), what is the defined outcome — abort with a documented report, publication blocked, admin may re-run or adjust? Should CR-18 semantics (no partial plan) extend to timeouts?
3. **At-scale optimality evidence (V2-06):** Is a solver **optimality certificate / proven zero-gap** recorded in the report acceptable as the at-scale verification meter, with small-instance exhaustive search as the solver-correctness validation? (AC-4 currently names only the small-instance meter.)
4. **NFR-01 contract status (V2-06):** Confirm "Goal ≤ 3 h" and "Stretch ≤ 1 h" are targets and only "Fail > 24 h" is contractual — given D-21 explicitly blesses overnight runs — so Gate 7 acceptance is unambiguous.
5. **D-20 vs CR-16 (V2-07):** Is "re-run matching" as a D-20 re-validation path an intentional exception to CR-16's "matching is not re-run" for mid-year changes, or should D-20 name reassignment (US-06) plus the next annual run only?
6. **D-20 acceptance coverage (V2-08):** Confirm adding a US-03 edit-AC for the D-20 rejection (capacity reduction below assigned count on an approved/published plan) — or is NFR-09's error-path suite intended to carry it (then reference it explicitly)?
7. **SM-01 confirmation (carried from v1 Q4, still outstanding):** Confirm the reworded SM-01 ("100% of registered **non-flagged** students… CR-18 runs judged on report completeness") at approval.
8. **Budget interaction (V2-11):** Confirm the Gate B re-check will explicitly cover D-21's solver choice/licensing and compute implications (commercial exact solvers can exceed $30/month) alongside OQ-14(c) geodata cost, before Phase 3 spend.
9. **US-04 size (V2-10):** Accept US-04's 8 ACs as a single capability with a recorded scope note (as D-17 did for US-08), or move AC-7/AC-8 into the US-09 failure flow?

---

## 5. Residual risk note (for the human approver)

- **Nothing in v2 blocks Gate 1**: the v1 Critical/Major items are genuinely resolved and the three new decisions are internally consistent. The conditions attached to this PASS are all Minor text/tracking corrections (V2-01…V2-05) that can be applied in the same revision cycle.
- The two items that keep the package from being a clean PASS — IR-07/IR-08 untracked and D-16/CR-07/NFR-01-Scale stale text — are exactly the class of "claimed closed but not actually closed" defects the independent-review step exists to catch; closing them requires no new decision, only OQ-14 tracking and text edits.
- Watch items for later gates (not blockers): D-21's at-scale verification method and Fail-breach behavior (V2-06) should be settled by design/acceptance time; D-20/CR-16 scope (V2-07) before US-06 implementation; OQ-14 must close before Phase 3 as scheduled, including the new location-field item if Q1 is accepted.