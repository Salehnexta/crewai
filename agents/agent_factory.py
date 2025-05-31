"""
Agent Factory for creating different types of CrewAI agents
"""
from typing import Dict, List, Optional, Any
from crewai import Agent
from crewai_tools import SerperDevTool, WebsiteSearchTool, DirectoryReadTool, FileReadTool

class AgentFactory:
    """Factory class for creating different types of CrewAI agents"""
    
    def __init__(self):
        """Initialize with common tools that can be used by agents"""
        self.common_tools = {
            "search": SerperDevTool(),
            "website": WebsiteSearchTool(),
            "directory": DirectoryReadTool(),
            "file": FileReadTool()
        }
    
    def get_agent(self, agent_type: str, **kwargs) -> Agent:
        """
        Create an agent based on the specified type
        
        Args:
            agent_type: Type of agent to create
            **kwargs: Additional arguments for agent customization
        
        Returns:
            Agent: A CrewAI Agent instance
        """
        agent_creators = {
            "researcher": self._create_researcher_agent,
            "writer": self._create_writer_agent,
            "analyst": self._create_analyst_agent,
            "developer": self._create_developer_agent,
            "manager": self._create_manager_agent,
        }
        
        if agent_type not in agent_creators:
            raise ValueError(f"Agent type '{agent_type}' not supported")
        
        return agent_creators[agent_type](**kwargs)
    
    def _create_researcher_agent(self, **kwargs) -> Agent:
        """Create a researcher agent specialized in information gathering"""
        return Agent(
            role="Research Specialist",
            goal="Find and provide the most accurate and comprehensive information on the given topic",
            backstory="""You are an expert researcher with a background in gathering information 
            from diverse sources. You have a keen eye for detail and can distinguish between 
            credible and non-credible information. You pride yourself on thoroughness.""",
            verbose=True,
            tools=[self.common_tools["search"], self.common_tools["website"]],
            **kwargs
        )
    
    def _create_writer_agent(self, **kwargs) -> Agent:
        """Create a writer agent specialized in content creation"""
        return Agent(
            role="Content Writer",
            goal="Create engaging, accurate, and well-structured content based on research findings",
            backstory="""You are a talented writer with years of experience creating various 
            types of content. You can adapt your writing style to different audiences and purposes, 
            ensuring the message is clear and compelling.""",
            verbose=True,
            tools=[self.common_tools["file"]],
            **kwargs
        )
    
    def _create_analyst_agent(self, **kwargs) -> Agent:
        """Create an analyst agent specialized in data analysis"""
        return Agent(
            role="Data Analyst",
            goal="Analyze information and data to extract meaningful insights and patterns",
            backstory="""You are a data analyst with a strong background in statistics and 
            data interpretation. You can take raw information and transform it into valuable 
            insights that inform decision-making.""",
            verbose=True,
            tools=[self.common_tools["search"]],
            **kwargs
        )
    
    def _create_developer_agent(self, **kwargs) -> Agent:
        """Create a developer agent specialized in code and technical solutions"""
        return Agent(
            role="Technical Developer",
            goal="Develop and explain technical solutions, code, and implementation details",
            backstory="""You are an experienced developer with expertise in multiple programming 
            languages and technical frameworks. You can create efficient, well-documented code 
            and explain complex technical concepts in accessible terms.""",
            verbose=True,
            tools=[self.common_tools["directory"], self.common_tools["file"]],
            **kwargs
        )
    
    def _create_manager_agent(self, **kwargs) -> Agent:
        """Create a manager agent specialized in coordination and oversight"""
        return Agent(
            role="Project Manager",
            goal="Coordinate the work of other agents, ensure quality, and deliver final results",
            backstory="""You are a skilled project manager with experience leading teams to 
            successful outcomes. You excel at planning, coordination, and quality control, 
            ensuring all elements come together cohesively.""",
            verbose=True,
            tools=[],
            **kwargs
        )
