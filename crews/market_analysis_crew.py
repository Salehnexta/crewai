"""
Market Analysis Crew - A crew of agents for market research and analysis
"""
from crewai import Agent, Crew, Task, Process
from agents.agent_factory import AgentFactory
from tasks.task_factory import TaskFactory

class MarketAnalysisCrew:
    """
    Market Analysis Crew that assembles researcher and analyst agents
    to conduct comprehensive market analysis on specified industries or topics
    """
    
    def __init__(self):
        """Initialize factories for creating agents and tasks"""
        self.agent_factory = AgentFactory()
        self.task_factory = TaskFactory()
    
    def researcher(self) -> Agent:
        """Create the market researcher agent"""
        return self.agent_factory.get_agent(
            "researcher",
            role="Market Research Specialist",
            goal="Gather comprehensive market data and insights on the specified industry or topic",
            backstory="""You are an expert market researcher with extensive experience
            in gathering market intelligence across various industries. You know how to
            find valuable data from both mainstream and specialized sources."""
        )
    
    def analyst(self) -> Agent:
        """Create the market analyst agent"""
        return self.agent_factory.get_agent(
            "analyst",
            role="Market Analyst",
            goal="Analyze market data to identify trends, opportunities, and strategic insights",
            backstory="""You are a skilled market analyst with a background in economics and
            business strategy. You excel at interpreting data, identifying patterns, and
            extracting actionable insights for business decision-making."""
        )
    
    def strategist(self) -> Agent:
        """Create the market strategist agent"""
        return self.agent_factory.get_agent(
            "manager",
            role="Strategic Advisor",
            goal="Develop strategic recommendations based on market analysis",
            backstory="""You are a strategic advisor with years of experience helping
            businesses leverage market opportunities. You can translate analytical findings
            into practical, actionable recommendations that drive business success."""
        )
    
    def research_task(self) -> Task:
        """Create the market research task"""
        return self.task_factory.get_task(
            task_type="research",
            agent=self.researcher(),
            description="""Research the current market landscape for the specified industry or topic.
            Gather data on market size, growth rate, key players, market shares, consumer trends,
            regulatory factors, and emerging opportunities/threats.""",
            expected_output="""A comprehensive market research report with detailed data on market size,
            growth projections, competitive landscape, consumer behavior, and external factors."""
        )
    
    def analysis_task(self) -> Task:
        """Create the market analysis task with research context"""
        return self.task_factory.get_task(
            task_type="analysis",
            agent=self.analyst(),
            context=[self.research_task()],
            description="""Analyze the market research data to identify key trends, patterns,
            opportunities, and challenges. Evaluate competitive positioning and market dynamics.""",
            expected_output="""An analytical report with identified market trends, competitive analysis,
            SWOT assessment, and key factors driving market evolution."""
        )
    
    def strategy_task(self) -> Task:
        """Create the strategy development task with analysis context"""
        return self.task_factory.get_task(
            task_type="writing",
            agent=self.strategist(),
            context=[self.research_task(), self.analysis_task()],
            description="""Develop strategic recommendations based on the market research and analysis.
            Focus on actionable insights that can drive business decisions and create competitive advantage.""",
            expected_output="""A strategic advisory report with prioritized recommendations,
            implementation considerations, potential risks, and expected outcomes."""
        )
    
    def crew(self) -> Crew:
        """Assemble the market analysis crew"""
        return Crew(
            agents=[self.researcher(), self.analyst(), self.strategist()],
            tasks=[self.research_task(), self.analysis_task(), self.strategy_task()],
            process=Process.sequential,
            verbose=True
        )
