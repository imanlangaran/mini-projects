# Session Handoff — School Driver Platform Requirements (Phase 1 COMPLETE)

> Paste-or-point briefing for continuing work. Updated 2026-08-25 after Gate-1 lock.
> **Verify everything below against the files themselves — they are the source of truth, not this memo.**

## Project
Smart transportation platform for school students (daily home ↔ school shuttles). **Phase 1 — Requirements: COMPLETE. Baseline v1.0 LOCKED 2026-08-25; amended to v1.1 on 2026-09-05 (five PO rulings → D-49…D-53).** Any further change requires a formal amendment (version increment + §6 changelog + ripple sweep).

Project root: `test-user-story-schooldriver/` (under this workspace).

## Files
- `docs/requirements.md` — **v1.1 BASELINE LOCKED** (US-01…09 + ACs incl. the v1.1 additions, MoSCoW, NFR-01…09 incl. corrected NFR-08, §5 matrix, §6 full changelog)
- `docs/requirements/discovery.md` — **v1.1 BASELINE LOCKED** (CR-01…26, A-01…16 all confirmed, D-01…53, OQ ledger, SM-01…02)
- `docs/requirements/gate1-packet.md` — Gate-1 briefing; rulings recorded inline
- **Reader Edition** (generated, headers cite "Derived from baseline v1.1"): `docs/requirements/requirements-consolidated.md`, `docs/requirements/discovery-consolidated.md`
- Review trail: `story-review*.md` v1…v7 — **read-only, never modify**. v5 = CONDITIONAL PASS (remediated v0.16); v6 = commissioned confirmation pass (found V6-01/V6-02); v7 = pre-lock verification (**PASS**, zero new findings)
- Historical context (superseded): earlier versions of this memo described the pre-lock state

## What happened at Gate 1 (2026-08-25)
- PO confirmed all Gate-1 assumptions; **A-02 restated** ("dismissal time = end time of the relevant shift").
- Rule-7 disposition: commissioned confirmation pass → **review v6** found **V6-01** (budget arithmetic: 96 pd × $200 = $19,200 ≠ "$17,200"; old $18k ceiling was exceeded) and **V6-02** (OQ-06 trigger conflict blocking the lock).
- PO dispositions: ceiling raised **$18,000 → $20,000** (≈4% headroom); **OQ-06 resolved → D-48** (tweak direction-scope admin-selected per tweak, both-default); US-06 gained AC-5.
- Mechanical batch V6-03…05 applied; verification **review v7: PASS**; both artifacts bumped to **v1.0 BASELINE LOCKED**.
- Process incidents during remediation (disclosed in review v7 §3): transient A-02 row deletion (caught, restored, re-verified) + one cosmetic patch artifact (fixed).

## Standing rules (unchanged)
- **Rule 7:** author of edits does not verify; label self-reviews procedurally-independent-only.
- **Amendment protocol on locked artifacts:** version increment + §6 changelog + ripple sweep over every criterion citing changed wording (stranded-criteria defects of the V4-08/V5-01/V6-02 class are this project's recurring failure mode).
- **ID conventions:** CR/A/D/OQ sequential, never reused or renumbered; supersession via in-place annotation.
- **Estimation:** $200/person-day basis; build ceiling **$20,000**; operating $30/month. `MIN_TURNAROUND_MINUTES` = config, MVP 30 (CR-26/D-37).
- **Do NOT** rewrite the locked originals; use formal amendments. The Reader Edition must track amendments if the baseline ever changes.
- **Do NOT** mark an OQ resolved without the product owner's explicit answer.

## Remaining queue
1. **Phase 2 — UX & Prototyping: COMPLETE — Gate 2 signed by the PO (2026-09-05).** Governance spec amended: UX/Design role added (§2, §3.7, update note 2026-08-30). The UX/Design agent (skill setup: `docs/ux/skill-setup.md`) authored the Phase-2 package: **`docs/ux/flows.md`** (flows for every Must story US-01…05/07…09 + US-06 sketch), **`docs/ux/wireframes.html`** (clickable low-fi RTL prototype, screens S1–S17), **`docs/ux/ux-findings.md`** (author-side AC walkthrough — self-check only). Independent usability pass v1 (2026-09-05, 16 findings F1–F16 → `usability-pass-report-v1.md`) was fully remediated by the author-fix pass (incl. PO rulings UX-OQ-25/26); the independent **re-pass v2 returned CLEAN — 0 findings** (`usability-pass-report-v2.md`). Gate-2 sign-off package: **`docs/ux/gate2-packet.md` (signed 2026-09-05)**. Remaining UX open questions (PO only, non-blocking): **UX-OQ-22** (admin home content), **UX-OQ-23** (driver credential delivery), **UX-OQ-24** (multi-hour run UX — needed before Phase 3). Baseline OQ-10…13/15 were answered by the PO and formalized as the **v1.1 amendment (D-49…D-53)** — an independent amendment review of v1.1 is still owed per Rule 7 (see item 4).
2. *Optional* — solver design spike, 2–3 days ≈ $400–600 (D-46 cost lever; doubles as verification of the NFR-08 solver-formulation assumption). — **✅ DONE 2026-08-31** → see `spikes/solver-design/` (report + prototype). Standing outcome: V5-06 structure confirmed; TWO PO decisions now open (item 3).
3. **NEW (2026-08-31, from the spike) — PO decisions, both amendment candidates, before Phase 3:**
   - **R1 (objective):** adopt the additive per-student distance surrogate as the defined MVP objective, or fund an integrated route-allocation work-stream (spike-report §9 R1, Finding F2).
   - **R2 (run windows):** pin run-window semantics (pickup lead / drop tail) — zero-extent anchors [S,S)/(E,E) are the interim convention and reproduce all fixtures (spike-report §9 R2, Finding F5).
4. Open OQs: **OQ-17 only (post-MVP)** — OQ-10…13/15 were answered by the PO (2026-09-05) and formalized in the v1.1 amendment (D-49…D-53). **Pending (Rule 7): commission the independent amendment review of the v1.1 changes** (requirements.md / discovery.md) before Phase 3 architecture work builds on them.
5. Phase 6 reminder: pin the performance reference environment (A-12); re-validate NFR-05 core hours against the shift model (D-33). The spike sharpens this: determinism (D-45) also requires environment pinning (spike-report F4; add NFR-01 certificate-convergence risk F6 to the Phase-6 checklist).
6. If the PO wants extra assurance beyond review v7: run the Appendix-A fresh-context brief from review v6 in a clean session.
