from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
import os
import uuid
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai import Credentials

load_dotenv()

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClauseRequest(BaseModel):
    clause_type: str
    prompt: str
    examples: Optional[List[str]] = None

class ExportRequest(BaseModel):
    clause_text: str
    export_type: str  # 'word' or 'pdf'


WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("WATSONX_URL")

@app.post("/generate-clause")
async def generate_clause(req: ClauseRequest):
    if not WATSONX_API_KEY or not WATSONX_PROJECT_ID or not WATSONX_URL:
        return JSONResponse(status_code=500, content={"error": "WatsonX credentials not set in environment."})

    prompt_parts = [
        f"You are a legal expert. Write a {req.clause_type} clause for a contract.",
        f"Prompt: {req.prompt}",
    ]
    if req.examples:
        for i, ex in enumerate(req.examples, 1):
            if ex.strip():
                prompt_parts.append(f"Example {i}: {ex}")
    prompt_text = "\n".join(prompt_parts)

    try:
        creds = Credentials(api_key=WATSONX_API_KEY, url=WATSONX_URL, project_id=WATSONX_PROJECT_ID)
        model = Model("ibm/granite-3-3-8b-instruct", credentials=creds)
        response = model.generate(prompt=prompt_text, max_new_tokens=512, temperature=0.3)
        clause = response['results'][0]['generated_text'].strip()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    return {"clause": clause}

@app.post("/export")
async def export_clause(req: ExportRequest):
    # Export clause_text as Word or PDF
    filename = f"clause_{uuid.uuid4()}"
    if req.export_type == 'word':
        from docx import Document
        doc = Document()
        doc.add_paragraph(req.clause_text)
        path = f"/tmp/{filename}.docx"
        doc.save(path)
        return FileResponse(path, filename="clause.docx")
    elif req.export_type == 'pdf':
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        path = f"/tmp/{filename}.pdf"
        c = canvas.Canvas(path, pagesize=letter)
        c.drawString(100, 750, req.clause_text)
        c.save()
        return FileResponse(path, filename="clause.pdf")
    else:
        return JSONResponse(status_code=400, content={"error": "Invalid export type"})

@app.get("/")
def root():
    return {"message": "Legal Clause Generator Backend"}
