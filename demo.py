"""
Demo script to showcase the CrewAI API functionality
This script starts the FastAPI server and sends a test request
"""
import os
import json
import time
import subprocess
import requests
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_server():
    """Start the FastAPI server"""
    print("Starting FastAPI server...")
    server_process = subprocess.Popen(
        ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give the server time to start
    time.sleep(3)
    return server_process

def test_api():
    """Test the CrewAI API endpoints"""
    # Define the API key
    api_key = os.getenv("API_KEY", "default-development-key")
    
    # Test health endpoint
    print("\nTesting health endpoint...")
    try:
        health_response = requests.get(
            "http://localhost:8000/health",
            headers={"X-API-Key": api_key}
        )
        print(f"Health check status: {health_response.status_code}")
        print(f"Response: {health_response.json()}")
    except Exception as e:
        print(f"Error testing health endpoint: {str(e)}")
    
    # Test crew endpoint
    print("\nTesting crew endpoint with content creation crew...")
    try:
        crew_data = {
            "crew_type": "content_creation",
            "inputs": {
                "topic": "Artificial Intelligence in Modern Healthcare",
                "target_audience": "Healthcare Professionals",
                "content_type": "Blog Post"
            },
            "metadata": {
                "user_id": "demo_user",
                "project_id": "demo_project"
            }
        }
        
        print(f"Sending request: {json.dumps(crew_data, indent=2)}")
        
        crew_response = requests.post(
            "http://localhost:8000/crew",
            headers={"X-API-Key": api_key},
            json=crew_data
        )
        
        print(f"Crew endpoint status: {crew_response.status_code}")
        
        if crew_response.status_code == 200:
            result = crew_response.json()
            print("\nResult preview (first 500 chars):")
            print(f"{result['result'][:500]}...")
            print("\nExecution time: {:.2f} seconds".format(result.get('execution_time', 0)))
        else:
            print(f"Error response: {crew_response.text}")
    
    except Exception as e:
        print(f"Error testing crew endpoint: {str(e)}")

def main():
    """Main function to run the demo"""
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set")
        print("Please set this in your .env file before running the demo")
        return
    
    # Start the server in a separate thread
    server_process = start_server()
    
    try:
        # Test the API
        test_api()
        
        print("\nDemo completed! Press Ctrl+C to exit.")
        
        # Keep the server running until user interrupts
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up the server process
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    main()
