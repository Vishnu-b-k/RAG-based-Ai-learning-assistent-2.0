# backend/services/pipeline_service.py
import logging
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import (
    Document,
    AnalysisJob,
    DocumentAnalysis,
    QuizQuestion,
    Flashcard
)
from services.ai_provider import AIProviderManager

logger = logging.getLogger(__name__)

async def run_analysis_pipeline(document_id: str, text: str):
    """Background worker to analyze a document and save derived data."""
    db: Session = SessionLocal()
    try:
        # Mark Job as PROCESSING
        job = db.query(AnalysisJob).filter(AnalysisJob.document_id == document_id).first()
        doc = db.query(Document).filter(Document.id == document_id).first()
        
        if not job or not doc:
            logger.error(f"Cannot find job or document for {document_id}")
            return
            
        job.status = "PROCESSING"
        job.started_at = datetime.utcnow()
        doc.status = "PROCESSING"
        db.commit()

        # Execute AI Analysis
        manager = AIProviderManager()
        result_json, provider_used = await manager.analyze_document(text)
        
        # Save Document Analysis
        analysis_record = DocumentAnalysis(
            id=f"analysis_{uuid.uuid4().hex[:8]}",
            document_id=document_id,
            summary=result_json.get("summary", ""),
            metadata_json=result_json.get("metadata", {}),
            topics_json=result_json.get("topics", []),
            key_concepts_json=result_json.get("key_concepts", []),
            learning_path_json=result_json.get("learning_path", []),
            provider=provider_used,
            model="auto",
            prompt_version=1,
            analysis_version=1
        )
        db.add(analysis_record)

        # Save Quizzes
        quizzes = result_json.get("quiz", [])
        for q in quizzes:
            q_record = QuizQuestion(
                id=f"quiz_{uuid.uuid4().hex[:8]}",
                document_id=document_id,
                question=q.get("question", ""),
                options_json=q.get("options", []),
                answer_index=q.get("answer_index", 0),
                explanation=q.get("explanation", "")
            )
            db.add(q_record)

        # Save Flashcards
        flashcards = result_json.get("flashcards", [])
        for f in flashcards:
            f_record = Flashcard(
                id=f"fc_{uuid.uuid4().hex[:8]}",
                document_id=document_id,
                front=f.get("front", ""),
                back=f.get("back", ""),
                difficulty=f.get("difficulty", "mixed")
            )
            db.add(f_record)
            
        # Update Status to READY
        job.status = "READY"
        job.finished_at = datetime.utcnow()
        job.provider = provider_used
        doc.status = "READY"
        
        db.commit()
        logger.info(f"Analysis complete for document {document_id} via {provider_used}")

    except Exception as e:
        logger.error(f"Analysis pipeline failed for {document_id}: {e}", exc_info=True)
        # Mark as FAILED
        try:
            db.rollback()
            job = db.query(AnalysisJob).filter(AnalysisJob.document_id == document_id).first()
            doc = db.query(Document).filter(Document.id == document_id).first()
            if job:
                job.status = "FAILED"
                job.error = str(e)
                job.finished_at = datetime.utcnow()
            if doc:
                doc.status = "FAILED"
            db.commit()
        except Exception as rollback_err:
            logger.error(f"Failed to save error state for {document_id}: {rollback_err}")
    finally:
        db.close()
