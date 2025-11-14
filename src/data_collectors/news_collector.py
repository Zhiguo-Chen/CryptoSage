import aiohttp
from datetime import datetime
from typing import Dict, List
import os


class NewsCollector:
    def __init__(self):
        self.cryptopanic_key = os.getenv("CRYPTOPANIC_API_KEY")
        self.cryptopanic_base = "https://cryptopanic.com/api/v1"

    async def fetch_cryptopanic_news(self, currencies: str = "BTC") -> List[Dict]:
        url = f"{self.cryptopanic_base}/posts/"
        params = {
            "auth_token": self.cryptopanic_key,
            "currencies": currencies,
            "filter": "important",
            "public": "true",
        }

        news_list = []
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                if "results" in data:
                    for item in data["results"]:
                        news_list.append(
                            {
                                "source": "cryptopanic",
                                "published_at": datetime.fromisoformat(
                                    item["published_at"].replace("Z", "+00:00")
                                ),
                                "title": item["title"],
                                "url": item["url"],
                                "content": item.get("body", ""),
                                "keywords": [currencies],
                            }
                        )
        return news_list

    async def fetch_coindesk_rss(self) -> List[Dict]:
        # Simplified RSS parsing
        url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
        news_list = []

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                # In production, use feedparser library
                text = await resp.text()
                # Basic parsing placeholder
                news_list.append(
                    {
                        "source": "coindesk",
                        "published_at": datetime.now(),
                        "title": "CoinDesk News",
                        "url": url,
                        "content": "",
                        "keywords": ["BTC"],
                    }
                )
        return news_list

    async def collect_all(self) -> List[Dict]:
        tasks = [self.fetch_cryptopanic_news(), self.fetch_coindesk_rss()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_news = []
        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
        return all_news
