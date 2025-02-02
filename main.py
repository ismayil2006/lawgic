from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import openai
import os
from fpdf import FPDF
from dotenv import load_dotenv

import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# ✅ Load lawyer data
with open("lawyers.json", "r") as file:
    LAWYERS = json.load(file)

app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LawyerRequest(BaseModel):
    location: str
    category: str
    range: int

@app.post("/find-lawyer")
async def find_lawyer(request: LawyerRequest):
    user_location = request.location.lower()
    category = request.category
    max_distance = int(request.range)

    # ✅ Filter lawyers based on category
    filtered_lawyers = [
        lawyer for lawyer in LAWYERS
        if lawyer["specialty"] == category and user_location in lawyer["location"].lower()
    ]

    if not filtered_lawyers:
        return {"lawyers": []}

    return {"lawyers": filtered_lawyers}

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
openai.api_key = "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"

if not openai.api_key:
    raise RuntimeError("❌ OpenAI API Key is missing! Set it in the .env file.")

# ✅ Chat Request Model
class ChatRequest(BaseModel):
    messages: list[dict]

# ✅ Lawyer Referral Request Model
class LawyerRequest(BaseModel):
    messages: list[dict]

# ✅ PDF Report Request Model
class PDFRequest(BaseModel):
    messages: list[dict]  # Retain all chat messages

# ✅ Chat Endpoint (Multiturn)
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        request.messages = request.messages[-10:]  # Retain last 10 messages for efficiency

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=request.messages,
            max_tokens=300,
            temperature=0.7,
        )

        response_text = response.choices[0].message.content  
        return {"response": response_text}

    except Exception as e:
        return {"error": f"🚨 OpenAI API Error: {str(e)}"}

# ✅ Generate PDF Report
@app.post("/generate-report")
async def generate_report():
    try:
        # ✅ Disclaimer text only
        disclaimer = """DISCLAIMER:
This document is generated for informational purposes only. 
It does not constitute legal advice, and no information contained 
herein may be used for self-incrimination or as evidence in any legal proceeding.
"""

        # ✅ Generate PDF with just the disclaimer
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, disclaimer, border=0, align='C')

        # ✅ Save and return the PDF
        pdf_filename = "disclaimer.pdf"
        pdf.output(pdf_filename)

        return FileResponse(pdf_filename, media_type="application/pdf", filename="disclaimer.pdf")

    except Exception as e:
        print(f"🚨 PDF Report Generation Error: {e}")
        return {"error": f"🚨 PDF Report Generation Error: {str(e)}"}

# ✅ Dummy Lawyer Database (Replace with real API later)
LAWYERS_DB = {
    "family law": [
        {"name": "John Doe", "specialty": "Family Law", "location": "Chapel Hill, NC", "contact": "919-123-4567"},
        {"name": "Emily Smith", "specialty": "Divorce Attorney", "location": "Raleigh, NC", "contact": "984-987-6543"},
    ],
    "immigration": [
        {"name": "David Patel", "specialty": "Immigration Law", "location": "Durham, NC", "contact": "919-555-7890"},
    ],
    "criminal defense": [
        {"name": "Sarah Johnson", "specialty": "Criminal Defense", "location": "Chapel Hill, NC", "contact": "919-888-9999"},
    ],
}

# ✅ Lawyer Referral Endpoint
@app.post("/find-lawyer")
async def find_lawyer(request: LawyerRequest):
    try:
        messages = request.messages  # Retrieve conversation history

        # ✅ Use AI to determine legal topic from chat history
        analysis_prompt = f"""
        Analyze the following conversation and determine the primary legal issue:
        {messages}
        
        Respond with only one category: "family law", "immigration", "criminal defense", or "other".
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an AI that determines legal issues from conversations."},
                      {"role": "user", "content": analysis_prompt}],
            max_tokens=10
        )

        legal_topic = response.choices[0].message.content.strip().lower()

        # ✅ Retrieve lawyers based on identified legal topic
        if legal_topic in LAWYERS_DB:
            lawyer_list = LAWYERS_DB[legal_topic]
        else:
            lawyer_list = []

        return {"lawyers": lawyer_list}

    except Exception as e:
        print(f"🚨 Lawyer Referral Error: {e}")
        return {"error": f"🚨 Lawyer Referral Error: {str(e)}"}
