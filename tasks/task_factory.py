"""
Task Factory for creating different types of CrewAI tasks
"""
from typing import Dict, List, Optional, Any
from crewai import Task, Agent

class TaskFactory:
    """Factory class for creating different types of CrewAI tasks"""
    
    def get_task(self, task_type: str, agent: Agent, context: Optional[List[Task]] = None, **kwargs) -> Task:
        """
        Create a task based on the specified type
        
        Args:
            task_type: Type of task to create
            agent: The agent assigned to this task
            context: Optional list of tasks that provide context to this task
            **kwargs: Additional arguments for task customization
        
        Returns:
            Task: A CrewAI Task instance
        """
        task_creators = {
            "research": self._create_research_task,
            "analysis": self._create_analysis_task,
            "writing": self._create_writing_task,
            "development": self._create_development_task,
            "review": self._create_review_task,
        }
        
        if task_type not in task_creators:
            raise ValueError(f"Task type '{task_type}' not supported")
        
        return task_creators[task_type](agent=agent, context=context, **kwargs)
    
    def _create_research_task(self, agent: Agent, context: Optional[List[Task]] = None, **kwargs) -> Task:
        """Create a research task for gathering information"""
        description = kwargs.get("description", 
            "Research and gather comprehensive information on the specified topic")
        expected_output = kwargs.get("expected_output", 
            "A detailed research report with key findings, facts, statistics, and relevant sources")
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            context=context if context else [],
            **{k: v for k, v in kwargs.items() if k not in ["description", "expected_output"]}
        )
    
    def _create_analysis_task(self, agent: Agent, context: Optional[List[Task]] = None, **kwargs) -> Task:
        """Create an analysis task for interpreting information"""
        description = kwargs.get("description", 
            "Analyze the provided information and extract key insights, patterns, and implications")
        expected_output = kwargs.get("expected_output", 
            "An analytical report with key insights, trends, and actionable recommendations")
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            context=context if context else [],
            **{k: v for k, v in kwargs.items() if k not in ["description", "expected_output"]}
        )
    
    def _create_writing_task(self, agent: Agent, context: Optional[List[Task]] = None, **kwargs) -> Task:
        """Create a writing task for content creation"""
        description = kwargs.get("description", 
            "Create well-structured, engaging content based on the provided information")
        expected_output = kwargs.get("expected_output", 
            "A well-written document that effectively communicates the key information and insights")
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            context=context if context else [],
            **{k: v for k, v in kwargs.items() if k not in ["description", "expected_output"]}
        )
    
    def _create_development_task(self, agent: Agent, context: Optional[List[Task]] = None, **kwargs) -> Task:
        """Create a development task for technical implementation"""
        description = kwargs.get("description", 
            "Develop code or technical solutions based on the provided specifications")
        expected_output = kwargs.get("expected_output", 
            "Well-documented, functional code or technical solution that meets the requirements")
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            context=context if context else [],
            **{k: v for k, v in kwargs.items() if k not in ["description", "expected_output"]}
        )
    
    def _create_review_task(self, agent: Agent, context: Optional[List[Task]] = None, **kwargs) -> Task:
        """Create a review task for quality assurance"""
        description = kwargs.get("description", 
            "Review and evaluate the provided content, identifying areas for improvement")
        expected_output = kwargs.get("expected_output", 
            "A detailed review with specific feedback, corrections, and suggestions for improvement")
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            context=context if context else [],
            **{k: v for k, v in kwargs.items() if k not in ["description", "expected_output"]}
        )
