import os
from openai import OpenAI
from dotenv import load_dotenv
from llm.sys_prompt import sys_prompt

from llm.memory.mem0_client import client as mem0Client

load_dotenv()
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("NVIDIA_API_KEY"),
)

messages = [
    {"role": "system", "content": sys_prompt},
]

def memory_agent():
    user_id = input("Enter your user id 👉:")

    user_input = input("Enter the message 👉:")

    memories = mem0Client.search(user_input, filters={"user_id": user_id})

    print("memories : ", memories)
    messages.append(
        {
            "role": "system",
            "content": f"If there are relevant memories to the user input then they will be shown here : {memories}. If there are none, then we don't have user query stored.",
        }
    )

    messages.append({"role": "user", "content": f"{user_input}"})

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="openai/gpt-oss-120b",
        temperature=0.99
    )

    mem0Client.add(messages, user_id=user_id)

    print()
    print(chat_completion.choices[0].message.content)
