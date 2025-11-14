import aiohttp
import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Dict, List
import os


class PriceCollector:
    def __init__(self):
        self.okx_base = "https://www.okx.com"
        self.binance_base = "https://api.binance.com"

    async def fetch_okx_price(self, symbol: str = "BTC-USDT") -> Dict:
        url = f"{self.okx_base}/api/v5/market/candles"
        params = {"instId": symbol, "bar": "1H", "limit": "1"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                if data["code"] == "0" and data["data"]:
                    candle = data["data"][0]
                    return {
                        "source": "okx",
                        "symbol": symbol.replace("-", "/"),
                        "timestamp": datetime.fromtimestamp(int(candle[0]) / 1000),
                        "open": Decimal(candle[1]),
                        "high": Decimal(candle[2]),
                        "low": Decimal(candle[3]),
                        "close": Decimal(candle[4]),
                        "volume": Decimal(candle[5]),
                    }
        return None

    async def fetch_binance_price(self, symbol: str = "BTCUSDT") -> Dict:
        url = f"{self.binance_base}/api/v3/klines"
        params = {"symbol": symbol, "interval": "1h", "limit": 1}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                if data:
                    candle = data[0]
                    return {
                        "source": "binance",
                        "symbol": "BTC/USDT",
                        "timestamp": datetime.fromtimestamp(candle[0] / 1000),
                        "open": Decimal(candle[1]),
                        "high": Decimal(candle[2]),
                        "low": Decimal(candle[3]),
                        "close": Decimal(candle[4]),
                        "volume": Decimal(candle[5]),
                    }
        return None

    async def collect_all(self) -> List[Dict]:
        tasks = [self.fetch_okx_price(), self.fetch_binance_price()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if r and not isinstance(r, Exception)]
