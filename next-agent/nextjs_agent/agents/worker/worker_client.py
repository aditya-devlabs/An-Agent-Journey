import os
from openai import OpenAI
from dotenv import load_dotenv
from nextjs_agent.config import Config, PACKAGE_DIR

load_dotenv(PACKAGE_DIR / ".env")
worker_client = OpenAI(
    base_url=Config().load().get_base_url(),
    api_key=os.environ.get("WORKER_AGENT_API_KEY"),
)
