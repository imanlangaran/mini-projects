# hermes-backups

Private repo under `~/Code/myGithub/mini-projects/hermes/` (owner: `emanlongaroon`).

## What this repo is

Originally set up as the **off-site backup store for a Hermes Agent instance**:
an hourly cron job (`hermes-backup-push.sh`, `no_agent`) was meant to run the
official `hermes backup` feature and push a single full snapshot to
`backups/hermes-backup.zip` here. **No backup zips exist in this tree or in git
history** — the job either never ran against this checkout or writes elsewhere.
(For the record: a fresh Hermes install can restore such a snapshot with
`hermes import backups/hermes-backup.zip`.)

Today the repo is used as the **working repo for the School Driver Platform**,
a multi-agent (AI agents + human Product Owner) software project:

- `test-user-story-schooldriver/` — the project tree:
  - `docs/requirements.md` + `docs/requirements/discovery.md` — locked
    requirements baseline (**v1.1**, 2026-09-05; US-01…09, CRs, D-01…53, OQ ledger)
  - `docs/requirements/story-review*.md` — independent review trail v1–v7
    (**read-only audit history — never modify**)
  - `docs/requirements/*-consolidated.md` — Reader Editions (derived from v1.1)
  - `docs/ux/` — Phase-2 UX package: flows, Farsi-RTL clickable wireframes
    (S1–S17), usability passes v1/v2, Gate-2 packet (signed 2026-09-05)
  - `spikes/solver-design/` — CP-SAT matching prototype + spike report
  - `HANDOFF.md` — **start here**: session handoff, standing rules, open items
- `plans/` — governance spec (roles, Rule 7), project lifecycle, the consolidated
  dispatch-brief run log (`run-log-briefs.md`), and the agent rulebook template.

## Ground rules

- **Rule 7 — author ≠ verifier:** whoever authors an artifact never verifies it;
  independent passes run in fresh contexts
  (see `plans/2026-08-04_110131-agent-workflow-gov.md`).
- **Locked baselines** change only via the formal amendment protocol
  (version increment + changelog + ripple sweep).
- Keep `session.jsonl` (raw Hermes session exports) out of git — it is ignored.

This repository is private. Do not make it public.
