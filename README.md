# AI Learning Assistant — Production-Grade Rebuild

This is an upgraded, production-level version of the Lecture Transcript Knowledge Base. It moves from a monolithic Streamlit app to a modern, scalable full-stack architecture.

## 🚀 Key Upgrades
- **Backend Architecture**: FastAPI for asynchronous performance and API-first design.
- **Frontend Architecture**: Next.js (planned) for a premium, responsive UI.
- **Advanced Retrieval**: Hybrid Search (BM25 + Semantic) and Cross-Encoder Reranking for superior accuracy.
- **Persistence**: Persistent ChromaDB and SQLite for session and history management.
- **Modular Code**: Clear separation of concerns between API, Services, Models, and Database.

## 📁 Project Structure
- `/backend`: Core API logic and services.
  - `/api`: REST endpoint definitions.
  - `/services`: RAG logic (Retrieval, LLM, PDF processing).
  - `/models`: Data validation and schema.
- `/data`: Local persistent storage for vector and relational databases.
- `/frontend`: Next.js client application.

## 🛠️ Getting Started (Backend)
1. Navigate to `backend/`
2. Install dependencies: `pip install -r requirements.txt`
3. Set your environment variable: `OPENROUTER_API_KEY`
4. Run the server: `python main.py` or `uvicorn main:app --reload`

Access the interactive API documentation at `http://localhost:8000/docs`.
