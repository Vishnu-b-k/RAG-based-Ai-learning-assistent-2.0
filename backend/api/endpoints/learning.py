# backend/api/endpoints/learning.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Document, DocumentAnalysis, QuizQuestion, ChatSession
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class QuizRequest(BaseModel):
    collection_id: str

class QuizQuestionSchema(BaseModel):
    question: str
    options: List[str]
    correctAnswerIndex: int
    explanation: str

class QuizResponse(BaseModel):
    questions: List[QuizQuestionSchema]

class MetadataResponse(BaseModel):
    collection_id: str
    filename: Optional[str]
    topics: List[str]
    suggested_questions: List[str]
    images: List[dict]

@router.get("/metadata/{collection_id}", response_model=MetadataResponse)
async def get_metadata(collection_id: str, db: Session = Depends(get_db)):
    try:
        doc = db.query(Document).filter(Document.id == collection_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
            
        analysis = db.query(DocumentAnalysis).filter(DocumentAnalysis.document_id == collection_id).first()
        
        # If analysis isn't ready yet, return empty fields gracefully
        topics = analysis.topics_json if analysis else []
        questions = analysis.key_concepts_json if analysis else [] # Mapping key concepts to suggested questions
        
        return {
            "collection_id": doc.id,
            "filename": doc.filename,
            "topics": topics,
            "suggested_questions": questions,
            "images": [] # Images removed in new schema, return empty for frontend compat
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
        analysis = db.query(DocumentAnalysis).filter(DocumentAnalysis.document_id == collection_id).first()
        session = db.query(ChatSession).filter(ChatSession.collection_id == collection_id).first()
        
        return {
            "topics": analysis.topics_json if analysis else [],
            "progress": session.progress if session else {},
            "quiz_scores": session.quiz_scores if session else []
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
            # Create session if missing
            session = ChatSession(id=f"sess_{collection_id}", collection_id=collection_id)
            db.add(session)
            
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
        analysis = db.query(DocumentAnalysis).filter(DocumentAnalysis.document_id == collection_id).first()
        if not analysis:
            return {"summary": "Summary is still being generated. Please wait."}
            
        return {"summary": analysis.summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest, db: Session = Depends(get_db)):
    try:
        quizzes = db.query(QuizQuestion).filter(QuizQuestion.document_id == request.collection_id).all()
        if not quizzes:
            return {"questions": []}
            
        formatted_questions = []
        for q in quizzes:
            formatted_questions.append({
                "question": q.question,
                "options": q.options_json,
                "correctAnswerIndex": q.answer_index,
                "explanation": q.explanation
            })
            
        return {"questions": formatted_questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
