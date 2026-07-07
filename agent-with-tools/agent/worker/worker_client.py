import os
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

load_dotenv()
worker_client = Cerebras(
    
    api_key=os.environ.get("WORKER_CEREBRAS_API_KEY"),
)



