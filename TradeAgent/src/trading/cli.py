from trading.market.ccxt_provider import CCXTMarketDataProvider
from trading.market.exchanges import create_binance


def main():
    exchange = create_binance()
    provider = CCXTMarketDataProvider(exchange)

    candles = provider.get_candles(
        symbol="BTC/USDT",
        timeframe="15m",
        limit=10,
    )

    for candle in candles:
        print(candle)


if __name__ == "__main__":
    main()
