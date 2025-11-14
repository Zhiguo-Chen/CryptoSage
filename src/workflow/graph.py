from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from ..agents.technical_agents import TechAgentOpenAI, TechAgentGemini
from ..agents.news_agents import NewsAgentOpenAI, NewsAgentGemini, RAGAgent
from ..agents.consensus_agents import TechConsensusAgent, NewsConsensusAgent
from ..agents.decision_agents import DecisionAgent, DiscussionAgent, ReflectionAgent


class AgentState(TypedDict):
    prices: List[Dict]
    news: List[Dict]
    tech_results: List[Dict]
    news_results: List[Dict]
    tech_consensus: Dict
    news_consensus: Dict
    initial_decision: Dict
    discussion_result: Dict
    reflection: Dict
    final_signal: Dict


class BTCAgentWorkflow:
    def __init__(self):
        self.tech_agents = [TechAgentOpenAI(), TechAgentGemini()]
        self.news_agents = [NewsAgentOpenAI(), NewsAgentGemini(), RAGAgent()]
        self.tech_consensus = TechConsensusAgent()
        self.news_consensus = NewsConsensusAgent()
        self.decision_agent = DecisionAgent()
        self.discussion_agent = DiscussionAgent()
        self.reflection_agent = ReflectionAgent()

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("technical_analysis", self._technical_analysis)
        workflow.add_node("news_analysis", self._news_analysis)
        workflow.add_node("tech_consensus", self._tech_consensus)
        workflow.add_node("news_consensus", self._news_consensus)
        workflow.add_node("decision", self._decision)
        workflow.add_node("discussion", self._discussion)
        workflow.add_node("reflection", self._reflection)

        # 定义流程
        workflow.set_entry_point("technical_analysis")
        workflow.add_edge("technical_analysis", "tech_consensus")
        workflow.add_edge("news_analysis", "news_consensus")
        workflow.add_edge("tech_consensus", "decision")
        workflow.add_edge("news_consensus", "decision")
        workflow.add_edge("decision", "discussion")
        workflow.add_edge("discussion", "reflection")
        workflow.add_edge("reflection", END)

        # 并行执行技术和新闻分析
        workflow.set_entry_point("technical_analysis")
        workflow.add_edge("technical_analysis", "news_analysis")

        return workflow.compile()

    async def _technical_analysis(self, state: AgentState) -> AgentState:
        """并行执行技术分析"""
        results = []
        for agent in self.tech_agents:
            result = await agent.analyze({"prices": state["prices"]})
            results.append(result)
        state["tech_results"] = results
        return state

    async def _news_analysis(self, state: AgentState) -> AgentState:
        """并行执行新闻分析"""
        results = []
        for agent in self.news_agents:
            result = await agent.analyze({"news": state["news"]})
            results.append(result)
        state["news_results"] = results
        return state

    async def _tech_consensus(self, state: AgentState) -> AgentState:
        """技术面共识"""
        result = await self.tech_consensus.analyze(
            {"tech_results": state["tech_results"]}
        )
        state["tech_consensus"] = result
        return state

    async def _news_consensus(self, state: AgentState) -> AgentState:
        """新闻面共识"""
        result = await self.news_consensus.analyze(
            {"news_results": state["news_results"]}
        )
        state["news_consensus"] = result
        return state

    async def _decision(self, state: AgentState) -> AgentState:
        """初步决策"""
        result = await self.decision_agent.analyze(
            {
                "technical_analysis": [state["tech_consensus"]],
                "news_analysis": [state["news_consensus"]],
            }
        )
        state["initial_decision"] = result
        return state

    async def _discussion(self, state: AgentState) -> AgentState:
        """多Agent讨论"""
        all_results = state["tech_results"] + state["news_results"]
        result = await self.discussion_agent.moderate_discussion(all_results, rounds=3)
        state["discussion_result"] = result
        return state

    async def _reflection(self, state: AgentState) -> AgentState:
        """反思与学习"""
        result = await self.reflection_agent.reflect(
            state["discussion_result"], []  # 历史表现数据
        )
        state["reflection"] = result
        state["final_signal"] = state["discussion_result"]
        return state

    async def run(self, prices: List[Dict], news: List[Dict]) -> Dict[str, Any]:
        """执行完整工作流"""
        initial_state = AgentState(
            prices=prices,
            news=news,
            tech_results=[],
            news_results=[],
            tech_consensus={},
            news_consensus={},
            initial_decision={},
            discussion_result={},
            reflection={},
            final_signal={},
        )

        final_state = await self.graph.ainvoke(initial_state)
        return final_state["final_signal"]
