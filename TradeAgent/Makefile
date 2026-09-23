# TradeAgent — convenience wrapper for the Docker workflow.
#
# Same commands on Linux (Docker Engine) and Windows (Docker Desktop +
# WSL2; run via `make` from a WSL2/PowerShell+make setup, or just copy
# the underlying docker commands from DOCKER.md).
#
# `make help` lists all targets.

COMPOSE ?= docker compose
IMAGE   ?= tradeagent:latest
TESTIMG ?= tradeagent:test

# Default scripted response for `make run` — override on the command line:
#   make run SCRIPTED='{"BTC/USDT": {"decision": "HOLD", "symbol": "BTC/USDT", "reasoning": "hold"}}'
SCRIPTED ?= {"BTC/USDT": {"decision": "NO_TRADE", "symbol": "BTC/USDT", "reasoning": "make smoke test"}}

.PHONY: help build build-test test run bridge down shell clean

help:
	@echo "TradeAgent — Docker workflow"
	@echo "  make build       build runtime image (analysis + bridge)"
	@echo "  make build-test  build test image (suite runs as a build gate)"
	@echo "  make test        run the full suite in the test image"
	@echo "  make run         analysis run (override: SCRIPTED='...')"
	@echo "  make bridge      start the chart bridge on :8000"
	@echo "  make down        stop the bridge / remove compose containers"
	@echo "  make shell       shell into the runtime image"
	@echo "  make clean       remove compose containers (keeps data/ and images)"

build:
	$(COMPOSE) build analysis bridge

build-test:
	docker build --target test -t $(TESTIMG) .

test: build-test
	docker run --rm $(TESTIMG)

# Full analysis run with live candles; args are appended after --scripted,
# so extra CLI flags can be passed: make run ARGS="--symbol ETH/USDT"
run:
	$(COMPOSE) run --rm analysis --strategy price-action --scripted '$(SCRIPTED)' $(ARGS)

bridge:
	$(COMPOSE) up -d bridge
	@sleep 2
	@curl -s -m 5 http://127.0.0.1:8000/ && echo

down:
	$(COMPOSE) down

shell:
	docker run --rm -it --entrypoint sh -v $(CURDIR)/data:/data $(IMAGE)

clean:
	$(COMPOSE) down --remove-orphans
