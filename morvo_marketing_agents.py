"""
Morvo AI Marketing Platform - M1-M5 Specialized Marketing Agents

This module defines the five specialized marketing agents (M1-M5) and their CrewAI implementations
for the Morvo AI Marketing Platform.

Each agent has a specific role in the marketing ecosystem:
- M1: Strategic Analysis
- M2: Social Media Monitoring
- M3: Campaign Optimization
- M4: Content Strategy
- M5: Data Analytics
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

# Initialize CrewAI
from crewai import Agent, Task, Crew, Process
from crewai.task import TaskOutput
from crewai_tools import SerperDevTool

# Import SEMrush integration
from semrush_supabase_integration import get_semrush_supabase_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("morvo_marketing_agents")

# Define agent roles
M1_ROLE = """
You are M1, the Strategic Analysis Agent for the Morvo AI Marketing Platform.
You specialize in comprehensive market analysis, competitive intelligence, and strategic recommendations.
Your insights drive high-level marketing strategy and business positioning decisions.
"""

M2_ROLE = """
You are M2, the Social Media Monitoring Agent for the Morvo AI Marketing Platform.
You track, analyze, and interpret social media trends, brand mentions, and engagement metrics.
Your insights help organizations understand their social presence and audience engagement.
"""

M3_ROLE = """
You are M3, the Campaign Optimization Agent for the Morvo AI Marketing Platform.
You analyze marketing campaign performance, optimize ad spend, and improve conversion metrics.
Your goal is to maximize ROI and efficiency across marketing campaigns.
"""

M4_ROLE = """
You are M4, the Content Strategy Agent for the Morvo AI Marketing Platform.
You develop comprehensive content strategies, identify content gaps, and create content plans.
Your expertise ensures content aligns with business goals and audience needs.
"""

M5_ROLE = """
You are M5, the Data Analytics Agent for the Morvo AI Marketing Platform.
You transform marketing data into actionable insights through advanced analytics and visualization.
Your analysis drives data-backed decision making across all marketing functions.
"""

# Define agent prompts
M1_PROMPT_TEMPLATE = """
Analyze {domain} with these objectives:
1. Identify key market positioning and competitive landscape
2. Evaluate SEO strengths and weaknesses using SEMrush data
3. Discover market gaps and strategic opportunities
4. Analyze top competitors {competitors} for their strategies
5. Recommend strategic pivots and positioning improvements

Additional context: {context}
Keywords to analyze: {keywords}

Provide structured analysis with:
- Executive Summary (3-5 bullet points)
- Market Position Analysis
- Competitive Intelligence
- SEO/SEM Opportunity Assessment
- Strategic Recommendations (actionable steps)

Be data-driven, strategic, and business-focused in your analysis.
"""

M2_PROMPT_TEMPLATE = """
Monitor social media for {brand} with these objectives:
1. Track brand mentions and sentiment across platforms
2. Analyze engagement metrics and trends
3. Identify viral content opportunities and trending topics
4. Compare social performance against {competitors}
5. Detect potential PR issues or reputation threats

Time period: {time_period}
Platforms to analyze: {platforms}
Focus keywords: {keywords}

Provide structured analysis with:
- Social Listening Summary
- Engagement Metrics Analysis
- Content Performance Report
- Competitor Social Comparison
- Actionable Social Media Recommendations

Be data-driven while understanding social context and audience psychology.
"""

M3_PROMPT_TEMPLATE = """
Optimize campaigns for {brand} with these objectives:
1. Analyze performance of current campaigns: {campaigns}
2. Identify underperforming channels and content
3. Recommend budget reallocation for optimal ROI
4. Suggest A/B testing opportunities
5. Provide conversion rate optimization tactics

Campaign data: {campaign_data}
Budget constraints: {budget}
KPIs: {kpis}

Provide structured optimization plan with:
- Performance Analysis Summary
- Channel Effectiveness Breakdown
- Budget Allocation Recommendations
- Creative and Copy Improvement Suggestions
- Technical Implementation Steps

Be data-driven, results-focused, and provide specific actionable recommendations.
"""

M4_PROMPT_TEMPLATE = """
Develop a content strategy for {brand} with these objectives:
1. Audit existing content and identify gaps: {existing_content}
2. Research keyword opportunities based on SEMrush data
3. Create a content calendar for {time_period}
4. Outline key content themes and formats
5. Define content distribution and promotion channels

Target audience: {audience}
Content goals: {goals}
Key competitors: {competitors}

Provide structured content strategy with:
- Content Audit Summary
- Keyword and Topic Research
- Content Calendar (key dates/themes)
- Content Format Recommendations
- Distribution Strategy

Be creative yet strategic, focusing on both search performance and audience engagement.
"""

M5_PROMPT_TEMPLATE = """
Analyze marketing data for {brand} with these objectives:
1. Process and clean marketing dataset: {dataset}
2. Identify key performance trends and anomalies
3. Create attribution modeling across channels
4. Generate predictive insights for future performance
5. Visualize data into actionable dashboards/reports

Analysis period: {time_period}
Key metrics: {metrics}
Required segmentation: {segments}

Provide structured analytics report with:
- Executive Dashboard Summary
- Channel Performance Analysis
- Conversion Funnel Visualization
- Audience Segmentation Insights
- Predictive Trends and Recommendations

Be technically precise while making insights accessible to non-technical stakeholders.
"""

# Optional tools setup
def get_search_tool():
    """Get search tool if API key is available, otherwise return None."""
    serper_api_key = os.getenv("SERPER_API_KEY")
    if serper_api_key:
        return SerperDevTool(api_key=serper_api_key)
    logger.warning("SERPER_API_KEY not found, search tool will not be available")
    return None

# Custom SEMrush tool
class SEMrushTool:
    """Tool for accessing SEMrush data (real or mock)."""
    
    def __init__(self):
        """Initialize the SEMrush tool."""
        self.manager = get_semrush_supabase_manager()
    
    async def get_domain_overview(self, domain: str) -> Dict:
        """Get domain overview data from SEMrush."""
        return await self.manager.get_domain_data(domain)
    
    async def get_keyword_data(self, keyword: str) -> Dict:
        """Get keyword data from SEMrush."""
        return await self.manager.get_keyword_data(keyword)
    
    def domain_analysis(self, domain: str) -> str:
        """Synchronous wrapper for domain analysis."""
        data = asyncio.run(self.get_domain_overview(domain))
        return json.dumps(data, indent=2)
    
    def keyword_analysis(self, keyword: str) -> str:
        """Synchronous wrapper for keyword analysis."""
        data = asyncio.run(self.get_keyword_data(keyword))
        return json.dumps(data, indent=2)

# Function to create agents
def create_marketing_agents(model_name=None):
    """
    Create the M1-M5 marketing agents.
    
    Args:
        model_name: Optional model name to use for agents
    
    Returns:
        Dictionary of agents
    """
    # Use environment variable or default if model not specified
    model = model_name or os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
    
    # Set up tools
    search_tool = get_search_tool()
    semrush_tool = SEMrushTool()
    
    # Define agent tools
    m1_tools = []
    if search_tool:
        m1_tools.append(search_tool)
    
    # Create the agents
    m1_agent = Agent(
        role="Strategic Analysis Agent",
        goal="Provide comprehensive market and competitor analysis with strategic recommendations",
        backstory=M1_ROLE,
        verbose=True,
        allow_delegation=True,
        tools=m1_tools,
        llm=model
    )
    
    m2_agent = Agent(
        role="Social Media Monitoring Agent",
        goal="Track and analyze social media presence, engagement, and sentiment",
        backstory=M2_ROLE,
        verbose=True,
        allow_delegation=True,
        tools=[search_tool] if search_tool else [],
        llm=model
    )
    
    m3_agent = Agent(
        role="Campaign Optimization Agent",
        goal="Maximize marketing campaign ROI through data-driven optimization",
        backstory=M3_ROLE,
        verbose=True,
        allow_delegation=True,
        tools=[search_tool] if search_tool else [],
        llm=model
    )
    
    m4_agent = Agent(
        role="Content Strategy Agent",
        goal="Develop effective content strategies aligned with business goals and audience needs",
        backstory=M4_ROLE,
        verbose=True,
        allow_delegation=True,
        tools=[search_tool] if search_tool else [],
        llm=model
    )
    
    m5_agent = Agent(
        role="Data Analytics Agent",
        goal="Transform marketing data into actionable insights and visualizations",
        backstory=M5_ROLE,
        verbose=True,
        allow_delegation=True,
        tools=[search_tool] if search_tool else [],
        llm=model
    )
    
    return {
        "m1": m1_agent,
        "m2": m2_agent,
        "m3": m3_agent,
        "m4": m4_agent,
        "m5": m5_agent
    }

# Function to create marketing crews
def create_marketing_crews(agents):
    """
    Create specialized marketing crews from the agents.
    
    Args:
        agents: Dictionary of agents
        
    Returns:
        Dictionary of crews
    """
    # Market Analysis Crew (M1 + M5)
    market_analysis_crew = Crew(
        agents=[agents["m1"], agents["m5"]],
        tasks=[],  # Tasks will be added dynamically
        verbose=True,
        process=Process.sequential  # Sequential process for analysis workflow
    )
    
    # Content & Social Crew (M2 + M4)
    content_social_crew = Crew(
        agents=[agents["m2"], agents["m4"]],
        tasks=[],  # Tasks will be added dynamically
        verbose=True,
        process=Process.sequential
    )
    
    # Campaign Execution Crew (M3 + M2 + M5)
    campaign_execution_crew = Crew(
        agents=[agents["m3"], agents["m2"], agents["m5"]],
        tasks=[],  # Tasks will be added dynamically
        verbose=True,
        process=Process.sequential
    )
    
    # Complete Marketing Automation (All M1-M5)
    complete_marketing_crew = Crew(
        agents=list(agents.values()),
        tasks=[],  # Tasks will be added dynamically
        verbose=True,
        process=Process.sequential
    )
    
    return {
        "market_analysis": market_analysis_crew,
        "content_social": content_social_crew,
        "campaign_execution": campaign_execution_crew,
        "complete_marketing": complete_marketing_crew
    }

# Helper function to create a strategic analysis task
def create_strategic_analysis_task(agent, domain, competitors=None, keywords=None, context=None):
    """Create a strategic analysis task for M1 agent."""
    competitors_str = ", ".join(competitors) if competitors else "None provided"
    keywords_str = ", ".join(keywords) if keywords else "None provided"
    context_str = context or "No additional context provided"
    
    prompt = M1_PROMPT_TEMPLATE.format(
        domain=domain,
        competitors=competitors_str,
        keywords=keywords_str,
        context=context_str
    )
    
    return Task(
        description=f"Perform strategic analysis for {domain}",
        expected_output="Comprehensive strategic analysis with recommendations",
        agent=agent,
        async_execution=False,
        context=[prompt]
    )

# Helper function to create a social media monitoring task
def create_social_monitoring_task(agent, brand, platforms=None, time_period=None, competitors=None, keywords=None):
    """Create a social media monitoring task for M2 agent."""
    platforms_str = ", ".join(platforms) if platforms else "All major platforms"
    competitors_str = ", ".join(competitors) if competitors else "None provided"
    keywords_str = ", ".join(keywords) if keywords else "None provided"
    time_period_str = time_period or "Last 30 days"
    
    prompt = M2_PROMPT_TEMPLATE.format(
        brand=brand,
        platforms=platforms_str,
        time_period=time_period_str,
        competitors=competitors_str,
        keywords=keywords_str
    )
    
    return Task(
        description=f"Monitor social media for {brand}",
        expected_output="Social media analysis report with recommendations",
        agent=agent,
        async_execution=False,
        context=[prompt]
    )

# Similar helper functions for other agent tasks
def create_campaign_optimization_task(agent, brand, campaigns=None, campaign_data=None, budget=None, kpis=None):
    """Create a campaign optimization task for M3 agent."""
    campaigns_str = ", ".join(campaigns) if campaigns else "All active campaigns"
    campaign_data_str = campaign_data or "Use available campaign data"
    budget_str = budget or "Current budget allocation"
    kpis_str = ", ".join(kpis) if kpis else "ROAS, CPA, CTR, Conversion Rate"
    
    prompt = M3_PROMPT_TEMPLATE.format(
        brand=brand,
        campaigns=campaigns_str,
        campaign_data=campaign_data_str,
        budget=budget_str,
        kpis=kpis_str
    )
    
    return Task(
        description=f"Optimize marketing campaigns for {brand}",
        expected_output="Campaign optimization plan with recommendations",
        agent=agent,
        async_execution=False,
        context=[prompt]
    )

def create_content_strategy_task(agent, brand, audience=None, goals=None, competitors=None, existing_content=None, time_period=None):
    """Create a content strategy task for M4 agent."""
    audience_str = audience or "Target audience not specified"
    goals_str = ", ".join(goals) if goals else "Increase engagement and conversions"
    competitors_str = ", ".join(competitors) if competitors else "None provided"
    existing_content_str = existing_content or "Review current website and social content"
    time_period_str = time_period or "Next 3 months"
    
    prompt = M4_PROMPT_TEMPLATE.format(
        brand=brand,
        audience=audience_str,
        goals=goals_str,
        competitors=competitors_str,
        existing_content=existing_content_str,
        time_period=time_period_str
    )
    
    return Task(
        description=f"Develop content strategy for {brand}",
        expected_output="Comprehensive content strategy with calendar",
        agent=agent,
        async_execution=False,
        context=[prompt]
    )

def create_data_analytics_task(agent, brand, dataset=None, time_period=None, metrics=None, segments=None):
    """Create a data analytics task for M5 agent."""
    dataset_str = dataset or "Available marketing data"
    time_period_str = time_period or "Last 6 months"
    metrics_str = ", ".join(metrics) if metrics else "Conversions, Revenue, ROAS, CAC, LTV"
    segments_str = ", ".join(segments) if segments else "Channel, Campaign, Demographics, Device"
    
    prompt = M5_PROMPT_TEMPLATE.format(
        brand=brand,
        dataset=dataset_str,
        time_period=time_period_str,
        metrics=metrics_str,
        segments=segments_str
    )
    
    return Task(
        description=f"Analyze marketing data for {brand}",
        expected_output="Marketing analytics report with visualizations",
        agent=agent,
        async_execution=False,
        context=[prompt]
    )

# Function to run a single agent task
async def run_agent_task(agent_type, **kwargs):
    """
    Run a single agent task.
    
    Args:
        agent_type: The type of agent (m1, m2, m3, m4, m5)
        **kwargs: Parameters for the specific task
    
    Returns:
        Task output
    """
    agents = create_marketing_agents()
    
    if agent_type == "m1":
        task = create_strategic_analysis_task(agents["m1"], **kwargs)
    elif agent_type == "m2":
        task = create_social_monitoring_task(agents["m2"], **kwargs)
    elif agent_type == "m3":
        task = create_campaign_optimization_task(agents["m3"], **kwargs)
    elif agent_type == "m4":
        task = create_content_strategy_task(agents["m4"], **kwargs)
    elif agent_type == "m5":
        task = create_data_analytics_task(agents["m5"], **kwargs)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    # Create a simple crew with just this agent and task
    crew = Crew(
        agents=[agents[agent_type]],
        tasks=[task],
        verbose=True,
        process=Process.sequential
    )
    
    # Run the crew and return results
    result = crew.kickoff()
    
    # Format result for API response
    return {
        "agent": agent_type,
        "timestamp": datetime.now().isoformat(),
        "result": result,
        "task_type": task.description
    }

# Function to run a crew workflow
async def run_crew_workflow(crew_type, **kwargs):
    """
    Run a marketing crew workflow.
    
    Args:
        crew_type: The type of crew (market_analysis, content_social, campaign_execution, complete_marketing)
        **kwargs: Parameters for the tasks
    
    Returns:
        Crew output
    """
    agents = create_marketing_agents()
    crews = create_marketing_crews(agents)
    
    if crew_type not in crews:
        raise ValueError(f"Unknown crew type: {crew_type}")
    
    crew = crews[crew_type]
    
    # Add appropriate tasks based on crew type
    if crew_type == "market_analysis":
        crew.tasks = [
            create_strategic_analysis_task(agents["m1"], **kwargs),
            create_data_analytics_task(agents["m5"], **kwargs)
        ]
    elif crew_type == "content_social":
        crew.tasks = [
            create_social_monitoring_task(agents["m2"], **kwargs),
            create_content_strategy_task(agents["m4"], **kwargs)
        ]
    elif crew_type == "campaign_execution":
        crew.tasks = [
            create_campaign_optimization_task(agents["m3"], **kwargs),
            create_social_monitoring_task(agents["m2"], **kwargs),
            create_data_analytics_task(agents["m5"], **kwargs)
        ]
    elif crew_type == "complete_marketing":
        crew.tasks = [
            create_strategic_analysis_task(agents["m1"], **kwargs),
            create_social_monitoring_task(agents["m2"], **kwargs),
            create_campaign_optimization_task(agents["m3"], **kwargs),
            create_content_strategy_task(agents["m4"], **kwargs),
            create_data_analytics_task(agents["m5"], **kwargs)
        ]
    
    # Run the crew and return results
    result = crew.kickoff()
    
    # Format result for API response
    return {
        "crew": crew_type,
        "timestamp": datetime.now().isoformat(),
        "agents_involved": [agent.role for agent in crew.agents],
        "result": result
    }

if __name__ == "__main__":
    # Test code
    import asyncio
    
    async def test_agents():
        # Test a single agent
        result = await run_agent_task(
            "m1",
            domain="example.com",
            competitors=["competitor1.com", "competitor2.com"],
            keywords=["digital marketing", "marketing automation"]
        )
        print(json.dumps(result, indent=2))
        
        # Test a crew
        crew_result = await run_crew_workflow(
            "market_analysis",
            domain="example.com",
            competitors=["competitor1.com", "competitor2.com"],
            keywords=["digital marketing", "marketing automation"]
        )
        print(json.dumps(crew_result, indent=2))
    
    asyncio.run(test_agents())
