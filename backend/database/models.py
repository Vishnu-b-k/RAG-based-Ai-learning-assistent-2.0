# backend/database/models.py
from sqlalchemy import Column, Integer, String, JSON, Float, DateTime
from datetime import datetime
from database.db import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    file_hash = Column(String, index=True, unique=True) # SHA256 for deduplication
    status = Column(String, default="UPLOADED") # UPLOADED, PROCESSING, READY, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, index=True)
    chunk_index = Column(Integer)
    content = Column(String)
    token_count = Column(Integer, default=0)

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, index=True)
    status = Column(String, default="PENDING") # PENDING, PROCESSING, READY, FAILED
    provider = Column(String, nullable=True)
    error = Column(String, nullable=True)
    retry_count = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

class DocumentAnalysis(Base):
    __tablename__ = "document_analysis"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, index=True)
    summary = Column(String, nullable=True)
    metadata_json = Column(JSON, default=dict)
    topics_json = Column(JSON, default=list)
    key_concepts_json = Column(JSON, default=list)
    learning_path_json = Column(JSON, default=list)
    analysis_version = Column(Integer, default=1)
    prompt_version = Column(Integer, default=1)
    provider = Column(String, nullable=True)
    model = Column(String, nullable=True)
    temperature = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class QuizQuestion(Base):
    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, index=True)
    question = Column(String)
    options_json = Column(JSON, default=list)
    answer_index = Column(Integer)
    explanation = Column(String)

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, index=True)
    front = Column(String)
    back = Column(String)
    difficulty = Column(String, default="mixed")

class ChatSession(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, index=True)
    collection_id = Column(String, index=True)
    history = Column(JSON, default=list) # List of {"role": "...", "content": "..."}
    progress = Column(JSON, default=dict) # {"Topic A": 20, "Topic B": 0}
    quiz_scores = Column(JSON, default=list) # List of quiz results
