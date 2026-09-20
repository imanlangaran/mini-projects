"""Strategy configuration — the pythonic, executable source of truth.

Each strategy lives in ``strategies/<slug>/`` and contains two files that
MUST agree with each other:

- ``strategy.md`` — human- and agent-readable declaration of what the
  strategy needs (timeframes, indicators, risk rules). It references its
  config via the ``Config:`` metadata line.
- ``config.py`` — the same requirements as executable Python: the exact
  timeframes to fetch, minimum candle counts, and the indicator functions
  (imported from ``trading.indicators.library``) to run, with their
  parameters.

The core system reads ONLY ``config.py``. The markdown is for the agent
and for humans; the code is what drives the pipeline (collector ->
calculator -> snapshot). If the two drift apart, the code wins — so keep
them in sync.
"""

from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

import pandas as pd


@dataclass(frozen=True)
class IndicatorSpec:
    """One indicator as declared by a strategy config.

    ``func`` is imported from ``trading.indicators.library`` and must be a
    callable with the signature ``func(df: pd.DataFrame, **params) ->
    pd.Series``. The calculator stores its result under ``df[name]``.
    """

    name: str
    func: Callable[..., pd.Series]
    params: dict[str, Any] = field(default_factory=dict)
    #: Timeframes this indicator applies to; ``None`` means every timeframe.
    timeframes: tuple[str, ...] | None = None


@dataclass(frozen=True)
class StrategyConfig:
    """Validated, executable requirements of one strategy.

    Everything the collector and calculator need is derived from here —
    never from hardcoded preferences and never from the markdown file.
    """

    slug: str
    name: str
    symbols: tuple[str, ...]
    timeframes: tuple[str, ...]
    min_candles: dict[str, int]
    indicators: tuple[IndicatorSpec, ...]
    risk_per_trade: float = 0.01
    params: dict[str, Any] = field(default_factory=dict)

    def indicators_for(self, timeframe: str | None = None) -> tuple[IndicatorSpec, ...]:
        """Indicators that apply to ``timeframe`` (all if ``None``)."""
        if timeframe is None:
            return self.indicators
        return tuple(
            spec
            for spec in self.indicators
            if spec.timeframes is None or timeframe in spec.timeframes
        )

    def indicator_names(self, timeframe: str | None = None) -> tuple[str, ...]:
        return tuple(spec.name for spec in self.indicators_for(timeframe))


def strategies_dir() -> Path:
    """Repository-level strategies directory.

    Override with the ``TRADEAGENT_STRATEGIES_DIR`` environment variable.
    """
    env = os.environ.get("TRADEAGENT_STRATEGIES_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3] / "strategies"


def load_strategy_config(slug: str, base_dir: Path | None = None) -> StrategyConfig:
    """Load and validate the pythonic config of a strategy.

    Resolves ``<base_dir>/<slug>/config.py`` (default: the repo's
    ``strategies/`` folder) and builds a :class:`StrategyConfig` from the
    module constants:

    - ``SYMBOLS``: tuple[str, ...]
    - ``TIMEFRAMES``: tuple[str, ...]
    - ``MIN_CANDLES``: dict[str, int]  (per timeframe)
    - ``INDICATORS``: tuple[IndicatorSpec, ...]
    - ``RISK_PER_TRADE``: float (default 0.01)
    - ``PARAMS``: dict[str, Any] (strategy-specific knobs, default {})

    Raises ``ValueError`` with a descriptive message when the module is
    missing a required declaration or its contents are inconsistent.
    """
    base = base_dir or strategies_dir()
    module_path = base / slug / "config.py"

    if not module_path.is_file():
        raise ValueError(
            f"No pythonic config found for strategy {slug!r}: {module_path}"
        )

    spec = importlib.util.spec_from_file_location(
        f"strategies.{slug}.config", module_path
    )
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load config module for strategy {slug!r}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    timeframes = _require_tuple(module, "TIMEFRAMES", slug)
    if not timeframes:
        raise ValueError(f"{module_path}: TIMEFRAMES must not be empty")

    min_candles = _require_dict(module, "MIN_CANDLES", slug)
    missing = set(timeframes) - set(min_candles)
    if missing:
        raise ValueError(
            f"{module_path}: MIN_CANDLES is missing an entry for "
            f"timeframe(s) {sorted(missing)} declared in TIMEFRAMES"
        )
    for timeframe, count in min_candles.items():
        if not isinstance(count, int) or count <= 0:
            raise ValueError(
                f"{module_path}: MIN_CANDLES[{timeframe!r}] must be a "
                f"positive integer, got {count!r}"
            )

    indicators = tuple(getattr(module, "INDICATORS", ()))
    names = [spec.name for spec in indicators]
    if len(names) != len(set(names)):
        raise ValueError(f"{module_path}: indicator names must be unique")
    for spec in indicators:
        if not isinstance(spec, IndicatorSpec):
            raise ValueError(
                f"{module_path}: INDICATORS must contain IndicatorSpec "
                f"instances, got {type(spec).__name__}"
            )
        if spec.timeframes is not None:
            unknown = set(spec.timeframes) - set(timeframes)
            if unknown:
                raise ValueError(
                    f"{module_path}: indicator {spec.name!r} references "
                    f"undeclared timeframe(s) {sorted(unknown)}"
                )

    return StrategyConfig(
        slug=slug,
        name=getattr(module, "NAME", slug.replace("-", " ").title()),
        symbols=_require_tuple(module, "SYMBOLS", slug),
        timeframes=timeframes,
        min_candles=min_candles,
        indicators=indicators,
        risk_per_trade=float(getattr(module, "RISK_PER_TRADE", 0.01)),
        params=dict(getattr(module, "PARAMS", {})),
    )


def _require_tuple(module, attribute: str, slug: str) -> tuple:
    value = getattr(module, attribute, None)
    if value is None or not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(
            f"strategies/{slug}/config.py must declare {attribute} as a "
            f"tuple/list, got {value!r}"
        )
    return tuple(value)


def _require_dict(module, attribute: str, slug: str) -> dict:
    value = getattr(module, attribute, None)
    if not isinstance(value, dict):
        raise ValueError(
            f"strategies/{slug}/config.py must declare {attribute} as a "
            f"dict, got {value!r}"
        )
    return value