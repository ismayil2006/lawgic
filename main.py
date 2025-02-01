from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import openai
import os
import io
import logging
from dotenv import load_dotenv  # Secure API key storage
from PyPDF2 import PdfReader  # For extracting text from PDFs
from reportlab.pdfgen import canvas  # For generating reports
import uuid  # To create unique filenames

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Enable CORS (Allow frontend requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend's actual domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Middleware to log requests
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Chatbot Request Model
class ChatRequest(BaseModel):
    message: str

# Chatbot Endpoint
@app.post("/chat")
async def chatbot(request: ChatRequest):
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")  # Secure API key retrieval
        messages = [
            {"role": "system", "content": "You are a helpful legal assistant."},
            {"role": "user", "content": request.message}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use "gpt-4" if available
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        return {"response": response["choices"][0]["message"]["content"].strip()}
    except Exception as e:
        return {"error": str(e)}

# File Upload Endpoint (PDF & TXT)
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith((".pdf", ".txt")):
            return {"error": "Only PDF and text files are supported."}

        if file.filename.endswith(".pdf"):
            contents = await file.read()
            pdf_reader = PdfReader(io.BytesIO(contents))
            text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        else:
            text = (await file.read()).decode("utf-8")

        return {
            "filename": file.filename,
            "extracted_text": text[:200],
            "word_count": len(text.split()),
        }
    except Exception as e:
        return {"error": str(e)}

# Generate PDF Report
@app.post("/generate-report")
async def generate_report(content: str):
    try:
        filename = f"report_{uuid.uuid4().hex}.pdf"
        filepath = f"./{filename}"

        pdf = canvas.Canvas(filepath)
        pdf.drawString(100, 750, "AI Legal Chatbot Report")
        pdf.drawString(100, 730, content)
        pdf.save()

        return FileResponse(filepath, media_type="application/pdf", filename=filename)
    except Exception as e:
        return {"error": str(e)}

# Home Endpoint
@app.get("/")
def home():
    return {"message": "Welcome to the AI Legal Chatbot Backend!"}
