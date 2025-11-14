from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime


class BaseAgent(ABC):
    def __init__(self, name: str, model: str, weight: float = 0.5):
        self.name = name
        self.model = model
        self.weight = weight

    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析数据并返回结果"""
        pass

    def format_output(
        self, signal: str, confidence: float, reasoning: str
    ) -> Dict[str, Any]:
        return {
            "agent": self.name,
            "model": self.model,
            "signal": signal,
            "confidence": confidence,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat(),
            "weight": self.weight,
        }
