# CrewAI Agents Platform

A scalable platform for building, deploying, and managing CrewAI agents for various AI applications.

## Overview

This project provides a comprehensive framework for creating AI agent crews using [CrewAI](https://github.com/crewai/crewai), with a focus on deployment to Railway. The platform includes:

- Multiple pre-configured agent types (researchers, writers, analysts, developers)
- Task templates for common workflows
- Ready-to-use crew configurations
- FastAPI backend for easy integration
- Railway deployment configuration
- Database integration for state persistence

## Installation

### Prerequisites

- Python 3.10+
- OpenAI API key
- Serper API key (for search capabilities)

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crewai.git
   cd crewai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Usage

### Running Locally

You can test the different crew types using the test script:

```bash
# Test content creation crew
python test_crew.py --crew content --topic "Artificial Intelligence in Healthcare" --save ai_healthcare.txt

# Test market analysis crew
python test_crew.py --crew market --topic "Electric Vehicle Market in Saudi Arabia" --save ev_market.txt

# Test tech development crew
python test_crew.py --crew tech --topic "Building a Recommendation System" --save recommendation_system.txt
```

### Starting the API Server

Run the FastAPI server locally:

```bash
uvicorn api:app --reload
```

The API will be available at http://localhost:8000 with Swagger documentation at http://localhost:8000/docs

### API Endpoints

- `GET /health`: Health check endpoint
- `POST /crew`: Run a crew with specific parameters

Example request to the `/crew` endpoint:

```json
{
  "crew_type": "content_creation",
  "inputs": {
    "topic": "Artificial Intelligence in Saudi Arabia",
    "target_audience": "Business Leaders",
    "content_type": "White Paper"
  },
  "metadata": {
    "user_id": "user123",
    "project_id": "project456"
  }
}
```

## Extending the Platform

### Creating Custom Agents

To create new agent types, extend the `AgentFactory` class:

1. Add a new method to create your specialized agent
2. Update the `get_agent` method to include your new agent type

```python
def _create_custom_agent(self, **kwargs) -> Agent:
    return Agent(
        role="Your Specialized Role",
        goal="Specific goal for this agent type",
        backstory="""Detailed backstory that provides context and expertise""",
        verbose=True,
        tools=[self.common_tools["relevant_tool"]],
        **kwargs
    )
```

### Creating Custom Tasks

To create new task types, extend the `TaskFactory` class:

1. Add a new method to create your specialized task
2. Update the `get_task` method to include your new task type

### Creating Custom Crews

To create a new crew type:

1. Create a new file in the `crews` directory
2. Define a class with agent and task methods
3. Implement a `crew()` method that assembles the agents and tasks
4. Update `CrewFactory` to include your new crew type

## Best Practices

### Agent Design

- **Specific Roles**: Use specific, specialized roles instead of generic ones
- **Clear Goals**: Define clear, measurable goals for each agent
- **Rich Backstories**: Create detailed backstories that establish expertise and context
- **Appropriate Tools**: Assign relevant tools to each agent based on their role

Example of a well-defined agent:

```python
researcher = Agent(
    role="Market Research Specialist for Saudi Arabian Markets",
    goal="Gather comprehensive market data with special focus on cultural and regional factors",
    backstory="""You are an expert market researcher with 15 years of experience in
    Middle Eastern markets, particularly Saudi Arabia. You understand the nuances of
    the Saudi business environment, cultural preferences, and regulatory landscape.
    You have connections to reliable data sources and know how to interpret regional trends."""
)
```

### Task Design

- **Clear Instructions**: Provide specific, unambiguous instructions
- **Contextual Information**: Include relevant context for the task
- **Expected Output**: Clearly define what the output should look like
- **Breaking Down Tasks**: Split complex tasks into smaller, manageable parts

## Deployment

For detailed deployment instructions to Railway, see [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [CrewAI](https://github.com/crewai/crewai) for the core agent framework
- [LangChain](https://github.com/langchain-ai/langchain) for language model integration
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Railway](https://railway.app/) for deployment platform
