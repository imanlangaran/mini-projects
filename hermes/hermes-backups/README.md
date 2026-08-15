# hermes-backups

Automated full backups of a Hermes Agent instance, pushed to this **private** repository
by a scheduled cron job.

- **Owner:** `emanlongaroon`
- **Cadence:** every hour, 07:00–24:00 Tehran time (Asia/Tehran, UTC+3:30) — i.e. 18 runs/day
- **Source:** Hermes Agent running on a Railway deployment (`HERMES_HOME=/data/.hermes`)

---

## What this repo is for

This repo is the off-site disaster-recovery store for a Hermes Agent instance. Every hour
the deployment runs the official Hermes backup feature and pushes the result here, so that
**a brand-new Hermes install (or another AI agent) can rebuild the exact same instance** —
configuration, skills, session history, memory, cron jobs, kanban boards, and API keys.

Each run produces a full backup zip, stored as a **single file that is replaced**:

- `backups/hermes-backup.zip` — the latest full backup (overwritten by every new run)

Backups are created with the official Hermes backup feature:

**What is inside each zip** (created with the `hermes backup` feature):

| Content | Why it matters |
|---|---|
| `config.yaml` | All settings (models, providers, toolsets, skins…) |
| `.env` | **API keys / secrets — do NOT make this repo public** |
| `auth.json`, `state.db` | OAuth/credential pools, session store (SQLite + FTS5) |
| `sessions/` | Gateway routing index + transcripts |
| `skills/` | Installed skills (incl. agent-created ones) |
| `memory/`, `kanban/`, `cron/`, `plugins/`, `projects.db` | Memories, boards, scheduled jobs, plugins, projects |

**Stripped from each zip** (regenerable, not user data — keeps the repo lean):

- `bin/` — tool binaries (`uv`, `uvx`, `tirith`); a fresh install provides its own
- `cache/`, `models_dev_cache.json` — regenerable caches

---

## How to restore this backup into a new Hermes (read me, AI agent)

You (an AI agent) can fully restore the instance. **Use the newest zip** — every zip is a
complete snapshot, so only the latest one is needed.

### 1. Get the backup zip

The backup is a single file — the newest snapshot is always at:

```bash
backups/hermes-backup.zip
```

(Clone the repo, or download that one file from the GitHub web UI / API.)

### 2. Import it with the official Hermes feature

```bash
hermes import backups/hermes-backup.zip
```

`hermes import <zip>` extracts the backup into `$HERMES_HOME` (default `~/.hermes`),
restoring configuration, skills, sessions, and data. Add `--force` to overwrite an
existing install without confirmation:

```bash
hermes import --force backups/hermes-backup.zip
```

### 3. Verify

```bash
hermes doctor        # configuration & dependency check
hermes cron list     # scheduled jobs restored
hermes --version
```

If the instance runs with a non-default `HERMES_HOME` (this deployment uses
`/data/.hermes`), make sure it is exported before importing:

```bash
export HERMES_HOME=/data/.hermes
hermes import backups/hermes-backup.zip
```

### Manual alternative (no Hermes CLI yet)

```bash
unzip backups/hermes-backup.zip -d "$HERMES_HOME"   # extracts config/, skills/, state.db, …
```

Then start the gateway: `hermes gateway`.

---

## ⚠️ Security

- This repository is **private** and **contains secrets** (API keys in `.env`, OAuth
  tokens in `auth.json`). Never change it to public, never fork/share it.
- If you suspect exposure, rotate the keys in `.env` and re-push a fresh backup.

---

## Maintenance notes (for the operator / AI agent)

- **Scheduling:** the hourly job is a Hermes cron job (`no_agent` script job) running
  `hermes-backup-push.sh` from `$HERMES_HOME/scripts/` on schedule `30 3-20 * * *` (UTC),
  which maps to **every hour 07:00–24:00 Tehran time** (Tehran = UTC+3:30, so minute :30
  UTC = :00 Tehran).
- **Retention:** the working tree holds a **single** backup file
  (`backups/hermes-backup.zip`) — every run **replaces** it, it never accumulates.
  Previous versions live on in git history; when the local `.git` exceeds 900 MB the
  script squashes history (orphan snapshot + force push) so the remote never hits
  GitHub's size limits.
- **Logs:** each run appends to `$HERMES_HOME/logs/backup-push.log`.
- **Run manually anytime:** `bash $HERMES_HOME/scripts/hermes-backup-push.sh`
- **On success the job is silent** (no message is sent); on failure it emits an error
  alert with a pointer to the log.
