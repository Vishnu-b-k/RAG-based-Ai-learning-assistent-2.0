# backend/models/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class IngestionResponse(BaseModel):
    status: str
    filename: str
    collection_id: str
    chunks_count: int
    images_count: int

class ChatRequest(BaseModel):
    query: str
    session_id: str
    collection_name: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    session_id: str
