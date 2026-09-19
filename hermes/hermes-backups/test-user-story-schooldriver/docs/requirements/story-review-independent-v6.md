# Independent Requirements Review v6 (Gate-1 confirmation pass) — School Driver Platform

> **Commission:** product owner, 2026-08-25 (Gate-1 packet §3 decision (b)) — a contextually fresh confirmation pass before baseline lock v1.0.
> **Review date:** 2026-08-25 · **Artifacts reviewed (current state):**
> - `docs/requirements.md` — DRAFT v0.17 (stories US-01…09, MoSCoW, NFR-01…09, traceability §5, baseline §6)
> - `docs/requirements/discovery.md` — DRAFT v0.17 (CR-01…26, A-01…16, D-01…47, OQ-01…21, SM-01…02)
> - `story-review*.md` v1…v5 — treated strictly as history
> **Method:** review v5's stated method, re-executed from scratch: adversarial desk review against the defect taxonomy; hidden-assumption scan; edge-case sweep; CR↔story↔matrix consistency; stale-pointer and stale-text grep sweeps; **independent recalculation** of the estimate/gate arithmetic; interaction sweep across consecutive amendment cycles (the project's recurring failure mode); spot re-verification of prior dispositions (see §4 for exactly what was re-checked and how — no attestation beyond what was performed).

---

## 1. Verdict

**CONDITIONAL — two product-owner dispositions required before the v1.0 lock; neither invalidates the requirement model itself.**

The v0.16 remediation is genuinely in-file (V5-01 cluster coherent: CR-23 scope-restriction ↔ D-47 ↔ retargeted US-03 AC-12 ↔ replaced US-04 AC-11; V5-02…05 all landed). The v0.17 assumption confirmations are recorded. However, this pass finds **2 Major defects**, **1 Minor**, and **2 Notes** — including one arithmetic error that **review v5 explicitly attested as correct** (see V6-01), which validates the product owner's decision to commission this confirmation pass.

**Provenance (Rule 7 disclosure — read before weighing this review):** this pass was executed in the same working session that applied the v0.17 edits. Its independence is therefore **procedural-only** (method re-derived from v5's documented checklist; every disposition below re-checked against file contents; the reviewing pass did not consult v5's conclusions before forming findings). It is **not** contextually independent in the strong sense the commission requested. Two mitigating facts: (i) the v0.17 edit set was narrow (assumption bookkeeping + status lines), and the substantive content under review (v0.16) predates this session; (ii) the pass found defects v5 missed, including one in an area v5 claimed to have verified — evidence against rubber-stamping. For full contextual independence, run **Appendix A** (paste-ready brief) in a genuinely fresh session; its result supersedes or confirms this document.

---

## 2. Findings

| ID | Severity | Defect type | Location | Description | Suggested fix (PO decides) |
|---|---|---|---|---|---|
| V6-01 | **Major** | Arithmetic error / false attestation (budget gate) | requirements.md NFR-08 + §6; discovery.md D-46; story-review-independent-v5.md §3.1 | The envelope converts incorrectly: **96 pd × $200/day = $19,200**, not "~$17,200" as stated in all three places. Consequently the "~5% headroom" claim over the stacked high end is **false**: the $18,000 ceiling is **$1,200 below** the envelope's high end. The error propagated into D-46's rationale and into review v5 §3.1, which attested "envelope arithmetic checks out" — a false verification. (Low-end figure $11,600 = 58 pd × $200 is correct; the ≈90 pd gloss for $18,000 is internally consistent.) | PO chooses: **(α)** raise the ceiling to cover the true high end (e.g., $20,000 ⇒ ~4% headroom over $19,200); **(β)** keep $18,000 as a hard commitment and record the 78–96 pd tail as overrun risk with a mitigation note (spike lever pulls toward floor); or **(γ)** a justified re-estimate of the 20–40 pd band. Whichever is chosen, correct the dollar figures in NFR-08/D-46 and add a correction note to the v5 attestation. |
| V6-02 | **Major** | Cross-artifact contradiction (lock precondition) | discovery.md OQ-06 status vs requirements.md US-06 note + MoSCoW table | OQ-06's recorded trigger is "needed before US-06 is built **or baselined as Should**". The v1.0 baseline locks US-06 **as Should** (MoSCoW §3). So under discovery's own wording, **OQ-06 blocks the very lock this cycle prepares** — while requirements.md's US-06 note says only "must close before US-06 is built," under which the lock may proceed. The artifacts disagree on whether OQ-06 gates Gate 1; the stricter reading (discovery, the declared source of truth) blocks. Same amendment-interaction defect class as V4-08/V5-01: D-36's ripple narrowed OQ-06 inconsistently in the two files. | PO chooses: **(α)** answer OQ-06 now in-session (does a US-06 tweak apply to the to-school run, the from-school run, or admin-selected per tweak? CR-24 makes direction-scope a real design input) — cleanest path, unblocks lock immediately; **(β)** align both triggers to "before US-06 build" and record US-06's Should-baseline as provisional on OQ-06; or **(γ)** descope US-06 from the v1.0 baseline. |
| V6-03 | Minor | Incomplete application (introduced by v0.17) | discovery.md §3 rows A-01, A-03…A-11, A-14…A-16 | The PO confirmed these assumptions unchanged at Gate 1 (recorded in requirements.md §6 changelog), but the rows' Expiry cells still read "Gate 1"/"Gate 1 (confirm)" — only A-02 was updated to ✅. The ledger understates its own state. | Mechanical: set each confirmed row's Expiry to "✅ Confirmed (Gate 1, 2026-08-25)". Apply together with the V6-01/V6-02 dispositions in one v0.18 cycle. |
| V6-04 | Note | Ambiguity (wording, no behavior change) | requirements.md US-03 AC-14 warning clause | "compatible only if both are allocated to **that same school**" presumes one common school; a pair may share ≥ 2. Intent is clear ("a common school"); literal reading wobbles. | Reword to "at least one common school" whenever touched next; standalone change not warranted. |
| V6-05 | Note | Pointer-style residue (cosmetic) | requirements.md US-08 AC-1 | Cites "(OQ-05)" bare, whereas every other live citation annotates resolution — "(OQ-05, resolved)" (US-03 AC-5, CR-03). Residue of the V5-04 class, cosmetic only. | Add ", resolved" for uniformity whenever touched next. |

**Severity counts: 0 Critical, 2 Major (V6-01, V6-02), 1 Minor (V6-03), 2 Notes (V6-04/05).**

---

## 3. Verification results (what was checked, what was found)

### 3.1 Sweeps re-run fresh
| Sweep | Result |
|---|---|
| Stale-text grep (`morning`, `noon`, `revers`, `one-school`, `strictly contains`, `service time window`) | ✅ Clean — all hits are supersession annotations, history records, or the correctly-scoped CR-23/D-47 cluster |
| Stale pointers (closed OQs cited as live) | ✅ Clean — remaining OQ citations are resolution records/annotations; see V6-05 for one cosmetic residue |
| CR↔story↔matrix | ✅ All 9 trace lines match their matrix rows character-for-character |
| AC counts & GWT form | ✅ 9/9 stories ≥3 testable GWT ACs (6, 6, 14, 12, 5, 4+note, 4, 7, 4) |
| Estimate arithmetic (recalculated independently) | ❌ **V6-01** |
| Interaction sweep, consecutive amendments (D-36→OQ-06 ripples) | ❌ **V6-02** |

### 3.2 Substantive coherence checks
- **V5-01/D-47 cluster:** CR-23's D-47 annotation, D-47 itself, US-03 AC-12 (derived-window display), US-04 AC-11 (selection-shortfall) — mutually consistent; no boundary-containment test survives at MVP. ✅
- **US-04 AC-7 fixture:** eligibility preconditions make turnaround the discriminating cause (driver sex = both schools' sex; zones cover both schools+homes; both shifts selected). Sound. ✅
- **US-03 AC-14:** three cases (raw overlap reject / buffered∩no-common-school reject / buffered∩shared-school warn) consistent with CR-26 + D-38; entry-time school-adoption knowledge remains a known, accepted implicit dependency (flagged in v5 §3.5, unchanged). ✅ modulo V6-04 wording.
- **§1 scope paragraph, CR-04/CR-06, D-30 purity rationale, D-39 geometry ↔ CR-12 ↔ US-07 AC-1:** aligned. ✅
- **D-45 ↔ CR-07/CR-08/D-21:** evaluated-separately/decided-globally wording landed in both files. ✅
- **SM-01, MoSCoW litmus, MVP set, NFR-02…07/09:** unchanged, consistent. ✅
- **v0.17 edits:** A-02 restatement coherent with CR-01/D-33 (ripple sweep: no other text cites dismissal time); headers/§6 aligned at v0.17 — modulo V6-03 ledger completeness.

### 3.3 Prior dispositions — spot re-verification (scope honestly stated)
Re-verified directly against current files: the three v4 Majors (V4-01→D-35, V4-02→CR-06, V4-03→D-39); V4-07/OQ-18→D-34; V4-09→US-02 AC-4; V4-11→CR-18 eligibility clause; V4-14→D-30; all seven v5 findings as applied in v0.16; SM-01 reconciliation note; D-24's D-39 annotation; D-31's D-43 narrowing. Earlier dispositions (IR/V2/F series) were **not** exhaustively re-derived in this pass — they were attested by v5 §3.2 and their visible anchors check out; a fresh-context pass wanting to exceed this scope should follow Appendix A.

---

## 4. Conditions for the v1.0 lock

1. **PO disposition of V6-01** (ceiling amount vs. commitment posture) → corrective figures in NFR-08/D-46 + v5-attestation correction note.
2. **PO disposition of V6-02** (answer OQ-06, align triggers, or descope US-06).
3. **Mechanical batch** (single v0.18 cycle): V6-03 (+optionally V6-04/05), changelog entries, standard ripple sweep.

Upon 1–3: bump both artifacts to **v1.0 BASELINE LOCKED**, then proceed to the queued Reader Edition (`*-consolidated.md`, "Derived from baseline v1.0").

---

## Appendix A — Brief for a genuinely fresh-context confirmation pass (optional)

> Paste the following into a brand-new session (no shared conversation context) to obtain contextual independence this document cannot claim:

"You are an independent requirements reviewer. Adversarially desk-review `test-user-story-schooldriver/docs/requirements.md` (v0.17+) and `test-user-story-schooldriver/docs/requirements/discovery.md` (v0.17+) against the defect taxonomy (ambiguity, incompleteness, inconsistency, infeasibility, unverifiability, duplication, gold-plating, design-in-requirements). Do NOT read any `story-review*.md` file before forming your own findings. Execute: hidden-assumption scan; edge-case sweep; CR↔story↔matrix consistency; stale-pointer and stale-text grep sweeps; independent recalculation of all person-day/dollar figures in NFR-08/D-46; interaction sweep across consecutive amendment cycles; then compare against `story-review-independent-v6.md` and report agreements and any findings it missed. Output: verdict, findings table with severities, and explicitly what you verified vs. assumed."
