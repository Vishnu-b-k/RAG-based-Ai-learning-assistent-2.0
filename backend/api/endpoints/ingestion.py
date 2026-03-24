# backend/api/endpoints/ingestion.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from services.pdf_service import PDFService
from database.db import get_db
from database.models import CollectionMeta, ChatSession
import uuid
import os

router = APIRouter()
pdf_svc = PDFService()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        content = await file.read()
        
        # 1. Extraction
        text, images = pdf_svc.extract_text_and_images(content)
        
        # 2. Chunking
        chunks = pdf_svc.recursive_split(text)
        
        # 3. Generating Collection ID
        collection_id = f"doc_{uuid.uuid4().hex[:8]}"
        
        # 4. Save Images and build metadata
        saved_images = []
        for idx, img in enumerate(images):
            img_filename = f"{collection_id}_{idx}.{img['ext']}"
            img_path = os.path.join("./data/images", img_filename)
            with open(img_path, "wb") as f:
                f.write(img["bytes"])
            saved_images.append({
                "url": f"/images/{img_filename}",
                "caption": img["caption"],
                "page": img["page"]
            })
            
        # 5. Save to Database
        db_collection = CollectionMeta(
            id=collection_id,
            filename=file.filename,
            topics=[],
            suggested_questions=[],
            images=saved_images,
            chunks=chunks
        )
        db.add(db_collection)
        
        # Initialize default chat session for this collection
        db_session = ChatSession(
            id=f"sess_{uuid.uuid4().hex[:8]}",
            collection_id=collection_id,
            progress={},
            history=[],
            quiz_scores=[]
        )
        db.add(db_session)
        
        db.commit()
        
        return {
            "status": "success",
            "filename": file.filename,
            "collection_id": collection_id,
            "session_id": db_session.id,
            "chunks_count": len(chunks),
            "images_count": len(images)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
