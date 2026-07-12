import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
worker_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("WORKER_AGENT_API_KEY"),
)
