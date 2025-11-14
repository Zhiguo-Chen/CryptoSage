from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from .base_agent import BaseAgent
from typing import Dict, Any
import pandas as pd


class TechAgentOpenAI(BaseAgent):
    def __init__(self, weight: float = 0.5):
        super().__init__("TechAgent-OpenAI", "gpt-4", weight)
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        price_df = pd.DataFrame(data.get("prices", []))

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """你是一位专业的比特币技术分析师。基于提供的价格数据和技术指标，
            分析当前市场趋势并给出交易建议（BUY/SELL/HOLD）。
            
            请提供：
            1. 信号类型（BUY/SELL/HOLD）
            2. 置信度（0-1之间）
            3. 详细推理过程
            
            以JSON格式返回：{{"signal": "BUY/SELL/HOLD", "confidence": 0.85, "reasoning": "..."}}""",
                ),
                ("user", "价格数据：\n{price_data}\n\n技术指标：\n{indicators}"),
            ]
        )

        indicators = self._calculate_indicators(price_df)

        chain = prompt | self.llm
        response = await chain.ainvoke(
            {"price_data": price_df.tail(10).to_string(), "indicators": str(indicators)}
        )

        # Parse response
        result = self._parse_response(response.content)
        return self.format_output(
            result["signal"], result["confidence"], result["reasoning"]
        )

    def _calculate_indicators(self, df: pd.DataFrame) -> Dict:
        if df.empty or len(df) < 2:
            return {}

        # Simple indicators
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        return {
            "price_change": float(
                (latest["close"] - prev["close"]) / prev["close"] * 100
            ),
            "volume_change": float(
                (latest["volume"] - prev["volume"]) / prev["volume"] * 100
            ),
            "high_low_range": float(
                (latest["high"] - latest["low"]) / latest["close"] * 100
            ),
        }

    def _parse_response(self, content: str) -> Dict:
        import json

        try:
            return json.loads(content)
        except:
            return {"signal": "HOLD", "confidence": 0.5, "reasoning": content}


class TechAgentGemini(BaseAgent):
    def __init__(self, weight: float = 0.5):
        super().__init__("TechAgent-Gemini", "gemini-2.0-flash-exp", weight)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.3)

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        price_df = pd.DataFrame(data.get("prices", []))

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a Bitcoin technical analyst. Analyze price trends and patterns.
            Return JSON: {{"signal": "BUY/SELL/HOLD", "confidence": 0.85, "reasoning": "..."}}""",
                ),
                ("user", "Price data:\n{price_data}"),
            ]
        )

        chain = prompt | self.llm
        response = await chain.ainvoke({"price_data": price_df.tail(10).to_string()})

        result = self._parse_response(response.content)
        return self.format_output(
            result["signal"], result["confidence"], result["reasoning"]
        )

    def _parse_response(self, content: str) -> Dict:
        import json

        try:
            return json.loads(content)
        except:
            return {"signal": "HOLD", "confidence": 0.5, "reasoning": content}
