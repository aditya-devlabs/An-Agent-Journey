from mem0 import MemoryClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MemoryClient(api_key=os.getenv("mem0-api-key"))
