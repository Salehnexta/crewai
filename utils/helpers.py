"""
Helper utilities for the CrewAI application
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_result(result: str, output_dir: str = "outputs", filename: Optional[str] = None) -> str:
    """
    Save agent results to a file
    
    Args:
        result: The content to save
        output_dir: Directory to save the file in
        filename: Optional filename, defaults to timestamp-based name
        
    Returns:
        Path to the saved file
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a filename based on timestamp if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"result_{timestamp}.txt"
    
    # Ensure the filename has a .txt extension
    if not filename.endswith('.txt'):
        filename += '.txt'
    
    # Full path to the file
    file_path = os.path.join(output_dir, filename)
    
    # Save the content to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(result)
    
    logger.info(f"Result saved to {file_path}")
    return file_path

def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON content as a dictionary
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {str(e)}")
        return {}

def create_execution_log(crew_type: str, inputs: Dict[str, Any], result: str) -> Dict[str, Any]:
    """
    Create an execution log entry for monitoring and analytics
    
    Args:
        crew_type: Type of crew executed
        inputs: Input parameters provided to the crew
        result: Execution result
        
    Returns:
        Log entry as a dictionary
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "crew_type": crew_type,
        "inputs": inputs,
        "result_length": len(result),
        "status": "success"
    }

def chunk_text(text: str, chunk_size: int = 8000) -> List[str]:
    """
    Split long text into smaller chunks for processing
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        
    Returns:
        List of text chunks
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
