from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .base_agent import BaseAgent
from typing import Dict, Any, List
import json


class DecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("DecisionAgent", "gpt-4", 1.0)
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.2)

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        tech_results = data.get("technical_analysis", [])
        news_results = data.get("news_analysis", [])

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """你是最终决策者。综合技术分析和新闻分析结果，做出最终交易决策。
            
            考虑因素：
            1. 各Agent的信号和置信度
            2. 技术面与新闻面的一致性
            3. 各Agent的历史准确率权重
            
            返回JSON：{{"signal": "BUY/SELL/HOLD", "confidence": 0.85, "reasoning": "...", "consensus_level": 0.9}}""",
                ),
                ("user", "技术分析结果：\n{tech}\n\n新闻分析结果：\n{news}"),
            ]
        )

        chain = prompt | self.llm
        response = await chain.ainvoke(
            {
                "tech": json.dumps(tech_results, ensure_ascii=False, indent=2),
                "news": json.dumps(news_results, ensure_ascii=False, indent=2),
            }
        )

        result = self._parse_response(response.content)
        return self.format_output(
            result["signal"], result["confidence"], result["reasoning"]
        )

    def _parse_response(self, content: str) -> Dict:
        try:
            return json.loads(content)
        except:
            return {"signal": "HOLD", "confidence": 0.5, "reasoning": content}


class DiscussionAgent(BaseAgent):
    def __init__(self):
        super().__init__("DiscussionAgent", "gpt-4", 1.0)
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.5)

    async def moderate_discussion(
        self, agents_results: List[Dict], rounds: int = 3
    ) -> Dict[str, Any]:
        """主持多Agent辩论式讨论"""
        discussion_history = []

        for round_num in range(rounds):
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """你是讨论主持人。各Agent已提出初步观点，现在进行第{round}轮讨论。
                
                请：
                1. 指出观点分歧点
                2. 要求Agent解释其推理
                3. 寻找共识
                
                返回JSON：{{"consensus": "BUY/SELL/HOLD", "confidence": 0.85, "key_points": [...], "disagreements": [...]}}""",
                    ),
                    ("user", "当前观点：\n{opinions}\n\n历史讨论：\n{history}"),
                ]
            )

            chain = prompt | self.llm
            response = await chain.ainvoke(
                {
                    "round": round_num + 1,
                    "opinions": json.dumps(agents_results, ensure_ascii=False),
                    "history": json.dumps(discussion_history, ensure_ascii=False),
                }
            )

            discussion_history.append(
                {"round": round_num + 1, "summary": response.content}
            )

        # Final consensus
        final_result = self._extract_consensus(discussion_history)
        return self.format_output(
            final_result["signal"],
            final_result["confidence"],
            final_result["reasoning"],
        )

    def _extract_consensus(self, history: List[Dict]) -> Dict:
        if not history:
            return {"signal": "HOLD", "confidence": 0.5, "reasoning": "No discussion"}

        last_round = history[-1]["summary"]
        try:
            return json.loads(last_round)
        except:
            return {"signal": "HOLD", "confidence": 0.5, "reasoning": last_round}


class ReflectionAgent(BaseAgent):
    def __init__(self):
        super().__init__("ReflectionAgent", "gpt-4", 1.0)
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)

    async def reflect(
        self, signal_data: Dict, historical_performance: List[Dict]
    ) -> Dict[str, Any]:
        """基于历史表现进行反思和权重调整"""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """你是反思专家。分析当前决策和历史表现，提出改进建议。
            
            返回JSON：{{"adjusted_confidence": 0.75, "weight_adjustments": {{"agent_name": 0.6}}, "insights": "..."}}""",
                ),
                ("user", "当前决策：\n{signal}\n\n历史表现：\n{performance}"),
            ]
        )

        chain = prompt | self.llm
        response = await chain.ainvoke(
            {
                "signal": json.dumps(signal_data, ensure_ascii=False),
                "performance": json.dumps(historical_performance, ensure_ascii=False),
            }
        )

        return self._parse_response(response.content)

    def _parse_response(self, content: str) -> Dict:
        try:
            return json.loads(content)
        except:
            return {
                "adjusted_confidence": 0.5,
                "weight_adjustments": {},
                "insights": content,
            }
