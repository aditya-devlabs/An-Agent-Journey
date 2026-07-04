# CLI Chatbot with Memory

Just a small project I made while playing around with the Cerebras API.

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
uv add python-dotenv cerebras-cloud-sdk
``` 

Create a `.env` file:

```env
cerebras_api_key=YOUR_API_KEY
```

Then run:

```bash
uv run main.py
```

Type `quit` anytime to save the conversation and exit.

---

Nothing serious—just experimenting with conversational memory and context compression.