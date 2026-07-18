import json
import asyncio
from openai import OpenAI
from pydantic import ValidationError
from nextjs_agent.models.orchestrator_response import OrchestratorResponse
from nextjs_agent.agents.orchestrator.orchestrator_sys_prompt import orchestrator_sys_prompt
from nextjs_agent.config import Config


async def call_orchestrator(
    client: OpenAI,
    config: Config,
    project_tree: str,
    history: list[str],
) -> OrchestratorResponse:
    messages = _build_messages(project_tree, history)

    response = await asyncio.to_thread(
        client.chat.completions.create,
        messages=messages,
        model=config.get_model(),
    )

    content = response.choices[0].message.content
    return _parse_response(content)


def _build_messages(project_tree: str, history: list[str]) -> list[dict]:
    user_content = f"Project structure:\n{project_tree}"

    if history:
        user_content += "\n\nHistory of what has been done:\n"
        user_content += "\n".join(f"- {item}" for item in history)

    user_content += "\n\nWhat is the NEXT single atomic task?"

    return [
        {"role": "system", "content": orchestrator_sys_prompt},
        {"role": "user", "content": user_content},
    ]


def _parse_response(content: str) -> OrchestratorResponse:
    try:
        data = json.loads(content)
        return OrchestratorResponse.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        return OrchestratorResponse(
            thought=f"Failed to parse response: {e}",
            task=None,
            done=True,
            reason="Orchestrator returned invalid response",
        )
