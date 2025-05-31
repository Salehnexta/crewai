"""
Content Creation Crew - A crew of agents for researching and creating content
"""
from crewai import Agent, Crew, Task, Process
from agents.agent_factory import AgentFactory
from tasks.task_factory import TaskFactory

class ContentCreationCrew:
    """
    Content Creation Crew that assembles researcher and writer agents
    to produce high-quality content on specified topics
    """
    
    def __init__(self):
        """Initialize factories for creating agents and tasks"""
        self.agent_factory = AgentFactory()
        self.task_factory = TaskFactory()
    
    def researcher(self) -> Agent:
        """Create the researcher agent"""
        return self.agent_factory.get_agent("researcher")
    
    def writer(self) -> Agent:
        """Create the writer agent"""
        return self.agent_factory.get_agent("writer")
    
    def editor(self) -> Agent:
        """Create the editor agent (based on the analyst type)"""
        return self.agent_factory.get_agent(
            "analyst", 
            role="Content Editor",
            goal="Review and refine content to ensure it's engaging, accurate, and high-quality",
            backstory="""You are a skilled editor with years of experience in content 
            publishing. You have a keen eye for quality, clarity, and style. You can transform 
            good content into exceptional content through thoughtful revisions."""
        )
    
    def research_task(self) -> Task:
        """Create the research task"""
        return self.task_factory.get_task(
            task_type="research",
            agent=self.researcher(),
            description="Research thoroughly on the given topic, gathering key information, facts, statistics, and relevant sources",
            expected_output="A comprehensive research document with all relevant information organized by subtopics"
        )
    
    def writing_task(self) -> Task:
        """Create the writing task with research context"""
        return self.task_factory.get_task(
            task_type="writing",
            agent=self.writer(),
            context=[self.research_task()],
            description="Create a well-structured, engaging article based on the research findings",
            expected_output="A complete article with an engaging introduction, well-organized body, and conclusion"
        )
    
    def editing_task(self) -> Task:
        """Create the editing task with writing context"""
        return self.task_factory.get_task(
            task_type="review",
            agent=self.editor(),
            context=[self.writing_task()],
            description="Review and refine the article for clarity, engagement, accuracy, and overall quality",
            expected_output="A polished final article ready for publication"
        )
    
    def crew(self) -> Crew:
        """Assemble the content creation crew"""
        return Crew(
            agents=[self.researcher(), self.writer(), self.editor()],
            tasks=[self.research_task(), self.writing_task(), self.editing_task()],
            process=Process.sequential,
            verbose=True
        )
