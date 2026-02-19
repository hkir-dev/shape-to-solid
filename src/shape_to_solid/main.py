import os

from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process, LLM
from crewai.mcp import MCPServerStdio

load_dotenv()

llm_architect = LLM(
    model=os.getenv("MODEL_NAME_ARCHITECT"),
    api_key=os.getenv("GITHUB_COPILOT_TOKEN"),
    base_url="https://api.github.com/copilot/chat",
    temperature=0.2,
    max_tokens=4000
)

llm_developer = LLM(
    model=os.getenv("MODEL_NAME_DEVELOPER"),
    api_key=os.getenv("GITHUB_COPILOT_TOKEN"),
    base_url="https://api.github.com/copilot/chat",
    temperature=0.2,
    max_tokens=4000
)

llm_tester = LLM(
    model=os.getenv("MODEL_NAME_TESTER"),
    api_key=os.getenv("GITHUB_COPILOT_TOKEN"),
    base_url="https://api.github.com/copilot/chat",
    temperature=0.2,
    max_tokens=4000
)
def main():
    # 1. Setup Local MCP Tools (The 'Hands' of the Agent)
    # This gives agents local filesystem and git access
    git_mcp = MCPServerStdio(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-git", "--repo-path", os.getenv("REPO_B_PATH")]
    )

    file_mcp = MCPServerStdio(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "--allow-read", "./blueprints"]
    )

    # 2. Define the Specialized Agents
    architect = Agent(
        role='System Architect',
        goal='Analyze SHACL shapes and map them to TypeScript structures based on rules.md',
        backstory='Expert in RDF, SHACL, and Linked Data. You ensure the design follows the ontology strictly.',
        mcps=[file_mcp],
        llm=llm_architect,
        verbose=True
    )

    developer = Agent(
        role='TypeScript Developer',
        goal='Write POJO classes in Repo B following the shacl-js standard and examples.',
        backstory='Senior TS developer. You write clean, performant, and type-safe POJO classes.',
        mcps=[git_mcp, file_mcp],
        llm=llm_developer,
        verbose=True
    )

    tester = Agent(
        role='QA Engineer',
        goal='Validate that generated classes match SHACL constraints and pass TS compilation.',
        backstory='Meticulous tester. You ensure Repo B remains stable and classes are bug-free.',
        mcps=[git_mcp],
        llm=llm_tester,
        verbose=True
    )

    # 1. The Human in the Loop Analysis Task
    analysis_task = Task(
        description=(
            "Analyze the SHACL shapes in Repo A according to rules.md. "
            "Create a detailed mapping for every sh:PropertyShape, including "
            "TypeScript types, cardinalities, and naming conversions."
        ),
        expected_output="A complete mapping blueprint for the TypeScript POJO classes.",
        agent=architect,
        # This writes the result directly to your local workspace
        output_file='analysis_output.md',
        # This pauses the execution and waits for your 'OK' or feedback in the terminal
        human_input=True
    )

    # 2. The Development Task (Depends on the Architect's approved output)
    coding_task = Task(
        description=(
            "Using the approved mapping in analysis_output.md, generate the "
            "TypeScript POJO classes in Repo B. Ensure you follow the shacl-js "
            "standard and refer to the examples/ directory for style."
        ),
        expected_output="New .ts files committed to Repo B and registered in index.ts.",
        agent=developer,
        context=[analysis_task] # Forces the developer to read the Architect's approved work
    )

    validation_task = Task(
        description="Run tsc on the new classes. Verify the structure against the POJO standard in rules.md.",
        expected_output="A validation report. If fail, send back to Developer with logs.",
        agent=tester,
        context=[coding_task]
    )

    # 4. Assemble the Crew
    crew = Crew(
        agents=[architect, developer, tester],
        tasks=[analysis_task, coding_task, validation_task],
        process=Process.sequential # Analysis -> Code -> Test
    )

    crew.kickoff()

if __name__ == "__main__":
    main()