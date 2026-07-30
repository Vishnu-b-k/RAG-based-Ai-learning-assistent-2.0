# backend/api/endpoints/ingestion.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from services.pdf_service import PDFService
from database.db import get_db
from database.models import Document, DocumentChunk, AnalysisJob
from services.pipeline_service import run_analysis_pipeline
import uuid
import hashlib

router = APIRouter()
pdf_svc = PDFService()

@router.post("/upload")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        content = await file.read()
        
        # Deduplication using SHA256
        file_hash = hashlib.sha256(content).hexdigest()
        existing_doc = db.query(Document).filter(Document.file_hash == file_hash).first()
        if existing_doc:
            return {
                "status": "success",
                "message": "Document already exists.",
                "document_id": existing_doc.id,
                "doc_status": existing_doc.status
            }
        
        # 1. Extraction & Chunking
        text, images = pdf_svc.extract_text_and_images(content)
        chunks = pdf_svc.recursive_split(text)
        
        # 2. Database Insertion
        document_id = f"doc_{uuid.uuid4().hex[:8]}"
        new_doc = Document(
            id=document_id,
            filename=file.filename,
            file_hash=file_hash,
            status="UPLOADED"
        )
        db.add(new_doc)
        
        for idx, chunk_text in enumerate(chunks):
            db.add(DocumentChunk(
                id=f"chk_{uuid.uuid4().hex[:8]}",
                document_id=document_id,
                chunk_index=idx,
                content=chunk_text,
                token_count=len(chunk_text.split()) # simple token estimate
            ))
            
        new_job = AnalysisJob(
            id=f"job_{uuid.uuid4().hex[:8]}",
            document_id=document_id,
            status="PENDING"
        )
        db.add(new_job)
        db.commit()
        
        # 3. Queue Background Analysis
        background_tasks.add_task(run_analysis_pipeline, document_id, text)
        
        return {
            "status": "success",
            "message": "Analysis queued.",
            "document_id": document_id,
            "doc_status": "PROCESSING"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/status/{document_id}")
async def get_status(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document_id": doc.id, "status": doc.status}
