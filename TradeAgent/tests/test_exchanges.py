"""Unit tests for the exchange factory (create_binance)."""
import pytest

from trading.market.exchanges import create_binance


PROXY_ENV_VARS = ("https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY")


@pytest.fixture()
def no_proxy_env(monkeypatch):
    for name in PROXY_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_create_binance_sets_session_proxy_explicitly(monkeypatch):
    # ccxt ignores proxy env vars unless passed via session.proxies
    # (SETUP.md #9) — the factory must do that translation.
    monkeypatch.setenv("https_proxy", "http://proxy.example:10808")
    exchange = create_binance()
    assert exchange.session.proxies == {
        "http": "http://proxy.example:10808",
        "https": "http://proxy.example:10808",
    }


def test_create_binance_uppercase_env_fallback(monkeypatch):
    monkeypatch.delenv("https_proxy", raising=False)
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example:10808")
    exchange = create_binance()
    assert exchange.session.proxies == {
        "http": "http://proxy.example:10808",
        "https": "http://proxy.example:10808",
    }


def test_create_binance_direct_when_no_proxy(no_proxy_env):
    exchange = create_binance()
    assert not exchange.session.proxies


def test_create_binance_rate_limit_enabled():
    exchange = create_binance()
    assert exchange.enableRateLimit is True


def test_create_binance_env_exchange_override(monkeypatch, no_proxy_env):
    # Regions blocked by binance (HTTP 451) can switch exchanges via env,
    # e.g. TRADEAGENT_EXCHANGE=binanceus — without touching the CLI.
    monkeypatch.setenv("TRADEAGENT_EXCHANGE", "binanceus")
    exchange = create_binance()
    assert exchange.id == "binanceus"


def test_create_binance_explicit_id_beats_env(monkeypatch, no_proxy_env):
    monkeypatch.setenv("TRADEAGENT_EXCHANGE", "binanceus")
    exchange = create_binance("kraken")
    assert exchange.id == "kraken"


def test_create_binance_unknown_exchange_fails_loud(no_proxy_env):
    with pytest.raises(ValueError, match="unknown ccxt exchange"):
        create_binance("not_an_exchange")
