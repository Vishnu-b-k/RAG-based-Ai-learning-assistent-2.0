# backend/database/models.py
from sqlalchemy import Column, Integer, String, JSON, Float
from database.db import Base

class CollectionMeta(Base):
    __tablename__ = "collections"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    topics = Column(JSON) # List of strings
    suggested_questions = Column(JSON) # List of strings
    images = Column(JSON) # List of dicts: {"url": "...", "caption": "...", "page": ...}
    chunks = Column(JSON, default=list) # List of text fragments for BM25

class ChatSession(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, index=True)
    collection_id = Column(String, index=True)
    history = Column(JSON, default=list) # List of {"role": "...", "content": "..."}
    progress = Column(JSON, default=dict) # {"Topic A": 20, "Topic B": 0}
    quiz_scores = Column(JSON, default=list) # List of quiz results
