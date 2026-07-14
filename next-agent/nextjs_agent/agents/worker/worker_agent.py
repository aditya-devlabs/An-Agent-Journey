from pydantic import ValidationError
import json
from nextjs_agent.models.worker_models import ToolCall, AssistantResponse
import asyncio
from nextjs_agent.models.exceptions import (
    WorkerError,
    InvalidAssistantResponseError,
    MaxRetriesExceededError,
    MaxIterationsExceededError,
    UnknownToolError,
    InvalidToolArgumentsError,
    ToolExecutionError,
)
from nextjs_agent.models.task import Task
from nextjs_agent.models.task_result import TaskResult
from nextjs_agent.tools.base import TOOL
from typing import TypeAlias, Mapping
from openai import OpenAI
from nextjs_agent.agents.worker import worker_sys_prompt
from nextjs_agent.config import Config

ToolRegistry: TypeAlias = Mapping[str, TOOL]


class WorkerAgent:

    MAX_RETRIES = 3
    MAX_ITERATIONS = 10

    def __init__(self, llm_client: OpenAI, tool_registry: ToolRegistry, config: Config):

        self._llm = llm_client
        self._config = config
        self._tool_registry = tool_registry
        self._retries = 0

    async def run(self, task: Task) -> TaskResult:

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
                model=self._config.get_model(),
                tools=self._build_tools(),
            )
            return response
        except Exception as e:
            if self._retries < self.MAX_RETRIES and self.is_transient(e):
                # transient req ke lie there is no need to append the error again and send it to llm, as they are self healing.
                delay = self._backoff(self._retries)
                self._retries += 1
                print(f"LLM error, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
                return await self._call_llm(messages)
            raise

    async def _executor(self, messages):
        modified_files: set[str] = set()

        for _ in range(self.MAX_ITERATIONS):
            print("Worker Agent 🤖 (Calling llm)...")

            response = await self._call_llm(messages)

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
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in tool_calls
                        ],
                    }
                )

                for tc in tool_calls:
                    try:
                        result = await self._execute_tool(tc)
                    except Exception as e:
                        self._retries += 1
                        if self._retries >= self.MAX_RETRIES:
                            raise MaxRetriesExceededError(
                                f"Maximum retries ({self.MAX_RETRIES}) exceeded."
                            )
                        result = {
                            "success": False,
                            "error": str(e),
                            "modified_files": [],
                        }

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(result),
                        }
                    )

                    modified_files.update(result.get("modified_files", []))

            except WorkerError as e:
                if self._retries >= self.MAX_RETRIES:
                    raise MaxRetriesExceededError(
                        f"Maximum retries ({self.MAX_RETRIES}) exceeded."
                    )
                delay = self._backoff(self._retries)
                self._retries += 1
                print(f"Worker error, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)

                if tool_calls is None:
                    messages.append(
                        {
                            "role": "assistant",
                            "content": f"Invalid assistant response: {e}",
                        }
                    )

        raise MaxIterationsExceededError("Maximum iterations exceeded.")

    def _build_messages(self, task: Task) -> list[dict]:

        user_prompt = f"Goal:\n{task.goal}"

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

        for tool in self._tool_registry.values():
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

        tool = self._tool_registry.get(tool_call.function.name)
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

    @staticmethod
    def _backoff(retry_count: int) -> float:
        return 2**retry_count

    @staticmethod
    def is_transient(e) -> bool:
        """Check if error is worth retrying."""
        # very half assed way to check if the error is known and easy to pass through on next iteration or not.
        error_type = type(e).__name__
        retryable = ["RateLimitError", "APITimeoutError", "APIConnectionError"]
        return error_type in retryable
