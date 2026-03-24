# backend/api/endpoints/learning.py
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from services.llm_service import LLMService
from services.retrieval_service import RetrievalService
from database.db import get_db
from database.models import CollectionMeta, ChatSession
from pydantic import BaseModel
from typing import List, Optional
import json
import re

router = APIRouter()
llm_svc = LLMService()

class QuizRequest(BaseModel):
    collection_id: str

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correctAnswerIndex: int
    explanation: str

class QuizResponse(BaseModel):
    questions: List[QuizQuestion]

class MetadataResponse(BaseModel):
    collection_id: str
    filename: Optional[str]
    topics: List[str]
    suggested_questions: List[str]
    images: List[dict]

@router.get("/metadata/{collection_id}", response_model=MetadataResponse)
async def get_metadata(collection_id: str, db: Session = Depends(get_db)):
    try:
        meta = db.query(CollectionMeta).filter(CollectionMeta.id == collection_id).first()
        if not meta:
            raise HTTPException(status_code=404, detail="Collection not found")
            
        # If topics or suggested questions are empty, generate them
        if not meta.topics or not meta.suggested_questions:
            docs = meta.chunks[:10] if meta.chunks else []
            context = "\n".join(docs)
            
            prompt = (
                "Based on this transcript, provide a JSON object with two keys:\n"
                "- 'topics': a list of 3-5 main topics covered.\n"
                "- 'questions': a list of 3 thought-provoking questions a student might ask.\n"
            )
            raw = await llm_svc.generate_answer(prompt, context)
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            data = json.loads(match.group(0)) if match else json.loads(raw)
            
            meta.topics = data.get("topics", [])
            meta.suggested_questions = data.get("questions", [])
            
            db.commit()
            
        return {
            "collection_id": meta.id,
            "filename": meta.filename,
            "topics": meta.topics,
            "suggested_questions": meta.suggested_questions,
            "images": meta.images or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AnalyticsResponse(BaseModel):
    topics: List[str]
    progress: dict
    quiz_scores: List[dict]

@router.get("/analytics/{collection_id}", response_model=AnalyticsResponse)
async def get_analytics(collection_id: str, db: Session = Depends(get_db)):
    try:
        meta = db.query(CollectionMeta).filter(CollectionMeta.id == collection_id).first()
        session = db.query(ChatSession).filter(ChatSession.collection_id == collection_id).first()
        
        if not meta or not session:
            raise HTTPException(status_code=404, detail="Data not found")
            
        return {
            "topics": meta.topics or [],
            "progress": session.progress or {},
            "quiz_scores": session.quiz_scores or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class QuizScoreRequest(BaseModel):
    score: float
    correct: int
    total: int
    topic: str

@router.post("/analytics/{collection_id}/score")
async def save_quiz_score(collection_id: str, request: QuizScoreRequest, db: Session = Depends(get_db)):
    try:
        session = db.query(ChatSession).filter(ChatSession.collection_id == collection_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        current_scores = session.quiz_scores.copy() if session.quiz_scores else []
        current_scores.append({
            "score": request.score,
            "correct": request.correct,
            "total": request.total,
            "topic": request.topic
        })
        session.quiz_scores = current_scores
        db.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{collection_id}")
async def get_summary(collection_id: str, level: str = "detailed", db: Session = Depends(get_db)):
    try:
        meta = db.query(CollectionMeta).filter(CollectionMeta.id == collection_id).first()
        if not meta:
            raise HTTPException(status_code=404, detail="Collection not found")
            
        docs = meta.chunks[:20] if meta.chunks else []
        context = "\n".join(docs)
        
        prompt = f"Summarize this lecture transcript at a {level} level. Use markdown formatting."
        summary = await llm_svc.generate_answer(prompt, context)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest, db: Session = Depends(get_db)):
    try:
        meta = db.query(CollectionMeta).filter(CollectionMeta.id == request.collection_id).first()
        if not meta:
            raise HTTPException(status_code=404, detail="Collection not found")
            
        docs = meta.chunks[:20] if meta.chunks else []
        context = "\n".join(docs)
        
        system = (
            "Generate 5 multiple-choice questions STRICTLY and EXCLUSIVELY based on the provided transcript below.\n"
            "DO NOT include any questions that cannot be answered using ONLY the transcript text.\n"
            "If the transcript is too short or empty, return basic comprehension questions strictly limited to the text shown.\n"
            "Return a JSON object with a 'questions' key containing the list of question objects.\n"
            "Each object must have 'question', 'options' (array of 4 distinct plausible strings), "
            "'correctAnswerIndex' (integer 0-3), and 'explanation' (explaining why based on the transcript)."
        )
        raw = await llm_svc.generate_answer(system, context)
        
        # Clean JSON and parse
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(match.group(0)) if match else json.loads(raw)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
