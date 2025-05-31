"""
Test script for the CrewAI application
Run this script to test a crew locally before deployment
"""
import os
import argparse
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool, WebsiteSearchTool

from crews.content_creation_crew import ContentCreationCrew
from crews.market_analysis_crew import MarketAnalysisCrew
from crews.tech_development_crew import TechDevelopmentCrew
from utils.helpers import save_result

# Load environment variables
load_dotenv()

def main():
    """Main function to run a test crew"""
    parser = argparse.ArgumentParser(description='Test CrewAI crews')
    parser.add_argument('--crew', type=str, required=True, choices=['content', 'market', 'tech'],
                        help='Type of crew to test (content, market, tech)')
    parser.add_argument('--topic', type=str, required=True,
                        help='Topic or subject for the crew to work on')
    parser.add_argument('--save', type=str, default=None,
                        help='Filename to save the result (optional)')
    
    args = parser.parse_args()
    
    # Ensure OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Select the appropriate crew
    if args.crew == 'content':
        crew_instance = ContentCreationCrew()
        crew = crew_instance.crew()
        print(f"Testing Content Creation Crew with topic: {args.topic}")
    elif args.crew == 'market':
        crew_instance = MarketAnalysisCrew()
        crew = crew_instance.crew()
        print(f"Testing Market Analysis Crew with topic: {args.topic}")
    elif args.crew == 'tech':
        crew_instance = TechDevelopmentCrew()
        crew = crew_instance.crew()
        print(f"Testing Tech Development Crew with topic: {args.topic}")
    else:
        print(f"Invalid crew type: {args.crew}")
        return
    
    # Run the crew with the provided topic
    print("Starting crew execution...")
    result = crew.kickoff(inputs={'topic': args.topic})
    
    # Print the result
    print("\nCrew Result:")
    print("=" * 80)
    print(result)
    print("=" * 80)
    
    # Save the result if requested
    if args.save:
        file_path = save_result(result, filename=args.save)
        print(f"Result saved to: {file_path}")

if __name__ == "__main__":
    main()
