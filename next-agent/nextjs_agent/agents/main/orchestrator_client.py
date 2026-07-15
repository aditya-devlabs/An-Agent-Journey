import os
from openai import OpenAI
from dotenv import load_dotenv
from nextjs_agent.config import Config, PACKAGE_DIR

load_dotenv(PACKAGE_DIR / ".env")
orchestrator_client = OpenAI(
    base_url=Config().get_base_url(),
    api_key=os.environ.get("MAIN_AGENT_API_KEY"),
)
