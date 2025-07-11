from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid


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

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.post("/generate-clause")
async def generate_clause(req: ClauseRequest):
    if not OPENAI_API_KEY:
        return JSONResponse(status_code=500, content={"error": "OpenAI API key not set in environment."})
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=512,
            temperature=0.3,
            api_key=OPENAI_API_KEY
        )
        clause = response.choices[0].message['content'].strip()
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
