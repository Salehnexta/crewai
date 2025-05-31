"""
Tech Development Crew - A crew of agents for technical planning and implementation
"""
from crewai import Agent, Crew, Task, Process
from agents.agent_factory import AgentFactory
from tasks.task_factory import TaskFactory

class TechDevelopmentCrew:
    """
    Tech Development Crew that assembles technical agents
    to plan, develop, and evaluate technical solutions
    """
    
    def __init__(self):
        """Initialize factories for creating agents and tasks"""
        self.agent_factory = AgentFactory()
        self.task_factory = TaskFactory()
    
    def architect(self) -> Agent:
        """Create the solution architect agent"""
        return self.agent_factory.get_agent(
            "analyst",
            role="Solution Architect",
            goal="Design scalable, efficient technical architectures and solutions",
            backstory="""You are an experienced solution architect with expertise in 
            designing complex systems. You understand how to balance technical requirements, 
            scalability needs, and business constraints to create optimal system designs."""
        )
    
    def developer(self) -> Agent:
        """Create the developer agent"""
        return self.agent_factory.get_agent(
            "developer",
            role="Senior Developer",
            goal="Implement robust, efficient code and technical solutions based on specifications",
            backstory="""You are a senior developer with expertise across multiple programming 
            languages and frameworks. You write clean, well-documented code and know how to 
            implement solutions that are both functional and maintainable."""
        )
    
    def tester(self) -> Agent:
        """Create the QA engineer agent"""
        return self.agent_factory.get_agent(
            "analyst",
            role="QA Engineer",
            goal="Thoroughly test and validate technical implementations to ensure quality",
            backstory="""You are a detail-oriented QA engineer with a strong background in 
            testing methodologies. You know how to identify edge cases, performance issues, 
            and potential bugs to ensure high-quality deliverables."""
        )
    
    def architecture_task(self) -> Task:
        """Create the architecture design task"""
        return self.task_factory.get_task(
            task_type="analysis",
            agent=self.architect(),
            description="""Design a comprehensive technical architecture for the specified solution.
            Consider scalability, performance, security, and maintainability. Identify key components,
            their interactions, and technology choices.""",
            expected_output="""A detailed architecture document including component diagrams,
            technology stack recommendations, data flow descriptions, and implementation considerations."""
        )
    
    def development_task(self) -> Task:
        """Create the development task with architecture context"""
        return self.task_factory.get_task(
            task_type="development",
            agent=self.developer(),
            context=[self.architecture_task()],
            description="""Implement the technical solution based on the architecture design.
            Write clean, efficient code with proper error handling, logging, and documentation.""",
            expected_output="""Functional code implementation with documentation, installation
            instructions, and examples of usage."""
        )
    
    def testing_task(self) -> Task:
        """Create the testing task with development context"""
        return self.task_factory.get_task(
            task_type="review",
            agent=self.tester(),
            context=[self.architecture_task(), self.development_task()],
            description="""Test the implemented solution against requirements and best practices.
            Identify any bugs, performance issues, or areas for improvement.""",
            expected_output="""A comprehensive test report with findings, recommendations for
            improvements, and validation of the solution's functionality."""
        )
    
    def crew(self) -> Crew:
        """Assemble the tech development crew"""
        return Crew(
            agents=[self.architect(), self.developer(), self.tester()],
            tasks=[self.architecture_task(), self.development_task(), self.testing_task()],
            process=Process.sequential,
            verbose=True
        )
