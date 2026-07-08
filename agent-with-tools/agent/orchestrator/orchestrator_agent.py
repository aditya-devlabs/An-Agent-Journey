from pydantic import BaseModel, Field
from agent.orchestrator.main_client import orchestrator_client
from agent.orchestrator.sys_prompt import orchestrator_sys_prompt
from agent.worker.worker_agent import WorkerAgent
from agent.worker.worker_client import worker_client
from agent.tools.tool_registery import TOOLS
from agent.models.task import Task
from agent.models.task_result import TaskResult
import asyncio
import json
import tiktoken


MAX_ITERATIONS = 20
MAX_PROMPT_TOKENS = 100_000
TOKENIZER = tiktoken.get_encoding("cl100k_base")


class DelegateTaskArgs(BaseModel):
    goal: str = Field(description="The specific task for the worker to accomplish")
    context: str | None = Field(
        default=None,
        description="Additional context or instructions for the worker",
    )
    relevant_files: list[str] = Field(
        default_factory=list,
        description="Files the worker should consider first",
    )


def _count_tokens(messages: list[dict]) -> int:
    count = 0
    for msg in messages:
        count += 4
        for key, value in msg.items():
            count += len(TOKENIZER.encode(str(value)))
            if key == "tool_calls" and isinstance(value, list):
                for tc in value:
                    count += len(TOKENIZER.encode(str(tc.get("function", {}).get("name", ""))))
                    count += len(TOKENIZER.encode(str(tc.get("function", {}).get("arguments", ""))))
    count += 2
    return count


class OrchestratorAgent:
    def __init__(self, llm_client, worker: WorkerAgent):
        self._llm = llm_client
        self._worker = worker
        self._model = "openai/gpt-oss-120b"

    async def run(self, messages: list[dict]) -> list[dict]:
        for _ in range(MAX_ITERATIONS):
            print("Orchestrator thinking...")
            response = await asyncio.to_thread(
                self._llm.chat.completions.create,
                model=self._model,
                messages=messages,
                tools=self._build_tools(),
                tool_choice="auto",
            )

            message = response.choices[0].message

            if not message.tool_calls:
                print("\n=== Final Answer ===")
                print(message.content)
                return messages

            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            for tc in message.tool_calls:
                if tc.function.name == "delegate_to_worker":
                    args = json.loads(tc.function.arguments)
                    task = Task(
                        goal=args["goal"],
                        context=args.get("context"),
                        relevant_files=args.get("relevant_files", []),
                    )
                    print(f"Delegating task: {args['goal'][:80]}...")
                    result: TaskResult = await self._worker.run(task)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps({
                            "success": result.success,
                            "summary": result.summary,
                            "modified_files": result.modified_files,
                            "error": result.error,
                        }),
                    })

        print("Max iterations reached.")
        return messages

    async def _compact(self, messages: list[dict]) -> list[dict]:
        system_msg = messages[0]
        rest = messages[1:]

        summary_prompt = (
            "Summarize the following conversation between a user and an AI coding assistant. "
            "Keep the summary concise — mention the goal, what was done, key decisions, "
            "and the current state. This summary will replace the entire conversation history."
        )

        summary_messages = [{"role": "user", "content": summary_prompt}, *rest]

        response = await asyncio.to_thread(
            self._llm.chat.completions.create,
            model=self._model,
            messages=summary_messages,
            max_tokens=1024,
        )

        summary = response.choices[0].message.content or ""
        print(f"\n[Context compacted — summarized {len(rest)} messages]\n")

        return [system_msg, {"role": "user", "content": f"[Previous conversation summary]: {summary}"}]

    def _build_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "delegate_to_worker",
                    "description": (
                        "Delegate a specific task to the worker agent. "
                        "The worker can read files, write files, edit code, list directories, etc. "
                        "Use this whenever you need to inspect or modify the project."
                    ),
                    "parameters": DelegateTaskArgs.model_json_schema(),
                },
            }
        ]


if __name__ == "__main__":
    worker = WorkerAgent(worker_client, TOOLS)
    agent = OrchestratorAgent(orchestrator_client, worker)

    messages: list[dict] | None = None
    print("Orchestrator ready. Type 'quit' to exit.\n")

    while True:
        if messages:
            tokens = _count_tokens(messages)
            bar_len = 30
            filled = int((tokens / MAX_PROMPT_TOKENS) * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"  Context: [{bar}] {tokens}/{MAX_PROMPT_TOKENS} tokens ({tokens * 100 // MAX_PROMPT_TOKENS}%)")

        goal = input(">>> ").strip()
        if goal.lower() == "quit":
            print("Goodbye!")
            break

        if messages is None:
            messages = [
                {"role": "system", "content": orchestrator_sys_prompt},
                {"role": "user", "content": goal},
            ]
        else:
            if _count_tokens(messages) > MAX_PROMPT_TOKENS:
                old_tokens = _count_tokens(messages)
                messages = asyncio.run(agent._compact(messages))
                new_tokens = _count_tokens(messages)
                print(f"  Compacted: {old_tokens} → {new_tokens} tokens (saved {old_tokens - new_tokens})")
            messages.append({"role": "user", "content": goal})

        messages = asyncio.run(agent.run(messages))
