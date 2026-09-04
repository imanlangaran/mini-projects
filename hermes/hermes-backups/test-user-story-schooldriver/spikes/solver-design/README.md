# Solver Design Spike — School Driver Platform

Deliverable of the optional D-46/NFR-08 cost-compression lever (approved to run
2026-08-31). Verifies the review-v5 V5-06 assumption: can an off-the-shelf
exact CP/MIP engine encode CR-26 pairwise turnaround + D-45 lexicographic
tie-breaks **without custom search**?

- **Read first:** `spike-report.md` (findings F1–F7, recommendations R1–R6,
  evidence in sections 4–5).
- **Code:** `prototype/school_solver.py` — CP-SAT model + brute-force
  verifier (US-04 AC-4 meter) + determinism check + demo/scale runners.
- **Headline results:**
  - 320/320 exact matches vs exhaustive search (3 seeds);
  - deterministic (D-45) in a pinned environment;
  - reference-scale 500/80 fully assigned, gap 6.25% → 4.15% (240 s → 480 s);
  - shortfall path (CR-18) exercised and reported;
  - V5-06 structure CONFIRMED; objective **surrogate exactness** needs a PO
    decision (R1); run-window semantics need pinning (R2).