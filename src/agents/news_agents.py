from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from .base_agent import BaseAgent
from typing import Dict, Any, List


class NewsAgentOpenAI(BaseAgent):
    def __init__(self, weight: float = 0.4):
        super().__init__("NewsAgent-OpenAI", "gpt-4", weight)
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        news_list = data.get("news", [])

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """你是新闻情绪分析专家。分析比特币相关新闻的整体情绪和影响。
            返回JSON格式：{{"signal": "BUY/SELL/HOLD", "confidence": 0.75, "reasoning": "...", "sentiment": 0.6}}""",
                ),
                ("user", "新闻列表：\n{news_text}"),
            ]
        )

        news_text = "\n".join([f"- {n.get('title', '')}" for n in news_list[:10]])

        chain = prompt | self.llm
        response = await chain.ainvoke({"news_text": news_text})

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


class NewsAgentGemini(BaseAgent):
    def __init__(self, weight: float = 0.4):
        super().__init__("NewsAgent-Gemini", "gemini-2.0-flash-exp", weight)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.3)

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        news_list = data.get("news", [])

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Analyze Bitcoin news sentiment and policy impact.
            Return JSON: {{"signal": "BUY/SELL/HOLD", "confidence": 0.75, "reasoning": "..."}}""",
                ),
                ("user", "News:\n{news_text}"),
            ]
        )

        news_text = "\n".join([f"- {n.get('title', '')}" for n in news_list[:10]])

        chain = prompt | self.llm
        response = await chain.ainvoke({"news_text": news_text})

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


class RAGAgent(BaseAgent):
    def __init__(self, weight: float = 0.2):
        super().__init__("RAGAgent", "rag-retrieval", weight)
        self.embeddings = OpenAIEmbeddings()

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Simplified RAG - retrieve similar historical news
        query = data.get("query", "Bitcoin market analysis")

        # In production: query vector DB for similar historical contexts
        return self.format_output(
            "HOLD", 0.6, "Historical context suggests cautious approach"
        )
