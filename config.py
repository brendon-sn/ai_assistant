from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_BASE = os.getenv("API_BASE")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2024-06-01")

llm = AzureChatOpenAI(
    api_key=API_KEY,
    azure_endpoint=API_BASE,
    openai_api_version=AZURE_API_VERSION,
    model=AZURE_DEPLOYMENT,
    temperature=0,
)