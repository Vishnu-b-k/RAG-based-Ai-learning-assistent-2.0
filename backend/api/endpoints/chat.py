# backend/api/endpoints/chat.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from services.retrieval_service import RetrievalService
from services.llm_service import LLMService
from database.db import get_db
from database.models import CollectionMeta, ChatSession
from models.schemas import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/query", response_model=ChatResponse)
async def process_query(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Retrieve Meta
        meta = db.query(CollectionMeta).filter(CollectionMeta.id == request.collection_name).first()
        if not meta or not meta.chunks:
            raise HTTPException(status_code=404, detail="Collection not found or empty.")

        # 1. Retrieval (BM25)
        retrieval_svc = RetrievalService()
        context_docs = retrieval_svc.hybrid_search(
            query=request.query, 
            documents=meta.chunks,
            top_k=5
        )
        context = "\n\n---\n\n".join(context_docs)
        
        # 2. Generation
        llm_svc = LLMService()
        answer = await llm_svc.generate_answer(request.query, context)
        
        # 3. Update Progress and History in DB
        meta = db.query(CollectionMeta).filter(CollectionMeta.id == request.collection_name).first()
        session = db.query(ChatSession).filter(ChatSession.collection_id == request.collection_name).first()
        
        if meta and session:
            # Append History
            current_history = session.history.copy()
            current_history.append({"role": "user", "content": request.query})
            current_history.append({"role": "assistant", "content": answer})
            session.history = current_history
            
            # Update Progress
            progress = session.progress.copy()
            combined_text = (request.query + " " + answer).lower()
            for topic in meta.topics:
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
