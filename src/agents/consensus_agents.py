from .base_agent import BaseAgent
from typing import Dict, Any, List
from collections import Counter


class TechConsensusAgent(BaseAgent):
    def __init__(self):
        super().__init__("TechConsensusAgent", "consensus", 1.0)

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """融合多个技术分析Agent的结果"""
        tech_results = data.get("tech_results", [])

        if not tech_results:
            return self.format_output("HOLD", 0.5, "No technical analysis available")

        # 加权投票
        weighted_signals = {}
        total_weight = 0

        for result in tech_results:
            signal = result["signal"]
            weight = result.get("weight", 0.5)
            confidence = result["confidence"]

            score = weight * confidence
            weighted_signals[signal] = weighted_signals.get(signal, 0) + score
            total_weight += weight

        # 选择得分最高的信号
        final_signal = max(weighted_signals, key=weighted_signals.get)
        final_confidence = (
            weighted_signals[final_signal] / total_weight if total_weight > 0 else 0.5
        )

        reasoning = (
            f"技术面共识：{len(tech_results)}个Agent分析，加权得分：{weighted_signals}"
        )

        return self.format_output(final_signal, final_confidence, reasoning)


class NewsConsensusAgent(BaseAgent):
    def __init__(self):
        super().__init__("NewsConsensusAgent", "consensus", 1.0)

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """融合多个新闻分析Agent的结果"""
        news_results = data.get("news_results", [])

        if not news_results:
            return self.format_output("HOLD", 0.5, "No news analysis available")

        # 加权投票
        weighted_signals = {}
        total_weight = 0

        for result in news_results:
            signal = result["signal"]
            weight = result.get("weight", 0.5)
            confidence = result["confidence"]

            score = weight * confidence
            weighted_signals[signal] = weighted_signals.get(signal, 0) + score
            total_weight += weight

        final_signal = max(weighted_signals, key=weighted_signals.get)
        final_confidence = (
            weighted_signals[final_signal] / total_weight if total_weight > 0 else 0.5
        )

        reasoning = (
            f"新闻面共识：{len(news_results)}个Agent分析，加权得分：{weighted_signals}"
        )

        return self.format_output(final_signal, final_confidence, reasoning)
