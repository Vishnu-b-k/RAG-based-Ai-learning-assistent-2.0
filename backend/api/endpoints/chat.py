# backend/api/endpoints/chat.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from services.retrieval_service import RetrievalService
from services.ai_provider import AIProviderManager
from database.db import get_db
from database.models import Document, DocumentChunk, DocumentAnalysis, ChatSession
from models.schemas import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/query", response_model=ChatResponse)
async def process_query(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        doc = db.query(Document).filter(Document.id == request.collection_name).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        # Get chunks
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == request.collection_name).order_by(DocumentChunk.chunk_index).all()
        chunk_texts = [c.content for c in chunks]
        
        if not chunk_texts:
            raise HTTPException(status_code=404, detail="No chunks found for document.")

        # 1. Retrieval (BM25)
        retrieval_svc = RetrievalService()
        context_docs = retrieval_svc.hybrid_search(
            query=request.query, 
            documents=chunk_texts,
            top_k=5
        )
        context = "\n\n---\n\n".join(context_docs)
        
        # 2. Generation using new fallback manager
        manager = AIProviderManager()
        answer, provider_used = await manager.chat(request.query, context)
        
        # 3. Update Progress and History in DB
        analysis = db.query(DocumentAnalysis).filter(DocumentAnalysis.document_id == request.collection_name).first()
        session = db.query(ChatSession).filter(ChatSession.collection_id == request.collection_name).first()
        
        if not session:
            session = ChatSession(id=f"sess_{request.collection_name}", collection_id=request.collection_name)
            db.add(session)
            
        # Append History
        current_history = session.history.copy() if session.history else []
        current_history.append({"role": "user", "content": request.query})
        current_history.append({"role": "assistant", "content": answer})
        session.history = current_history
        
        # Update Progress
        progress = session.progress.copy() if session.progress else {}
        combined_text = (request.query + " " + answer).lower()
        
        topics = analysis.topics_json if analysis else []
        for topic in topics:
            if topic.lower() in combined_text:
                old_score = progress.get(topic, 0)
                progress[topic] = min(old_score + 10, 100)
        session.progress = progress
        db.commit()
            
        return ChatResponse(
            answer=answer,
            sources=context_docs[:3],
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class HistoryResponse(BaseModel):
    history: list

@router.get("/history/{collection_id}", response_model=HistoryResponse)
async def get_history(collection_id: str, db: Session = Depends(get_db)):
    try:
        session = db.query(ChatSession).filter(ChatSession.collection_id == collection_id).first()
        if not session:
            return {"history": []}
        return {"history": session.history or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
