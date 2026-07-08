# CLI Chatbot with Memory

Just a small project I made while playing around with the NVIDIA NIM API.

It supports:
- Starting new conversations
- Loading old conversations
- Persistent chat history using `memory.json`
- Simple history compaction by asking the model to summarize older messages when the conversation gets too long

## Run

Initiallisation:
```bash
uv init
uv sync
```

Install dependencies:

```bash
uv add python-dotenv openai
``` 

Create a `.env` file:

```env
NVIDIA_API_KEY=YOUR_API_KEY
```

Then run:

```bash
uv run main.py
```

Type `quit` anytime to save the conversation and exit.

---

Nothing serious—just experimenting with conversational memory and context compression.