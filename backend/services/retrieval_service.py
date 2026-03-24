# backend/services/retrieval_service.py
import logging
from typing import List
from rank_bm25 import BM25Okapi

class RetrievalService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def _tokenize(self, text: str) -> List[str]:
        # Simple whitespace tokenization, lowercased.
        return text.lower().split()

    def hybrid_search(self, query: str, documents: List[str], top_k: int = 10) -> List[str]:
        """
        Ultra-fast BM25 Lexical search (replacing semantic search).
        Takes a list of documents directly from SQLite.
        """
        if not documents:
            return []
            
        tokenized_corpus = [self._tokenize(doc) for doc in documents]
        bm25 = BM25Okapi(tokenized_corpus)
        
        tokenized_query = self._tokenize(query)
        # get_top_n returns the actual documents
        top_docs = bm25.get_top_n(tokenized_query, documents, n=top_k)
        
        self.logger.info(f"Retrieved {len(top_docs)} chunks using BM25 for query.")
        return top_docs
