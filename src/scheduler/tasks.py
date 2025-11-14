from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from ..data_collectors.price_collector import PriceCollector
from ..data_collectors.news_collector import NewsCollector
from ..workflow.graph import BTCAgentWorkflow
from ..services.notification_service import NotificationService
from ..database.connection import get_db
from ..database.models import Price, News, Signal
from datetime import datetime
import asyncio


class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.price_collector = PriceCollector()
        self.news_collector = NewsCollector()
        self.workflow = BTCAgentWorkflow()
        self.notifier = NotificationService()

    def start(self):
        """启动所有定时任务"""
        # 每5分钟更新价格
        self.scheduler.add_job(
            self.collect_prices,
            CronTrigger.from_crontab("*/5 * * * *"),
            id="price_update",
        )

        # 每15分钟更新新闻
        self.scheduler.add_job(
            self.collect_news,
            CronTrigger.from_crontab("*/15 * * * *"),
            id="news_update",
        )

        # 每小时执行分析
        self.scheduler.add_job(
            self.run_analysis, CronTrigger.from_crontab("0 * * * *"), id="analysis"
        )

        # 每天评估
        self.scheduler.add_job(
            self.evaluate_performance,
            CronTrigger.from_crontab("0 0 * * *"),
            id="evaluation",
        )

        self.scheduler.start()
        print("调度器已启动")

    async def collect_prices(self):
        """采集价格数据"""
        try:
            prices = await self.price_collector.collect_all()

            with get_db() as db:
                for price_data in prices:
                    price = Price(**price_data)
                    db.add(price)

            print(f"采集了 {len(prices)} 条价格数据")
        except Exception as e:
            print(f"价格采集失败: {e}")

    async def collect_news(self):
        """采集新闻数据"""
        try:
            news_list = await self.news_collector.collect_all()

            with get_db() as db:
                for news_data in news_list:
                    news = News(**news_data)
                    db.add(news)

            print(f"采集了 {len(news_list)} 条新闻")
        except Exception as e:
            print(f"新闻采集失败: {e}")

    async def run_analysis(self):
        """执行完整分析流程"""
        try:
            # 获取最新数据
            with get_db() as db:
                prices = (
                    db.query(Price).order_by(Price.timestamp.desc()).limit(100).all()
                )
                news = db.query(News).order_by(News.published_at.desc()).limit(50).all()

            prices_data = [self._price_to_dict(p) for p in prices]
            news_data = [self._news_to_dict(n) for n in news]

            # 运行工作流
            signal = await self.workflow.run(prices_data, news_data)

            # 保存信号
            with get_db() as db:
                signal_record = Signal(
                    timestamp=datetime.now(),
                    signal_type=signal["signal"],
                    confidence=signal["confidence"],
                    reasoning=signal["reasoning"],
                    agents_consensus=signal,
                )
                db.add(signal_record)
                db.flush()

                # 发送通知
                await self.notifier.send_signal_notification(signal)

            print(f"分析完成: {signal['signal']} (置信度: {signal['confidence']:.2%})")
        except Exception as e:
            print(f"分析失败: {e}")

    async def evaluate_performance(self):
        """评估历史表现"""
        try:
            with get_db() as db:
                # 获取待评估的信号
                signals = db.query(Signal).filter(Signal.status == "PENDING").all()

                # 这里应该实现回测逻辑
                print(f"评估了 {len(signals)} 个信号")
        except Exception as e:
            print(f"评估失败: {e}")

    def _price_to_dict(self, price: Price) -> dict:
        return {
            "timestamp": price.timestamp,
            "source": price.source,
            "open": float(price.open),
            "high": float(price.high),
            "low": float(price.low),
            "close": float(price.close),
            "volume": float(price.volume),
        }

    def _news_to_dict(self, news: News) -> dict:
        return {
            "published_at": news.published_at,
            "source": news.source,
            "title": news.title,
            "content": news.content,
            "url": news.url,
            "sentiment_score": (
                float(news.sentiment_score) if news.sentiment_score else None
            ),
        }

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        print("调度器已停止")
