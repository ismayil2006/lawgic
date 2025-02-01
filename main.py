from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import openai
import os
import io
import logging
from dotenv import load_dotenv  # For loading API keys securely
from PyPDF2 import PdfReader  # For PDF text extraction
from reportlab.pdfgen import canvas  # For generating reports
import uuid  # For unique report filenames

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS for frontend communication (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        openai.api_key = os.getenv("OPENAI_API_KEY")  # Load API key from .env
        messages = [
            {"role": "system", "content": "You are a helpful and knowledgeable legal assistant. Answer the user's question as clearly and concisely as possible."},
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

# File Upload Endpoint (Handles PDF & TXT)
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Check file extension
        if not file.filename.endswith((".pdf", ".txt")):
            return {"error": "Only PDF and text files are supported."}
        
        # Process file content
        if file.filename.endswith(".pdf"):
            contents = await file.read()
            pdf_reader = PdfReader(io.BytesIO(contents))
            text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        else:
            text = (await file.read()).decode("utf-8")

        # Return summary of extracted text
        return {
            "filename": file.filename,
            "extracted_text": text[:200],  # Return first 200 characters
            "word_count": len(text.split()),  # Provide word count
        }
    except Exception as e:
        return {"error": str(e)}

# Generate PDF Report
@app.post("/generate-report")
async def generate_report(content: str):
    try:
        filename = f"report_{uuid.uuid4().hex}.pdf"
        filepath = f"./{filename}"

        # Create PDF
        pdf = canvas.Canvas(filepath)
        pdf.drawString(100, 750, "AI Legal Chatbot Report")
        pdf.drawString(100, 730, content)
        pdf.save()

        # Return PDF file for download
        return FileResponse(filepath, media_type="application/pdf", filename=filename)
    except Exception as e:
        return {"error": str(e)}

# Home Endpoint
@app.get("/")
def home():
    return {"message": "Welcome to the AI Legal Chatbot Backend!"}
