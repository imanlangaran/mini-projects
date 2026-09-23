# TradeAgent — multi-stage image (Linux container, cross-platform via Docker
# Desktop on Windows). The Windows-only MetaTrader5 package is intentionally
# NOT installed here: it requires a native Windows MT5 terminal and cannot run
# inside a Linux container (see DOCKER.md).

# ---------------------------------------------------------------------------
# Stage 1 — builder: install the pinned dependency set into a virtualenv
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY requirements.txt .

# Virtualenv is created outside the project dir so it can be copied cleanly
# into the runtime stage; --copy keeps absolute paths working after the move.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2 — test: image with the source tree + test suite (used by CI and
# `docker build --target test`); proves host/container parity.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS test

# NO_PROXY is a portable image default: localhost traffic (bridge health
# checks, agent→bridge POSTs, the HTTP-based test suite) must never be
# routed through a proxy — Docker Desktop may inject HTTP_PROXY into
# containers when the host uses one.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    TRADEAGENT_DATA_DIR=/data \
    NO_PROXY=localhost,127.0.0.1,::1 \
    no_proxy=localhost,127.0.0.1,::1

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY src/ ./src/
COPY strategies/ ./strategies/
COPY chartbridge/ ./chartbridge/
COPY tests/ ./tests/
COPY pytest.ini chartbridge/__init__.py ./

RUN useradd --create-home --shell /bin/bash trader && \
    mkdir -p /data && chown trader:trader /data /app
USER trader

# Fail the build if the suite regresses: 251 core + 37 chartbridge tests.
# `python -m pytest` (not the console script) so /app lands on sys.path.
CMD ["sh", "-c", "python -m pytest -q && python -m pytest chartbridge -q"]

# ---------------------------------------------------------------------------
# Stage 3 — runtime: minimal image for analysis runs and the bridge
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# NO_PROXY: see the comment in the test stage — localhost traffic
# (agent → bridge POSTs, health checks) must never go through a proxy.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    TRADEAGENT_DATA_DIR=/data \
    TRADEAGENT_STRATEGIES_DIR=/app/strategies \
    NO_PROXY=localhost,127.0.0.1,::1 \
    no_proxy=localhost,127.0.0.1,::1

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY src/ ./src/
COPY strategies/ ./strategies/
COPY chartbridge/ ./chartbridge/

RUN useradd --create-home --shell /bin/bash trader && \
    mkdir -p /data && chown trader:trader /data /app
USER trader

# Default: analysis run (override command for the bridge / other entry points).
# --scripted is mandatory until the live Hermes backend is wired (USAGE §2);
# compose and examples below pass it explicitly.
ENTRYPOINT ["python", "-m", "trading.cli"]
CMD ["--strategy", "price-action", "--help"]
