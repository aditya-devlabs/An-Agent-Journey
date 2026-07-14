import os
from openai import OpenAI
from dotenv import load_dotenv
from nextjs_agent.config import Config

load_dotenv()
worker_client = OpenAI(
    base_url=Config().get_base_url(),
    api_key=os.environ.get("WORKER_AGENT_API_KEY"),
)
