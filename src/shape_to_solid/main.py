import os
import yaml
import subprocess

from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from crewai_tools import FileReadTool, DirectoryReadTool, FileWriterTool

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


@tool("Run Shell Command")
def run_shell_command(command: str) -> str:
    """
    Run a shell command and return the output.
    Use this tool to execute shell commands like running TypeScript compiler to check for errors.

    Args:
        command: The shell command to execute (e.g., 'deno check src/solid/Email.ts')

    Returns:
        The stdout and stderr output of the command, or an error message if the command fails.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        if result.returncode != 0:
            output += f"Return code: {result.returncode}\n"
        return output if output else "Command completed successfully with no output."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"

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


def create_developer_agent(
    tools: list,
    shape_name: str,
    shape_file_path: str,
    output_class_file: str,
    output_dataset_file: str,
    output_mod_file: str,
    objects_path: str
) -> tuple[Agent, Task]:
    """Create and configure the Developer agent and task.

    Args:
        tools: List of tools available to the agent
        shape_name: Name of the shape (e.g., 'Email', 'Person')
        shape_file_path: Full path to the SHACL shape .ttl file
        output_class_file: Full path for the output class file (e.g., .../Email.ts)
        output_dataset_file: Full path for the output dataset file (e.g., .../EmailDataset.ts)
        output_mod_file: Full path to the mod.ts file to update
        objects_path: Path to the objects repository for running compiler
    """
    config = load_agent_config(
        'developer',
        project_root=PROJECT_ROOT,
        shape_name=shape_name,
        shape_file_path=shape_file_path,
        output_class_file=output_class_file,
        output_dataset_file=output_dataset_file,
        output_mod_file=output_mod_file,
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
        agent=agent
    )

    return agent, task



def main():
    # Setup file tools for reading blueprints and example files
    shapes_path = os.getenv("REPO_SHAPES_PATH")
    objects_path = os.getenv("REPO_OBJECT_PATH")

    # File reading tools for different directories
    file_read_tool = FileReadTool()
    dir_read_tool = DirectoryReadTool()
    file_write_tool = FileWriterTool()
    tools = [file_read_tool, dir_read_tool, file_write_tool, run_shell_command]

    # Create agents and tasks
    # architect, architect_guide_task = create_architect_agent(shapes_path, objects_path, tools)

    # Configure for Email shape (change these values for different shapes)
    shape_name = "Email"
    developer, developer_task = create_developer_agent(
        tools=tools,
        shape_name=shape_name,
        shape_file_path=f"{shapes_path}/shapes/Email/emailShape.ttl",
        output_class_file=f"{objects_path}/src/solid/Email.ts",
        output_dataset_file=f"{objects_path}/src/solid/EmailDataset.ts",
        output_mod_file=f"{objects_path}/src/solid/mod.ts",
        objects_path=objects_path
    )

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
    print(f"Developer has completed {shape_name} Solid Object implementation.")
    print(f"Output files in: {objects_path}/src/solid/")
    print("="*60)
    return result


if __name__ == "__main__":
    main()