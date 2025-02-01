from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from PyPDF2 import PdfReader  # Install via `pip install PyPDF2`
import io
import logging

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add CORS middleware (optional, for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to log requests and responses
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Chatbot Endpoint
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chatbot(request: ChatRequest):
    try:
        openai.api_key = "your_openai_api_key"  # Replace with your OpenAI API key
        # Add a legal-specific prompt for better responses
        legal_prompt = (
            "You are a helpful and knowledgeable legal assistant. "
            "Answer the user's question as clearly and concisely as possible.\n\n"
            f"User's question: {request.message}"
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=legal_prompt,
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return {"response": response.choices[0].text.strip()}
    except Exception as e:
        return {"error": str(e)}

# File Upload Endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Check file extension
        if not file.filename.endswith((".pdf", ".txt")):
            return {"error": "Only PDF and text files are supported."}
        
        # Process file based on type
        if file.filename.endswith(".pdf"):
            # Read and extract text from PDF
            contents = await file.read()
            pdf_reader = PdfReader(io.BytesIO(contents))
            text = " ".join(page.extract_text() for page in pdf_reader.pages)
        else:
            # Read plain text file
            text = (await file.read()).decode("utf-8")

        # Process extracted text as needed (e.g., save, analyze, etc.)
        return {"filename": file.filename, "extracted_text": text[:200]}  # Return first 200 chars
    except Exception as e:
        return {"error": str(e)}

# Home Endpoint
@app.get("/")
def home():
    return {"message": "Welcome to the AI Legal Chatbot Backend!"}
