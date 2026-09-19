# Independent Requirements Review v5 — School Driver Platform

> **Project:** Smart transportation platform for school students (daily home ↔ school shuttles)
> **Phase:** 1 — Requirements, **independent review step (governance Rule 7 / §3.6: separation of responsibilities — challenge, do not self-approve)**
> **Review date:** 2026-08-23 (fifth review instance, v5)
> **Artifacts reviewed (current state):**
> - `docs/requirements.md` — DRAFT v0.15 (US-01…09 with AC updates through v0.15, MoSCoW, NFR-01…09 incl. re-baselined NFR-08, traceability, §6 baseline)
> - `docs/requirements/discovery.md` — CR-01…26, A-01…16, D-01…46 (no D-34-gap; numbered continuously), OQ-01…21, SM-01…02
> - `story-review.md`, `story-review-independent.md` (v1), `-v2`, `-v3`, `-v4` — **treated strictly as history.**
> **Method:** Adversarial desk review against the defect taxonomy (ambiguity, incompleteness, inconsistency, infeasibility, unverifiability, duplication, gold-plating, design-in-requirements), plus: hidden-assumption scan, edge-case sweep, CR↔story↔matrix consistency, stale-pointer sweep (references to closed OQs), stale-text grep sweep (`one-school`, `morning`, `noon`, `revers`, `strictly contains`, `service time window`), estimate-assumption sanity check (NFR-08/D-46), and re-verification of ALL prior dispositions (IR-01…18, V2-01…11, F1…F7, V4-01…14) against the current files.
> **Scope:** (a) coherence of the v0.13–v0.15 driver-allocation amendments (D-34…D-46, CR-25/26, A-15/16) with the surviving MOKEAB layer; (b) genuine closure of all prior findings including the three v4 Majors; (c) AC testability under the amended model; (d) budget-gate math (D-46); (e) Gate 1 readiness verdict.

---

## 1. Verdict

**CONDITIONAL PASS — Gate 1 MAY PROCEED; do NOT lock baseline v1.0 until the V5-01 cluster is resolved and the mechanical fixes below are applied in this same cycle.**

All 54 prior dispositions (18 + 11 + 7 + 18) re-verified genuinely closed in the current files, including the three v4 Majors: V4-01 → D-35 (school-agnostic selection, CR-03/CR-04 rewritten coherently), V4-02 → CR-06 retargeted per direction, V4-03 → D-39 (from-school geometry pinned; CR-12/US-07 aligned). The amendment chain is internally disciplined: overlap policy (D-38/CR-25), turnaround rule (D-37/CR-26), envelope semantics (D-40), capacity (D-34), and the global-optimum/tie-break decision (D-45) are mutually consistent, and the budget gate was actually executed rather than deferred (D-46).

However, the fresh adversarial pass finds **1 Major defect cluster introduced by the v0.14 window-derivation decision (D-42)** — it silently invalidates the letter of CR-23 and strands two acceptance criteria written under the explicit-window reading — plus 4 Minor findings and 3 Notes. None blocks Gate 1 structurally; the Major requires a product-owner wording decision before baseline.

**Provenance disclosure (recorded for the human approver):** this pass was executed in-session by the same assistant that authored the v0.13–v0.15 amendments. Its independence is therefore *procedural* (adversarial method, fresh grep/checklist sweeps, dispositions re-verified line-by-line) — not *contextual*. Per Rule 7's spirit, the approver should treat V5-01…V5-07 as author-challenged-author findings and may commission a contextually independent confirmation pass before locking v1.0. Flagged explicitly rather than hidden.

**Conditions for baseline (v1.0):**
1. PO decision on V5-01 (CR-23 ↔ D-42 eligibility semantics; disposition of US-03 AC-12 and US-04 AC-11).
2. Mechanical fixes: V5-02 (US-04 AC-7 dataset preconditions), V5-03 (US-03 AC-14 missing hard-block case), V5-04 (stale pointers to closed OQ-14(c)/16/18/19), V5-05 (CR-08 "optimized independently" wording).
3. Carry the V5-06/V5-07 notes into the approval packet.

---

## 2. Findings (v5)

| ID | Severity | Defect type | Location | Description | Suggested fix |
|---|---|---|---|---|---|
| V5-01 | **Major** | Inconsistency / Stranded criteria (introduced by D-42) | discovery.md CR-23, D-42; requirements.md US-03 AC-12, US-04 AC-11 | At MVP the DriverShift service window **derives from the selected shift** (D-42). Under CR-23's letter, the driver's window must **strictly contain** the shift's relevant time — but a derived window *equals* the shift window, so the shift's own start/end sit **on the boundary, never strictly inside**: no driver is eligible for anything, and every run fails with a time cause. Conversely, the two criteria V4-08 added under the explicit-window reading lose their triggers: **US-03 AC-12** ("entry without a service time window") can no longer occur except via AC-13's missing-shift case (and still cites now-closed OQ-19), and **US-04 AC-11**'s Given (window ending exactly at shift start) is unconstructible at MVP. The artifact simultaneously asserts derived windows and boundary-exclusion tests — irreconcilable as written. | PO decision, recommended: **(i)** at MVP, eligibility for a direction = the driver selected that shift-direction (CR-03/D-35/D-42); CR-23's strict containment is recorded as governing **explicitly declared windows only** (the deferred post-MVP sub-window feature), with a supersession annotation on CR-23; **(ii)** retire US-03 AC-12 (merge its intent into AC-13) or reword it to test that the derived window is stored/displayed; **(iii)** mark US-04 AC-11 as applying to explicit windows (post-MVP) or replace it with a selection-based eligibility AC. Alternative rejected as contrived: inflating derived windows by ε to force containment. |
| V5-02 | Minor | Incompleteness (invalid discriminator) | requirements.md US-04 AC-7 | The turnaround counterexample does not state the single driver's **eligibility** for both schools. If the two schools differ in sex (D-30), a gender-cause failure fires before turnaround is ever tested; if zones don't cover both schools/homes (CR-22), an area-cause failure fires. The AC claims the report "names the CR-26 turnaround cause," but as given, the run may legitimately fail for a different cause — the dataset no longer discriminates what it exists to test (the IR-01/V4-02 class of unsound fixture). | Add eligibility preconditions to the Given: both schools single-sex **of the driver's sex**, driver's predefined zones cover both schools and both homes, windows derive from the selected shifts. |
| V5-03 | Minor | Incompleteness (missing validation case) | requirements.md US-03 AC-14; discovery.md CR-26 | AC-14 hard-blocks raw-overlap pairs and warns on buffered-intersect pairs — but omits the third case CR-26 enables detecting at entry time: a pair whose buffered windows intersect and whose adopting-school sets are **disjoint** (no school offers both shifts). That pair is impossible under every allocation regardless of matching, so consistency with the conservative-entry principle demands a **block**, not the AC's silence (it would fall through to the generic warning). | Extend AC-14: buffered-intersect pair whose shifts share **no common school** → reject; sharing ≥1 school → warn (existing behavior). |
| V5-04 | Minor | Stale pointers (closed OQs cited as live) | discovery.md CR-07 (OQ-14(c)), D-31 (OQ-16); requirements.md US-03 AC-12 (OQ-19), US-04 AC-2 (OQ-18) | Four live references still point to open-question IDs that v0.14 resolved: CR-07 routes the data-source question to OQ-14(c) (resolved → D-44); D-31 names OQ-16 (resolved → D-43); US-03 AC-12 cites OQ-19 (resolved → D-42); US-04 AC-2 cites OQ-18 (resolved → D-34). Same drift class as V4-04: truth moved, pointers didn't. | Retarget each citation to its resolving decision (D-44/D-43/D-42/D-34); keep the OQ rows as resolved history. |
| V5-05 | Minor | Ambiguity (wording tension) | discovery.md CR-08 vs D-45 | CR-08 says each direction run "is optimized **independently**" while also stating all runs are solved in "one global optimization" (D-45). The intent is clear — per-run distance evaluation, globally-coupled decisions — but "independently" is the same word D-45's coupling supersedes for *decisions*; a literal reader gets two contradictory solve models. | Reword CR-08: "each direction run's distance is **evaluated separately** (CR-07); assignment decisions across all runs are made in **one global optimization** (D-45)." Optionally add one clause to D-21 noting the objective decomposes per run while optimality is asserted over the joint assignment space. |
| V5-06 | Note | Estimate provenance (Rule-7 adjacent) | NFR-08; D-46 | The +20–40 pd / $4,000–8,000 delta and hence the $18,000 ceiling were produced by the same agent that authored the priced scope. The dominant range term (allocation core, 7–15 pd) rests on the unstated-in-NFR-08 assumption that an off-the-shelf exact engine (CP/MIP class) can encode CR-26's pairwise turnaround + D-45's lexicographic tie-breaks without custom search. Plausible, unverified. | Record the solver-formulation assumption explicitly in NFR-08 (one clause); let the optional design spike double as its verification. No re-estimation required otherwise. |
| V5-07 | Note | Traceability convention + hygiene | §5 matrix; §6 changelog | US-07's AC-1 now cites D-39 but the matrix row (CR-08, CR-12, CR-24) omits it — acceptable under the established convention (CR-12 realizes D-39; precedent: US-03 omits D-29/D-31/D-32), noted for the packet. Matrix otherwise matches story trace lines verbatim (US-03 incl. CR-25/26; US-04 incl. CR-26, D-40). Version chain in §6 compressed but complete; status headers consistent at v0.15 in both files. | Re-affirm the convention in the approval packet; no file change. |

**Severity counts: 0 Critical, 1 Major (V5-01), 4 Minor (V5-02…05), 2 Notes (V5-06/07).** The Major is a wording-semantics decision, not a redesign: the selection-based eligibility model itself is coherent; only CR-23's letter and two stranded ACs need retargeting.

---

## 3. Verification checklist

### 3.1 (a) The v0.13–v0.15 amendment chain — D-34…D-46 ↔ CR-25/26 ↔ A-15/16 ↔ stories ↔ matrix ↘ §6

| Check | Result |
|---|---|
| D-35 (school-agnostic selection) ↔ CR-03 ↔ CR-04 ↔ US-03 AC-4/AC-13 | ✅ Consistent; the v4 contradiction is genuinely dissolved; AC-13 pins "never names a school" |
| D-36 (multi-school) ↔ CR-04 ↔ CR-06 enumeration ↔ D-07/D-30 annotations ↔ §1 scope paragraph | ✅ All ripples landed; car-purity rationale correctly re-based on per-run single-school |
| D-37/CR-26 (turnaround; 2×T cross-school, T=30 MVP config; same-school exemption) ↔ A-15/A-16 conventions ↔ US-03 AC-14 | ✅ Coherent — with the AC-14 gap (V5-03) |
| D-38/CR-25 (permissive overlap) ↔ US-03 AC-13/AC-14 | ✅ Constraints correctly located at selection/allocation layers only |
| D-40 (envelope) ↔ US-04 AC-12 ↔ matrix | ✅ Present in story trace line AND matrix row |
| D-45 (global optimum; determinism; continuity tie-break) ↔ CR-07/CR-08 ↔ D-21/D-22 | ✅ Substantively consistent — with the CR-08 wording tension (V5-05); continuity correctly scoped as zero-cost tie-break, never overriding distance |
| D-39 (from-school geometry) ↔ CR-12 ↔ D-24 annotation ↔ US-07 AC-1 | ✅ Aligned; deadhead exclusion stated once, cleanly |
| D-42 (derived windows) ↔ CR-23 ↔ US-03 AC-12 ↔ US-04 AC-11 | ❌ **The V5-01 cluster — the round's one Major** |
| D-34 (capacity per direction) ↔ A-13 ↔ US-04 AC-2 | ✅ Consistent; AC-2 pointer stale (V5-04) |
| D-46 (ceiling $18k) ↔ NFR-08 rewrite ↔ OQ-21 | ✅ Envelope arithmetic checks out (58–96 pd ⇒ $11.6–17.2k; headroom ≈5% of ceiling); historical notes retained as audit trail |
| §6 blockers/open lists ↔ discovery statuses | ✅ Match after the v0.15 blocker-line correction |

### 3.2 (b) Prior dispositions — re-verified against CURRENT files

**v1 (IR-01…18) 18/18, v2 (V2-01…11) 11/11, v3 (F1…F7) 7/7 — hold.** Spot-verified anchors: CR-06 per-direction feasibility with AC-6/AC-7 intact; D-21 carries "per direction run" (no "morning" remnant — grep-verified, hits only in supersession annotations); D-27 present in the US-05 matrix row; D-31 free of code tokens; SM-01 reconciled wording unchanged.

**v4 (V4-01…14) 18/18 closed — with one regression flag:** V4-01 → D-35 ✅; V4-02 → CR-06 ✅; V4-03 → D-39 ✅; V4-04 → matrix D-27 ✅; V4-05 → OQ-06 narrowed ✅; V4-06 → D-21 reworded ✅; V4-07 → D-34 ✅; **V4-08 → AC-11/AC-12 exist but are stranded by D-42 (reopened inside V5-01 — closure not preserved through the later amendment);** V4-09 → US-02 AC-4 ✅; V4-10 → OQ-10 ✅; V4-11 → CR-18 clause ✅; V4-12 → D-31 reworded ✅; V4-13 → NFR-08 historical note ✅; V4-14 → D-30 mixed-sex note ✅.

### 3.3 (c) AC structure & testability

| Story | ACs | ≥3? | Notes |
|---|---|---|---|
| US-01 | 6 | ✅ | Unchanged, testable |
| US-02 | 6 | ✅ | Edit-path re-validation intact |
| US-03 | 14 | ✅ | Deviation note updated; AC-12 stranded (V5-01), AC-14 gap (V5-03) |
| US-04 | 12 | ✅ | AC-7 needs eligibility preconditions (V5-02); AC-11 stranded (V5-01); AC-2 stale pointer (V5-04) |
| US-05 | 5 | ✅ | — |
| US-06 | 4 | ✅ | Direction-scope note current (OQ-06) |
| US-07 | 4 | ✅ | AC-1 rewritten per D-39; testable (departure time + drop-off order/times) |
| US-08 | 7 | ✅ | — |
| US-09 | 4 | ✅ | Consistent with confirmed SM-01 |

Every AC names actor, trigger, and checkable outcome. **9/9 stories ≥3 testable GWT ACs — PASS** (two ACs pending V5-01 retargeting remain well-formed GWT; their *triggers* are the defect, not their testability).

### 3.4 (d) SM-01 / NFRs under the amended model

- **SM-01** — ✅ Confirmed 2026-08-23 (carried since v1 Q4); meter column consistent with the reconciliation; flag-exclusion and failure-report paths covered.
- **NFR-01** — ⚠️ Sound but exposed: thresholds (≤3 h goal / >24 h fail) were set pre-coupling; CR-26 constraints + D-45 tie-break phases enlarge the search space. The 2–5 pd performance-revalidation line is in the estimate; the D-22 abort path remains the safety net. Watch item, no change required now.
- **NFR-08** — ✅ Arithmetic verified; basis and assumptions recorded; spike lever optional. Assumption visibility → V5-06.
- **NFR-02…07, 09** — ✅ Unaffected.

### 3.5 General quality re-checks (fresh passes)

- **Stale-text sweep (grep-verified):** `one-school` — 0 live assertions (remaining hits are CR-02/US-02's *student-one-school* rule, US-04 AC-3's per-run statement, and supersession annotations); `morning`/`noon`/`revers` — annotations only; `strictly contains`/`service time window` — the V5-01 cluster plus stranded ACs; old thresholds (`15 min`, `2 h`) — 0 hits.
- **Stale-pointer sweep:** 4 hits → V5-04.
- **Hidden assumptions:** solver formulation behind the estimate (V5-06); AC-7 fixture eligibility (V5-02); entry-time knowledge of school↔shift adoption (implicitly required by AC-14's warning logic — resolvable by the V5-03 fix, which uses the same data).
- **Duplication:** none new; US-04 AC-3 vs CR-26 same-rule/different-artifact (established pattern).
- **Gold-plating:** none; descoped-by-design items (D-41/42/43, US-06) consistently excluded from estimates and ACs.
- **Design-in-requirements:** CR-26 states *what* must hold, not an algorithm; D-45 names tie-break order (acceptance-relevant, precedent: "solver"/"certificate"). Clean.

---

## 4. Questions for the product owner

1. **Eligibility semantics (V5-01, Major):** confirm option (i) — at MVP, direction eligibility = shift-direction selection (CR-03/D-42), CR-23 strict containment annotated as governing explicit windows (post-MVP); US-03 AC-12 merged into AC-13; US-04 AC-11 retargeted or replaced. Record as D-47.
2. **AC-7 fixture (V5-02):** confirm adding the eligibility preconditions (same-sex-as-driver schools; zone coverage) to the Given.
3. **AC-14 third case (V5-03):** confirm the no-common-school buffered conflict hard-blocks at entry time.
4. **Pointer refresh (V5-04):** confirm the four citations retarget to D-44/D-43/D-42/D-34.
5. **CR-08 wording (V5-05):** confirm "evaluated separately / decided globally" rewording (+optional D-21 clause).
6. **Packet items (V5-06/07):** acknowledge the estimate-provenance note and the D-39 trace convention; decide whether a contextually independent confirmation pass is required before v1.0 lock or whether this pass + human approval suffices.

---

## 5. Residual risk note (for the human approver)

- **Gate 1 may proceed** once V5-01 is decided and the four mechanical fixes land — all applicable in this revision cycle (v0.15 → v0.16). No Critical defects; all 54 prior dispositions verified; budget gate genuinely executed.
- **The item to watch is V5-01**: it is the same defect shape as v4's catch — a later amendment (D-42) silently stranding earlier criteria (AC-11/AC-12) — caught here because the reviewer swept *interactions between consecutive amendments*, not just file-internal consistency. It also validates the standing rule: **every amendment needs a ripple pass over criteria derived from the words it changes.**
- **Independence caveat**: see the provenance disclosure in §1. The findings above are reproducible from the stated grep/method by any fresh-context reviewer; the packet should state whether ratification-by-human or a second AI pass closes Rule 7 for v1.0.
