# backend/main.py
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.endpoints import chat, ingestion, learning
from database.db import engine, Base
import os

# Initialize Database
Base.metadata.create_all(bind=engine)
os.makedirs("./data/images", exist_ok=True)

app = FastAPI(
    title="AI Learning Assistant API",
    description="Production-grade RAG API for lecture transcript analysis.",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(ingestion.router, prefix="/api/v1/ingestion", tags=["Ingestion"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(learning.router, prefix="/api/v1/learning", tags=["Learning"])

# Mount static files for Extracted Figures
app.mount("/images", StaticFiles(directory="./data/images"), name="images")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
