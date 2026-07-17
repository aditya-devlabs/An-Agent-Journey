from openai import OpenAI
from dotenv import load_dotenv
from nextjs_agent.config import Config, PACKAGE_DIR

load_dotenv(PACKAGE_DIR / ".env")
config = Config().load()
worker_client = OpenAI(
    base_url=config.get_base_url(),
    api_key=config.get_worker_key() or None,
)
