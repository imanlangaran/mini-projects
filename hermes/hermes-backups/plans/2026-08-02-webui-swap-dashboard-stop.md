# WebUI swap runbook — legacy dashboard → nesquena/hermes-webui (2026-08-02)

## State change performed

Replaced the legacy `hermes dashboard` (built-in web UI, basic-auth) with
**nesquena/hermes-webui** on the SAME public URL. Nothing else changed.

| Item | Before | After |
|---|---|---|
| UI process | `hermes dashboard --port 8080` (uvicorn, basic auth `iman`) | `/opt/hermes-webui/server.py` (Python stdlib, HMAC password cookie) |
| Repo | baked-in agent web dist | `/opt/hermes-webui` @ `320789ae` (cloned 2026-08-02, matches agent v0.19.0) |
| Port / URL | 8080 = Railway `$PORT` | 8080 = Railway `$PORT` — **same public URL** `https://hermes-railway-template-production-45d2.up.railway.app` |
| Watchdog cron | `dashboard-watchdog` (`*/5 * * * *`, no_agent, `dashboard-watchdog.sh`) | `webui-watchdog` (job `2e55023f2d15`, `*/5 * * * *`, no_agent, `webui-watchdog.sh`) |
| Supervisor | `/data/.hermes/scripts/dashboard-supervisor.sh` | `/data/.hermes/scripts/webui-supervisor.sh` (kept old script for rollback) |

## How it runs (durability)

- WebUI: `server.py` under `webui-supervisor.sh` (while-true respawn loop).
  Launched by the watchdog cron with `nohup ... &` → reparented to tini (ppid=1)
  → **survives gateway restarts**. Only a full redeploy kills it.
- Watchdog cron (persists on the volume): every 5 min, if `:8080` is down AND no
  `webui-supervisor.sh` / `server.py` process exists → relaunches supervisor
  detached. Silent when healthy (no_agent semantics). Recovery log:
  `/data/.hermes/logs/webui-watchdog.log`; server log `/data/.hermes/logs/webui.log`.
- WebUI state dir: `/data/.hermes/webui` (on the persistent volume).

## Credentials

- WebUI password: `HERMES_WEBUI_PASSWORD` env. Current fallback (in
  `webui-supervisor.sh`): `D9dvNoJfVaC4wRJHL8iATX7Y`.
- **Recommended:** set `HERMES_WEBUI_PASSWORD` in Railway env vars so redeploys
  use a managed secret (supervisor script prefers the env var when present).
- Old dashboard basic-auth (`iman` / Railway `HERMES_DASHBOARD_BASIC_AUTH_*`)
  is no longer used.

## Operations

```bash
# Status
curl -s http://127.0.0.1:8080/health          # {"status":"ok",...}
bash /data/.hermes/scripts/webui-watchdog.sh  # manual run; silent if healthy

# Stop webui entirely (also remove cron job webui-watchdog first!)
kill -9 <server.py pid> <supervisor pid>
# or: kill -9 $(awk '{print $1}' /proc/*/stat ...) — pkill NOT available in container

# Start manually
nohup bash /data/.hermes/scripts/webui-supervisor.sh >> /data/.hermes/logs/webui.log 2>&1 < /dev/null &
```

## Revert to legacy dashboard (rollback)

1. Stop webui: remove cron `webui-watchdog`, `kill -9` the `server.py` +
   `webui-supervisor.sh` PIDs.
2. Recreate old watchdog cron (`*/5 * * * *`, no_agent, `dashboard-watchdog.sh`)
   and start `bash /data/.hermes/scripts/dashboard-supervisor.sh` (uses
   Railway `HERMES_DASHBOARD_BASIC_AUTH_*`).
3. Only one UI may bind `$PORT` — never both.

**Trigger phrase (tell the agent):** *"revert to the old dashboard"* —
it will do steps 1–2 and verify `:8080` serves the dashboard login.

**Trigger phrase (tear down webui, nothing in its place):**
*"stop the webui and its watchdog"*.

## Notes / pitfalls

- `pkill`, `ps`, `ss`, `free` are NOT in the slim container — kill by PID,
  scan `/proc/*/cmdline`, check `/proc/net/tcp` (port 8080 hex = `1F90`).
- The `KeyError: 'agent:main:telegram:dm:...'` trace in the webui boot log is
  benign (state.db bridge trips over the live gateway messaging session).
- Running the watchdog MANUALLY from the agent terminal false-positives the
  /proc scan (the agent's own command wrapper contains `server.py` text in its
  cmdline). Test recovery via `cronjob action=run` instead.
- WebUI + agent release trains must stay pinned together (both v0.19-era).
- Durable-beyond-redeploy path (template entrypoint block) still pending:
  webui baked into the template image + `HERMES_WEBUI=true` launch. Until then,
  the watchdog cron is the resilience mechanism.
