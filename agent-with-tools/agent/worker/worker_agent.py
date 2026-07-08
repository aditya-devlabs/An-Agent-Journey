from pydantic import BaseModel, ValidationError
from openai import OpenAI
from agent.tools.base import Tool
from collections.abc import Mapping
from typing import TypeAlias
from agent.models.task import Task
from agent.models.task_result import TaskResult
from agent.worker.sys_prompt import worker_sys_prompt
from agent.worker.worker_client import worker_client
from agent.tools.tool_registery import TOOLS
from agent.models.exceptions import (
    MaxRetriesExceededError,
    WorkerError,
    MaxIterationsExceededError,
    UnknownToolError,
    InvalidToolArgumentsError,
    ToolExecutionError,
    InvalidAssistantResponseError,
)
from httpx import HTTPStatusError
from agent.worker.worker_model import AssistantResponse, ToolCall
import asyncio
import json

ToolRegistry: TypeAlias = Mapping[str, Tool]
MAX_RETRIES = 5
MAX_ITERATIONS = 20


class WorkerAgent:
    def __init__(self, llm_client: OpenAI, tool_registery: ToolRegistry):
        self._llm = llm_client
        self._tool_registery = tool_registery

    async def run(self, task: Task):

        messages: list[dict[str, object]] = self._build_messages(task)
        try:
            message, modified_files = await self._executor(messages)

            return TaskResult(
                success=True,
                summary=message.content or "",
                modified_files=modified_files,
                error=None,
            )

        except WorkerError as e:
            return TaskResult(
                success=False,
                summary="",
                modified_files=[],
                error=str(e),
            )

    async def _call_llm(self, messages):
        try:
            response = await asyncio.to_thread(
                self._llm.chat.completions.create,
                messages=messages,
                model="openai/gpt-oss-120b",
                tools=self._build_tools(),
            )
            return response
        except Exception as e:
            print(type(e))
            print(e)
            raise

    async def _executor(self, messages):
        retries = 0
        modified_files: set[str] = set()
        for _ in range(MAX_ITERATIONS):
            print("Calling LLM...")
            response = await self._call_llm(messages)
            print("Response:::::::", response)

            tool_calls: list[ToolCall] | None = None
            try:
                if not response.choices:
                    raise InvalidAssistantResponseError("No choices returned by LLM")
                message = response.choices[0].message
                assistant_response = self._validate_assistant_response(message)

                if assistant_response.tool_calls is None:
                    return message, list(modified_files)

                tool_calls = assistant_response.tool_calls
                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_response.content,
                        "tool_calls": [
                            {
                                "id": tool_calls[0].id,
                                "type": "function",
                                "function": {
                                    "name": tool_calls[0].function.name,
                                    "arguments": tool_calls[0].function.arguments,
                                },
                            }
                        ],
                    }
                )

                result = await self._execute_tool(tool_calls[0])

                modified_files.update(result.get("modified_files", []))

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_calls[0].id,
                        "content": json.dumps(result),
                    }
                )

            except WorkerError as e:
                retries += 1

                if tool_calls is None:
                    messages.append(
                        {
                            "role": "assistant",
                            "content": f"Invalid assistant response: {e}",
                        }
                    )
                else:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_calls[0].id,
                            "content": json.dumps(
                                {
                                    "success": False,
                                    "error": str(e),
                                    "modified_files": [],
                                }
                            ),
                        }
                    )

            if retries >= MAX_RETRIES:
                raise MaxRetriesExceededError(
                    f"Maximum retries ({MAX_RETRIES}) exceeded."
                )

        raise MaxIterationsExceededError("Maximum iterations exceeded.")

    def _build_messages(self, task: Task) -> list[dict]:
        user_prompt = f"""Goal:
            {task.goal}
            """

        if task.context:
            user_prompt += f"\nContext:\n{task.context}\n"

        if task.relevant_files:
            user_prompt += "\nRelevant Files:\n"
            user_prompt += "\n".join(f"- {file}" for file in task.relevant_files)

        return [
            {
                "role": "system",
                "content": worker_sys_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

    def _build_tools(self) -> list[dict]:
        tools = []

        for tool in self._tool_registery.values():
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.args_schema.model_json_schema(),
                    },
                }
            )

        return tools

    async def _execute_tool(self, tool_call: ToolCall) -> dict:

        tool = self._tool_registery.get(tool_call.function.name)
        if tool is None:
            raise UnknownToolError(f"Unknown tool: {tool_call.function.name}")

        try:
            arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            raise InvalidToolArgumentsError("Tool arguments are not valid JSON.") from e
        try:
            validated_args = tool.args_schema.model_validate(arguments)
        except ValidationError as e:
            raise InvalidToolArgumentsError(str(e)) from e

        try:
            result = await tool.execute(validated_args)
        except Exception as e:
            raise ToolExecutionError(str(e)) from e

        return result

    def _validate_assistant_response(self, message) -> AssistantResponse:
        try:
            assistant_response = AssistantResponse.model_validate(
                {
                    "content": message.content,
                    "tool_calls": (
                        [tc.model_dump() for tc in message.tool_calls]
                        if message.tool_calls
                        else None
                    ),
                }
            )

            return assistant_response
        except ValidationError as e:
            raise InvalidAssistantResponseError(str(e)) from e
