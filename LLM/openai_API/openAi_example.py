# conda activate cv311

# для версии библиотеки openai>1.0

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=api_key)

resp = client.responses.create(
    model="gpt-4.1-mini",
    input="Привет"
)

print(resp.output_text)