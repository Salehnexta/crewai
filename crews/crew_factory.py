"""
Crew Factory for creating different types of CrewAI crews
"""
from typing import Dict, List, Optional, Any
from crewai import Crew, Process

from crews.content_creation_crew import ContentCreationCrew
from crews.market_analysis_crew import MarketAnalysisCrew
from crews.tech_development_crew import TechDevelopmentCrew

class CrewFactory:
    """Factory class for creating different types of CrewAI crews"""
    
    def get_crew(self, crew_type: str, **kwargs) -> Crew:
        """
        Create a crew based on the specified type
        
        Args:
            crew_type: Type of crew to create
            **kwargs: Additional arguments for crew customization
        
        Returns:
            Crew: A CrewAI Crew instance
        """
        crew_creators = {
            "content_creation": self._create_content_creation_crew,
            "market_analysis": self._create_market_analysis_crew,
            "tech_development": self._create_tech_development_crew,
        }
        
        if crew_type not in crew_creators:
            raise ValueError(f"Crew type '{crew_type}' not supported")
        
        return crew_creators[crew_type](**kwargs)
    
    def _create_content_creation_crew(self, **kwargs) -> Crew:
        """Create a content creation crew instance"""
        content_crew = ContentCreationCrew()
        return content_crew.crew()
    
    def _create_market_analysis_crew(self, **kwargs) -> Crew:
        """Create a market analysis crew instance"""
        market_crew = MarketAnalysisCrew()
        return market_crew.crew()
    
    def _create_tech_development_crew(self, **kwargs) -> Crew:
        """Create a technical development crew instance"""
        tech_crew = TechDevelopmentCrew()
        return tech_crew.crew()
