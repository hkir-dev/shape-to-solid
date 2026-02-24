import os

from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process, LLM
from crewai.mcp import MCPServerStdio

load_dotenv()

llm_architect = LLM(
    # model=os.getenv("MODEL_NAME_ARCHITECT"),
    model="gpt-4o",
    api_key=os.getenv("GITHUB_COPILOT_TOKEN"),
    base_url="https://models.github.ai/inference",
    temperature=1,  # o1-preview requires temperature=1
    max_tokens=8000
)


def main():
    # Setup MCP tools for filesystem access
    # Allow read access to blueprints and the example repositories
    file_mcp = MCPServerStdio(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            os.getenv("REPO_SHAPES_PATH", "./blueprints"),
            os.getenv("REPO_OBJECT_PATH", "./blueprints"),
            "./blueprints"
        ]
    )

    # Define the System Architect Agent with detailed role and backstory
    architect = Agent(
        role='Senior SHACL-to-TypeScript System Architect',
        goal=(
            'Read and deeply analyze the blueprints/rules.md file and all referenced example files '
            '(SHACL shapes and corresponding TypeScript Solid Object implementations). '
            'Produce a comprehensive, self-contained guidance document (agent_work/architect.md) '
            'that serves as the sole source of truth for the Developer Agent to implement '
            'SHACL Shape to TypeScript Solid Object conversions.'
        ),
        backstory='''You are a world-class expert in Semantic Web technologies, RDF, SHACL (Shapes Constraint Language), 
and TypeScript development. With over 15 years of experience bridging ontology design and practical software engineering, 
you have developed and contributed to multiple open-source RDF libraries including RDF/JS Wrapper.

Your expertise includes:
- Deep understanding of SHACL specifications (sh:NodeShape, sh:PropertyShape, cardinalities, datatypes)
- Expert knowledge of RDF concepts (Turtle syntax, URIs, prefixes, literals, blank nodes)
- Mastery of TypeScript patterns including class inheritance, generics, and type safety
- Extensive experience with the RDF/JS Wrapper library (TermWrapper, DatasetWrapper, ValueMapping, ObjectMapping)

Your approach is methodical and documentation-driven. You believe that clear, detailed specifications 
prevent implementation errors and reduce back-and-forth between team members. When analyzing examples, 
you identify patterns, edge cases, and best practices that must be documented for developers.

You are meticulous about:
- Mapping SHACL constraints to TypeScript patterns (minCount/maxCount to nullable/required properties)
- Naming conventions (URI local names to camelCase properties)
- Proper use of RDF/JS Wrapper utility methods (singular, singularNullable, set, overwrite, overwriteNullable)
- Dataset iteration patterns with DatasetWrapper
- Export organization in mod.ts files

Your mission is to create documentation so clear and comprehensive that a developer can implement 
any SHACL-to-TypeScript conversion without needing to ask clarifying questions.''',
        mcps=[file_mcp],
        llm=llm_architect,
        verbose=True,
        allow_delegation=False
    )

    # Single focused task: Generate the architect guidance document
    architect_guide_task = Task(
        description='''Your task is to create a comprehensive guidance document for SHACL to Solid Object conversion.

**Step 1: Read the Rules**
Read and analyze the file `blueprints/rules.md` thoroughly. Understand:
- Class mapping rules (sh:NodeShape -> TypeScript class)
- Property mapping rules (sh:path, sh:datatype, sh:node, cardinalities)
- Implementation guidelines (encapsulation, ValueMapping, ObjectMapping)
- Dataset wrapping patterns

**Step 2: Analyze All Examples**
The rules.md file references these example pairs. You MUST read and analyze EACH of them:

1. Group Shape: 
   - Shape: {REPO_SHAPES_PATH}/shapes/Group/groupShape.ttl
   - TypeScript: {REPO_OBJECT_PATH}/src/solid/Group.ts and GroupDataset.ts

2. Meeting Shape:
   - Shape: {REPO_SHAPES_PATH}/shapes/Meeting/meetingShape.ttl
   - TypeScript: {REPO_OBJECT_PATH}/src/solid/Meeting.ts and MeetingDataset.ts

3. Organization Shape:
   - Shape: {REPO_SHAPES_PATH}/shapes/Organization/organizationShape.ttl
   - TypeScript: {REPO_OBJECT_PATH}/src/solid/Organization.ts and OrganizationDataset.ts

4. Person Shape:
   - Shapes: {REPO_SHAPES_PATH}/shapes/Person/personShape.ttl and personNameShape.ttl
   - TypeScript: {REPO_OBJECT_PATH}/src/solid/Person.ts and PersonDataset.ts

5. Profile Shape:
   - Shape: {REPO_SHAPES_PATH}/shapes/PersonalProfile/personalProfileShape.ttl
   - TypeScript: {REPO_OBJECT_PATH}/src/solid/Profile.ts and ProfileDataset.ts

6. Mod file: {REPO_OBJECT_PATH}/src/solid/mod.ts

Note: Replace {REPO_SHAPES_PATH} with the value from environment variable REPO_SHAPES_PATH 
and {REPO_OBJECT_PATH} with the value from environment variable REPO_OBJECT_PATH.

**Step 3: Generate Comprehensive Guidance Document**
Create agent_work/architect.md with the following structure:

1. **Overview**: Purpose of the document and how to use it
2. **SHACL to TypeScript Mapping Reference Table**: Complete mapping of SHACL constructs to TypeScript patterns
3. **Class Generation Rules**: Step-by-step process for creating a class from sh:NodeShape
4. **Property Generation Rules**: Detailed rules for each property type:
   - Required string properties (sh:minCount 1, sh:datatype xsd:string)
   - Optional string properties (no minCount or minCount 0)
   - Required object references (sh:node with minCount 1)
   - Optional object references (sh:node without minCount or minCount 0)
   - Array properties (sh:maxCount > 1 or no maxCount)
   - List properties using ObjectMapping.as()
5. **Code Patterns**: Exact code templates with placeholders for:
   - Import statements
   - Class declaration extending TermWrapper
   - Getter methods (singular, singularNullable, set patterns)
   - Setter methods (overwrite, overwriteNullable patterns)
   - DatasetWrapper implementation
6. **Naming Conventions**: URI to property name conversion rules
7. **Export Organization**: How to update mod.ts
8. **Example Walkthroughs**: Detailed analysis of at least 2 complete examples showing:
   - Original SHACL shape
   - Resulting TypeScript code
   - Explanation of each mapping decision
9. **Common Patterns and Edge Cases**: Learned patterns from example analysis
10. **Checklist for Developers**: Step-by-step implementation checklist

The document must be self-contained - a developer should be able to implement any conversion 
using ONLY this document without needing to reference other files.
''',
        expected_output='''A comprehensive markdown document saved to agent_work/architect.md that contains:
- Complete SHACL to TypeScript mapping reference
- Detailed code templates and patterns
- At least 2 fully analyzed example walkthroughs
- Developer implementation checklist
- All information needed for a developer to implement Shape to Solid Object conversions independently''',
        agent=architect,
        output_file='agent_work/architect.md'
    )

    # Assemble the Crew with only the architect
    crew = Crew(
        agents=[architect],
        tasks=[architect_guide_task],
        process=Process.sequential,
        verbose=True
    )

    # Run and stop after generating the guide
    result = crew.kickoff()
    print("\n" + "="*60)
    print("System Architect has completed the guidance document.")
    print("Output saved to: agent_work/architect.md")
    print("="*60)
    return result


if __name__ == "__main__":
    main()