import os
from cerebras.cloud.sdk import Cerebras
client = Cerebras(
    api_key=os.environ.get("CEREBRAS_API_KEY"),
)



