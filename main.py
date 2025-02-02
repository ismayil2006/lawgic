from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

app = FastAPI()

# ✅ Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Retrieve OpenAI API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Debugging: Print the API key being used
print("🔍 OpenAI API Key Used:", openai.api_key)

if not openai.api_key:
    raise RuntimeError("❌ OpenAI API Key is missing! Set it in the .env file.")

class ChatRequest(BaseModel):
    messages: list[dict]

# ✅ Chat Endpoint with OpenAI API Fix
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        request.messages = request.messages[-5:]  # Keep only last 5 messages for optimization

        print("🔍 Sending to OpenAI:", request.messages)  # Debugging Log

        # ✅ Use the correct OpenAI API format for `openai>=1.0.0`
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=request.messages,
            max_tokens=200,
            temperature=0.7,
        )

        response_text = response.choices[0].message.content  # ✅ Extract Correctly

        print("✅ OpenAI Response:", response_text)  # Debugging Log

        return {"response": response_text}

    except Exception as e:
        print("🚨 OpenAI API Error:", e)  # Print the exact error
        return {"error": f"🚨 OpenAI API Error: {str(e)}"}

# ✅ Upload PDF with Analysis Prompt
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), prompt: str = Form(...)):
    try:
        return {"filename": file.filename, "prompt": prompt}
    except Exception as e:
        return {"error": f"🚨 PDF Upload Error: {str(e)}"}

# ✅ Generate PDF Report
@app.post("/generate-report")
async def generate_report(content: str):
    return {"report": "PDF Report Generated with content: " + content}
