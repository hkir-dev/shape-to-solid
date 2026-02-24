import os
import yaml

from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import FileReadTool, DirectoryReadTool

load_dotenv()

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '../../'))

llm_architect = LLM(
    model="gpt-4o",
    api_key=os.getenv("GITHUB_COPILOT_TOKEN"),
    base_url="https://models.github.ai/inference",
    temperature=1,
    max_tokens=8000
)

llm_architect_gpt = LLM(
    model="gpt-4o",
    temperature=1
)


def load_agent_config(agent_name: str, **format_kwargs) -> dict:
    """Load agent configuration from YAML file and format with provided kwargs."""
    config_path = os.path.join(PROJECT_ROOT, 'agent_docs', f'{agent_name}.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Format all string values with provided kwargs
    for key, value in config.items():
        if isinstance(value, str):
            config[key] = value.format(**format_kwargs)

    return config


def create_architect_agent(shapes_path: str, objects_path: str, tools: list) -> tuple[Agent, Task]:
    """Create and configure the System Architect agent and task."""
    config = load_agent_config(
        'architect',
        project_root=PROJECT_ROOT,
        shapes_path=shapes_path,
        objects_path=objects_path
    )

    agent = Agent(
        role=config['role'],
        goal=config['goal'],
        backstory=config['backstory'],
        tools=tools,
        llm=llm_architect_gpt,
        verbose=True,
        allow_delegation=False
    )

    task = Task(
        description=config['task_description'],
        expected_output=config['expected_output'],
        agent=agent,
        output_file=config['output_file']
    )

    return agent, task


def create_developer_agent(shapes_path: str, objects_path: str, tools: list) -> tuple[Agent, Task]:
    """Create and configure the Developer agent and task."""
    config = load_agent_config(
        'developer',
        project_root=PROJECT_ROOT,
        shapes_path=shapes_path,
        objects_path=objects_path
    )

    agent = Agent(
        role=config['role'],
        goal=config['goal'],
        backstory=config['backstory'],
        tools=tools,
        llm=llm_architect_gpt,
        verbose=True,
        allow_delegation=False
    )

    task = Task(
        description=config['task_description'],
        expected_output=config['expected_output'],
        agent=agent,
        output_file=config['output_file']
    )

    return agent, task



def main():
    # Setup file tools for reading blueprints and example files
    shapes_path = os.getenv("REPO_SHAPES_PATH")
    objects_path = os.getenv("REPO_OBJECT_PATH")

    # File reading tools for different directories
    file_read_tool = FileReadTool()
    dir_read_tool = DirectoryReadTool()
    tools = [file_read_tool, dir_read_tool]

    # Create agents and tasks
    # architect, architect_guide_task = create_architect_agent(shapes_path, objects_path, tools)
    developer, developer_task = create_developer_agent(shapes_path, objects_path, tools)

    # Assemble the Crew with only the architect
    # crew = Crew(
    #     agents=[architect],
    #     tasks=[architect_guide_task],
    #     process=Process.sequential,
    #     verbose=True
    # )

    # Assemble the Crew with only the developer agent
    crew = Crew(
        agents=[developer],
        tasks=[developer_task],
        process=Process.sequential,
        verbose=True
    )

    # Run and stop after generating the code
    result = crew.kickoff()
    print("\n" + "="*60)
    print("Agent has completed task.")
    print("Output saved to: agent_work")
    print("="*60)
    return result


if __name__ == "__main__":
    main()