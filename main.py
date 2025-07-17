from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from .api.routes import router as interview_router
from .services.pdf_service import PDFService
import os
import logging
import time
import tempfile
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cambridge CS Interview Practice",
    description="A tool for practicing Cambridge University Computer Science interviews",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(interview_router, prefix="/api", tags=["interview"])

# Initialize PDF service
pdf_service = PDFService()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request to {request.url.path} took {process_time:.2f} seconds")
    return response

@app.get("/")
async def root(request: Request):
    try:
        logger.info("Rendering index page")
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        raise

@app.get("/interview-report-form")
async def get_interview_report_form():
    pdf_path = os.path.join("app", "static", "pdfs", "interview_report_form.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Interview report form template not found")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="interview_report_form.pdf"
    )

@app.post("/generate-filled-report")
async def generate_filled_report(request: Request):
    try:
        # Get the request body
        body = await request.json()
        feedback_text = body.get("feedback_text", "")
        
        if not feedback_text:
            raise HTTPException(status_code=400, detail="No feedback text provided")
            
        logger.info("Generating filled report with feedback text")
        logger.debug(f"Feedback text: {feedback_text[:100]}...")  # Log first 100 chars
        
        # Parse the feedback text into structured data
        feedback_data = pdf_service.parse_feedback_text(feedback_text)
        logger.info(f"Parsed feedback data: {json.dumps(feedback_data, indent=2)}")
        
        # Create a temporary file for the filled PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            output_path = tmp.name
        
        # Fill the PDF form
        pdf_service.fill_interview_report(feedback_data, output_path)
        logger.info(f"Generated filled PDF at: {output_path}")
        
        # Return the filled PDF
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename="filled_interview_report.pdf"
        )
    except Exception as e:
        logger.error(f"Error generating filled report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
