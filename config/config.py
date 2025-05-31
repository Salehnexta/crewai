"""
Configuration settings for the CrewAI application
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the CrewAI application"""
    
    # API settings
    API_KEY = os.getenv("API_KEY", "default-development-key")
    PORT = int(os.getenv("PORT", "8000"))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    # LLM settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Tool settings
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Get LLM configuration settings"""
        return {
            "model": cls.OPENAI_MODEL,
            "temperature": cls.TEMPERATURE,
            "api_key": cls.OPENAI_API_KEY
        }
    
    @classmethod
    def load_from_file(cls, file_path: str) -> None:
        """Load configuration from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
                
            # Update environment variables with file values
            for key, value in config_data.items():
                os.environ[key] = str(value)
                
            # Reload environment variables
            load_dotenv()
            
        except Exception as e:
            print(f"Error loading configuration from {file_path}: {str(e)}")
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if the application is running in production mode"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
