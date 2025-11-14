import asyncio
from fastapi import FastAPI
from .scheduler.tasks import TaskScheduler
from .database.connection import engine
from .database.models import Base
import uvicorn

app = FastAPI(title="BTC Smart Agent System", version="1.0.0")

scheduler = TaskScheduler()


@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    # 创建数据库表
    Base.metadata.create_all(bind=engine)

    # 启动调度器
    scheduler.start()

    print("🚀 BTC智能监控与决策Agent系统已启动")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理"""
    scheduler.stop()
    print("👋 系统已关闭")


@app.get("/")
async def root():
    return {
        "message": "BTC Smart Agent System",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/analyze/manual")
async def manual_analysis():
    """手动触发分析"""
    await scheduler.run_analysis()
    return {"message": "分析已触发"}


@app.get("/signals/latest")
async def get_latest_signals():
    """获取最新信号"""
    from .database.connection import get_db
    from .database.models import Signal

    with get_db() as db:
        signals = db.query(Signal).order_by(Signal.timestamp.desc()).limit(10).all()
        return {
            "signals": [
                {
                    "timestamp": s.timestamp.isoformat(),
                    "signal": s.signal_type,
                    "confidence": float(s.confidence),
                    "reasoning": s.reasoning,
                }
                for s in signals
            ]
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
