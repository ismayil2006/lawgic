from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: list[dict]

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")

        # Keep only the last 5 messages for faster processing
        request.messages = request.messages[-5:]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Faster than GPT-4
            messages=request.messages,
            max_tokens=200,  # Limit response length for speed
            temperature=0.7,
            stream=True  # Enable real-time streaming
        )

        response_text = ""
        for chunk in response:
            if "choices" in chunk and chunk["choices"][0]["delta"].get("content"):
                response_text += chunk["choices"][0]["delta"]["content"]

        return {"response": response_text}
    except Exception as e:
        return {"error": str(e)}

# Upload PDF with Analysis Prompt
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), prompt: str = Form(...)):
    try:
        return {"filename": file.filename, "prompt": prompt}
    except Exception as e:
        return {"error": str(e)}

# Generate PDF Report
@app.post("/generate-report")
async def generate_report(content: str):
    return {"report": "PDF Report Generated with content: " + content}
