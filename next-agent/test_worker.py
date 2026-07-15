import asyncio
from pathlib import Path
from nextjs_agent.config import Config, PROJECT_ROOT
from nextjs_agent.agents.worker.worker_client import worker_client
from nextjs_agent.agents.worker.worker_agent import WorkerAgent
from nextjs_agent.tools.tools_registry import create_tools
from nextjs_agent.models.task import Task


async def main():
    config = Config.load()
    tools = create_tools(PROJECT_ROOT)

    agent = WorkerAgent(
        llm_client=worker_client,
        tool_registry=tools,
        config=config,
    )

    task = Task(
        goal="Yo, see the readme.md, update the readme by adding these 2 things under not started headline: 1. Provide websearch tool to the model for less hallucinations and more up to date knowledge. 2. Give grep tool to the agent so it becomes easy for it to find files, function names, variables etc in the nextjs repo easily. Add these on top of other not started contents.",
        context="This is a python project",
        relevant_files=["README.md"],
    )

    result = await agent.run(task)

    print(f"\nSuccess: {result.success}")
    print(f"Summary: {result.summary}")
    print(f"Modified: {result.modified_files}")
    if result.error:
        print(f"Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())
