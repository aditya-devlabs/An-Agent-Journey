import json
from pathlib import Path
import math
import random
import os
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
import sys

load_dotenv()


client = Cerebras(
    api_key=os.getenv("cerebras_api_key"),
)

Path("memory.json").touch(exist_ok=True)


def main():
    with open("memory.json", "r") as f:
        all_memories: list[list[dict]] = json.load(f)

    choice = input("""
        1. Start new conversation with /new
        2. Load existing conversation with /old
        Your choice 👉: """)

    if choice == "/old":
        print("Old memories:")
        print(json.dumps(all_memories, indent=2, ensure_ascii=False))

        print("\n")        
        index = int(input("Select the conversation by their index: "))
        if type(index) != int or not (0 <= index < len(all_memories)):
            print("Invalid choice!")
            return
        history = all_memories[int(index)]

    elif choice == "/new":
        pass
    else:
        print("Invalid choice. Start again")
        return
        
    print("\n")    
    prompt = input("Give the prompt lmbsm: ")

    sys_prompt = "You are helpful assistant."

    messages = []

    if choice == "/old":
        if len(history) <= 9: # either all old messages, or one message to compact history and 3 fresh messages.
            messages.extend(history)
        else:
            print("Please Wait, Memory Compaction is taking place!!!")
            messages.extend(compact(history))
            print("Message history compacted!!")
            print()
            print(messages)
            print()
    else:
        messages = [{"role": "system", "content": sys_prompt}]


    messages.append({"role": "user", "content": prompt})

    while True:

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="gemma-4-31b",
        )
        print(chat_completion.choices[0].message.content)
        messages.append(
            {
                "role": "assistant",
                "content": chat_completion.choices[0].message.content,
            }
        )
        print("\n")

        prompt = input("Give the prompt : ")

        if prompt == "quit":
            if choice == "/old":
                all_memories[index] = messages

            else:
                all_memories.append(messages)
            with open("memory.json", "w") as file:
                json.dump(all_memories, file, indent=2)
            break

        messages.append(
            {"role": "user", "content": f"{prompt}"},
        )


def compact(history):
    user_prompt = "Hey the size of the conversation became quite big, can you summarize that to keep the context size managed please. This was our conversation"
    messages = [{"role": "system", "content": "You are helpful ai assistant"}]
    messages.append({"role": "user", "content": user_prompt})

    messages.extend(history)
    chat_completion = client.chat.completions.create(
            messages=messages,
            model="gemma-4-31b",
        )
    updated_chat = [{"role": "system", "content": "You are helpful ai assistant"}]
    updated_chat.append({"role": "user", "content": user_prompt})
    updated_chat.append({"role": "assistant", "content": chat_completion.choices[0].message.content})
    
    return updated_chat
    
    
    



if __name__ == "__main__":
    main()
