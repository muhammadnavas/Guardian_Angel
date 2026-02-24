import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY")
)

response = client.responses.create(
  model="gpt-5-nano",
  input="write about openai",
  store=True,
)

print(response.output_text);
