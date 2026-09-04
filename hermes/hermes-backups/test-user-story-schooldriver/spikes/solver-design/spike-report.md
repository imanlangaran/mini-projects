# Solver Design Spike — Report

**Project:** School Driver Platform · **Artifact:** `spikes/solver-design/` (this directory)
**Date:** 2026-08-31 · **Author:** Hermes agent (implementation + verification)
**Status:** COMPLETE — findings below are decision-ready for the product owner.
**Locked baseline referenced:** `test-user-story-schooldriver/docs/requirements.md` + `docs/requirements/discovery.md`, both **v1.0 BASELINE LOCKED (2026-08-25)**. Nothing in the locked artifacts was modified; this spike is an advisory artifact only.

---

## 1. Purpose (what D-46 bought)

NFR-08 / D-46 record an **optional 2–3-day solver design spike** (~\$400–600) as the cost-compression lever for the allocation core (7–15 pd estimate) and as the **verification of the review-v5 V5-06 assumption**:

> "…an off-the-shelf exact engine (CP/MIP class) can encode CR-26's pairwise turnaround and D-45's lexicographic tie-breaks **without custom search** — plausible, unverified until the optional design spike runs; the spike doubles as its verification." (requirements.md §NFR-08, estimate assumptions)

Deliverables of this spike:

1. A **model formulation** for MVP matching (every constraint traced to its baseline ID).
2. A **working prototype** (OR-Tools CP-SAT) implementing the formulation.
3. **Verification evidence** that the prototype matches exhaustive search on small instances (the US-04 AC-4 meter) and is deterministic (D-45).
4. **Scale evidence** on a reference-ish dataset (NFR-01 shape: 500/50/10/2).
5. **Findings + recommendations**, including two wording gaps in the locked baseline that need product-owner attention (formal amendments).

---

## 2. Model formulation (MVP scope)

### 2.1 Variables

| Variable | Meaning | Baseline trace |
|---|---|---|
| `x[d, r, s] ∈ {0,1}` | student *s* assigned to driver *d* on run *r* | CR-06, D-33, D-36 |
| `y[d, r] ∈ {0,1}` | driver *d* serves run *r* (any student) | runs as an output of allocation |
| `z[s, dir] ∈ {0,1}` | student *s* unassigned for direction *dir* (shortfall report channel, never published) | CR-18 |
| `c[s] ∈ {0,1}` | student *s* has the **same driver** for to-school and from-school (continuity) | D-45 tier 1 |

### 2.2 Runs and time anchors

A run is the atomic allocation unit: **(school, shift, direction)**. School identity is an *output* of matching, never a driver attribute (D-36). Each student selects exactly one shift of their school (D-33); flagged students are excluded (CR-19).

**Time anchors (modeling note — see Finding F5):** to-school runs anchor at the shift start `S`; from-school runs anchor at the shift end `E` (D-39: from-school starts at the school at shift end). Anchors are zero-extent. This convention reproduces every baseline fixture *literally*:

- US-04 AC-7: School A from-school **ends 12:00** (= `E_A`), School B to-school **starts 12:00** (= `S_B`) ⇒ gap 0 < 2×30 ⇒ one driver cannot serve both ✓
- Same-school back-to-back (CR-26 iii): `E ≤ S′` touching allowed (A-16) ✓
- D-45 continuity (same driver AM+PM of the same shift) is feasible: to [S,S) then from [E,E), `S < E` ✓

### 2.3 Constraints (all as linear clauses — no custom search)

| # | Constraint | Formulation | Baseline |
|---|---|---|---|
| C1 | Assignment or shortfall | `Σ_d x[d,r,s] + z[s,dir] = 1` per student-direction | CR-06, CR-18 |
| C2 | Capacity per direction run | `Σ_s x[d,r,s] ≤ cap[d, dir]` per (driver, run) | D-34, A-13 |
| C3 | Run activation | `x ⇒ y` per (driver, run, student) | D-24 (leg cost paid once per driver-run) |
| C4 | Eligibility — selection | x exists only if `(shift, dir) ∈ driver.selected` | D-47 |
| C5 | Eligibility — gender | `driver.sex == student.sex` (per-student reading of AC-9; see §8) | CR-21 |
| C6 | Eligibility — area | `student.home_zone ∈ driver.zones` **and** `school.zone ∈ driver.zones` (union-coverage reading; see §8) | CR-22, D-43 |
| C7 | Same-day compatibility | per driver, per run pair: `y[r1] + y[r2] ≤ 1` when `run_pair_incompatible(r1, r2)` — static precompute | CR-26, D-37 |

**CR-26 static pairwise rule** (`run_pair_incompatible`, ordered A before B):

```
same school:        compatible iff A.end ≤ B.start
                    (iii: back-to-back valid; half-open per A-16)
different schools:  compatible iff B.start − A.end ≥ 2·MIN_TURNAROUND
                    (ii: MVP T = 30, D-37)
```

This is a **pure static-clause encoding**: every incompatible pair becomes a boolean `y+y′ ≤ 1` constraint at model build time. Clause count ≈ drivers × runs²/2 (50 drivers × 40 runs ⇒ ~39k clauses at reference scale) — no branching, no custom search, exactly the V5-06 question.

### 2.4 Objective (D-21/D-45) — and the surrogate caveat (Finding F2)

**Stage A — distance.** One global solve (D-45) minimizing total driving distance + a large penalty per skipped student-direction (CR-18 channel):

```
Σ_runs  leg(d,r)·y[d,r]                     # to-school only: driver home → school, once per
                                            # driver-run (D-24); from-school has no deadhead (D-39)
      + Σ_students inc(d,r,s)·x[d,r,s]     # to-school: home→school; from-school: school→home
      + P · Σ z[s,dir]                      # P = 10⁹ ≫ any real distance sum
```

All distances are **integer-scaled** (×100, i.e. 0.01-unit resolution) because CP-SAT requires integer coefficients.

⚠️ **Surrogate caveat:** the per-student incremental cost is an **additive surrogate** for the true per-run route length. The true route problem is a small TSP per run (pickup order, D-39) — see **Finding F2** for why this is the single most important decision the PO must make.

**Stage B — continuity tier (D-45 tier 1, exact).** Minimize `W·(distance) − Σc[s]` with `W > n_students`:

- any distance improvement of 1 unit outweighs *all* continuity points ⇒ tier-1 exact: distance is never traded for continuity;
- among distance-optimal plans, continuity is maximized — exactly D-45;
- (the earlier `distance == floor` equality formulation timed out at 100-student scale; the weighted form is provably equivalent and solves in seconds).

**Stage C — stable lexicographic order (D-45 tier 2).** Iterated fixing over the canonical assignment order (school, shift, direction, student, driver): maximize each variable in turn with all previous ones fixed. Exact, but O(#assignment vars) sequential solves ⇒ **verification-only**; production uses the stage-B solution plus solver determinism (Finding F4).

---

## 3. Prototype

**File:** `prototype/school_solver.py` (single file, ~700 lines, stdlib + OR-Tools only)

- Engine: **Google OR-Tools 9.15 CP-SAT** (free, permissive Apache-2.0 license — satisfies the D-21 Gate-B "free vs licensed" question at **$0 license cost**, consistent with the NFR-08 $30/month operating ceiling and D-44 self-hosting).
- Modes:
  - `--verify` — AC-4 meter: N random small instances, CP-SAT vs brute-force exhaustive enumeration; asserts exact equality of (min distance, max continuity, lexicographic-min assignment).
  - `--determinism` — D-45 check: two identical solves ⇒ identical report.
  - `--demo` — 100/15/5/3 medium instance.
  - `--scale [--dense --scale-drivers N]` — reference-ish 500/50/10/2 (NFR-01 shape).
- Reproduce: `python prototype/school_solver.py --verify --instances 160 --seed 20260831` (requires `pip install ortools`).

---

## 4. Verification evidence (US-04 AC-4 meter)

Run on 2026-08-31, all instances random-seeded, brute force = exhaustive product over eligible-driver choices per student-direction with capacity and CR-26 pruning:

| Seed | Instances | Exact matches | Mismatches |
|---|---|---|---|
| 20260831 | 160 | 160 | 0 |
| 424242 | 100 | 100 | 0 |
| 777 | 60 | 60 | 0 |
| **Total** | **320** | **320** | **0** |

Small-instance exhaustive verification is the acceptance meter for the exact-optimality guarantee (D-22, US-04 AC-4) and it **passes**. The metric compared is the full plan triple (distance, continuity, lexicographic assignment) — not just the objective value, so tie-breaking is verified too.

**Determinism (D-45):** two identical solves of an 8-student/5-driver instance produced bit-identical assignment hashes (and identical distance/continuity) in this environment. See Finding F4 for the environment-pinning caveat.

---

## 5. Scale evidence (NFR-01 shape)

Prototype instances: 500 students / 10 schools / 2 shifts / driver counts as shown, random geometry (Euclidean stand-in for D-19 road distance — structure is what is tested, not exact map values).

**Tight instance (50 drivers, constrained zones/selections — heavy shortfall path):**

| Metric | Value |
|---|---|
| Model size | 8,898 assignment vars, 2,000 run vars, 792 skip vars |
| Stage A (240 s cap) | FEASIBLE — objective 2,550,025,970.82 (scaled), **255 unassigned** student-directions |
| Certificate | none within cap (gap ≈ 100% — skip-penalty-dominated LP bound) |

Observation: with 50 drivers the instance is **latently infeasible** (see §7) — this run exercises the CR-18 shortfall reporting channel (unassigned list + causes) and the NFR-01 "no certificate within cap ⇒ report produced, publication blocked" fail-safe behavior.

**Dense feasible instance (80 drivers, all zones, caps 3–6 — the NFR-01-style reference test):**

| Metric | 240 s cap | 480 s cap |
|---|---|---|
| Model size | 30,387 assignment vars, 3,200 run vars, 792 skip vars | same |
| Stage A status | FEASIBLE | FEASIBLE |
| Best solution (unscaled) | 42,948.50 | **42,015.88** |
| Best bound (unscaled) | 40,263.18 | 40,271.90 |
| Gap | 6.25% | **4.15%** |
| Unassigned | **0** | **0** |

At reference scale the model *finds* a fully feasible, near-optimal plan quickly and the bound is **tight** (few-% gap), but the formal certificate had not closed within 8 minutes. Trajectory: solution improves steadily, bound advances slowly — the pairwise CR-26 clauses weaken the LP relaxation (Finding F6).

---

## 6. Findings

- **F1 — V5-06 assumption CONFIRMED for structure:** the entire MVP constraint set (C1–C7), including CR-26 pairwise turnaround and D-45's continuity tie-break, encodes as plain linear clauses in an off-the-shelf CP-SAT model — **no custom search needed**. 320/320 exact AC-4 matches and 0-skip fully assigned plans at reference scale demonstrate it.
- **F2 — V5-06 assumption PARTIAL for the objective (PO decision required):** "minimum total driving distance" (CR-07/D-21) as true *route* length requires solving a TSP per run jointly with the allocation — that **cannot** be done in CP-SAT without custom search (column-generation / joint route-arc model). The additive per-student surrogate *is* exactly encodable, and the verification harness proves the model finds the true minimum **of the surrogate — not of the route-TSP**. Two ways forward (Recommendation R1).
- **F3 — tie-break strategy is exact and practical:** the weighted-lexicographic objective (W·dist − cont) implements D-45 tier 1 exactly with one solve; the stable lexicographic tier 2 is exact via iterated fixing (verification) and practically deterministic in production (F4). The weighted form beats the naïve equality-constraint form at scale (§2.4, stage B).
- **F4 — D-45 determinism requires environment pinning:** CP-SAT is deterministic given identical binary/parameters/thread count/seed. Production must pin the container image + solver version + worker count — exactly the A-12 reference-environment item already on the Phase-6 checklist — and the AC-4 harness must run in that pinned environment.
- **F5 — run-window semantics are unspecified in the baseline (PO decision required):** the zero-extent anchors [S,S)/(E,E) reproduce every fixture literally (AC-7, CR-26 iii, D-45 continuity), but real pickup/drop-off run durations are not defined anywhere in the v1.0 artifacts. Phase-3 must pin them (pickup lead / drop tail) or matching stays conservative for cross-school pairings. Amendment candidate (R2).
- **F6 — certificate convergence at reference scale is the NFR-01 risk:** ~4% gap after 8 min on 500/80; if the bound trajectory holds, a 0-gap certificate could exceed the 3 h Goal (still inside the 24 h Fail). Mitigations: solve per direction-run decomposed (the only coupling is continuity — stage B), tighter cuts on the packing clauses (2-matching/separation), or the D-21 Gate-B re-check of the exact-solver choice (e.g., a licensed MIP with stronger machinery) at Phase-3. No baseline change needed now — but NFR-01's Goal may need a re-statement ("certificate within envelope" vs "plan quality within envelope + cert.") if the PO chooses the surrogate (R1).
- **F7 — cost impact on the estimate:** the prototype (formulation + verification harness + scale tests + this report) took ≈ 1 person-day of agent time — inside D-46's 2–3 d / $400–600 envelope. The 7–15 pd allocation-core estimate stands; the spike prevents the likeliest overruns. Actuals re-checked at Gate 7 (NFR-08) as planned.

---

## 7. Structural insight worth recording

In the tight run, 50 drivers cannot cover 500 students / 10 schools with random generation: every to-school run of a given shift starts at the **same minute** for every school, so CR-26 (ii) limits a driver to **one school per shift's to-school run** — 50 drivers × ~4.5 avg seats ≈ 225 < 250 demanded per sex half. This is a fixture-design lesson for US-04 AC-7-style tests, not a model bug: any realistic feasibility dataset needs enough drivers that CR-26 does not bite globally (or the acceptance tests must assert the shortfall cause, like AC-7 does).

---

## 8. Modeling notes (interpretations taken, all reversible at Phase-3)

- CR-21 implemented as per-student sex match ("male driver never carries female students", AC-9 literal). **D-30's** "same sex as both schools' students" is read as school-shift-level sex certification. Both readings coincide for same-sex school shifts.
- CR-22/D-43 implemented as union-coverage (each of home and school zone ∈ the driver's selected zone set); AC-7's "zones cover both schools and both homes" may intend a single zone covering all — check with PO at Phase-3.
- Distances: Euclidean stand-in for D-19 road network; the objective interface accepts any metric (the D-44 engine's road matrix swaps in unchanged).
- MIN_TURNAROUND = 30 (D-37 MVP value); run windows zero-extent (F5).

---

## 9. Recommendations (decision-ready)

| # | Recommendation | Owner | When |
|---|---|---|---|
| R1 | **Adopt the additive per-student distance surrogate as the defined MVP objective** (formal amendment of CR-07/CR-08/US-04 AC-4/AC-5 + NFR-01 wording: "total distance" := surrogate sum; per-run true routing becomes a post-allocation Phase-3 refinement with a documented gap bound) — OR schedule an integrated route-allocation solve as a separate work-stream with its own ceiling headroom. | PO | before Phase-3 |
| R2 | **Pin run-window semantics** (pickup lead / drop tail, MVP config values) via formal amendment; zero-extent anchors as the interim convention. | PO | before Phase-3 |
| R3 | Adopt OR-Tools CP-SAT as the MVP solver choice: free (Gate-B D-21), encodes the full constraint set (F1), fits within the $30/mo ops ceiling (D-44 self-hosting). | PO | Gate-B (Phase-3 kick-off) |
| R4 | Keep the verification harness as the AC-4 acceptance meter; add it to the regression suite; run it in the pinned environment (F4). | team | Phase-3 |
| R5 | Enter the NFR-01 cert-convergence risk (F6) on the Phase-6 checklist next to the A-12/NFR-05 items. | team | Phase-6 |
| R6 | Re-check actuals vs the $20,000 ceiling at Gate-7 as planned; spike spend inside envelope (F7). | finance/team | Gate-7 |

---

## 10. How to re-run

```bash
pip install ortools           # tested with 9.15
python prototype/school_solver.py --verify --instances 160 --seed 20260831
python prototype/school_solver.py --determinism
python prototype/school_solver.py --demo
python prototype/school_solver.py --scale --dense --scale-drivers 80 --time-limit 240
python prototype/school_solver.py --scale --time-limit 240        # tight/shortfall path
```

Observed outputs are recorded in sections 4–5 above.

---

## 11. Deliverable file map

- `prototype/school_solver.py` — prototype (model, brute force, verifier, demos, scale)
- `spike-report.md` — this report