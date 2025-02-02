import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if the API key is correctly loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ API key is missing from .env")
else:
    print("✅ API key loaded:", api_key)

# Test OpenAI request
try:
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("✅ OpenAI Response:", response["choices"][0]["message"]["content"])
except Exception as e:
    print("🚨 OpenAI API Error:", str(e))
