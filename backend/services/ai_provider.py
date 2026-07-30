import os
import json
import asyncio
import logging
import re
from abc import ABC, abstractmethod
from typing import Dict, Any
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

MASTER_PROMPT = """Analyze this document and extract key learning components.
Return a STRICT JSON object matching exactly this schema, and nothing else. Ensure output limits are respected:
{
  "summary": "max 300 words summary of the document",
  "metadata": {"author": "unknown", "date": "unknown", "type": "lecture/article"},
  "topics": ["list of 5 to 10 main topics"],
  "key_concepts": ["list of 10 key concepts defined in the text"],
  "learning_path": ["step 1", "step 2", "step 3"],
  "flashcards": [
    {"front": "concept", "back": "definition", "difficulty": "mixed"}
  ],
  "quiz": [
    {"question": "...", "options": ["A", "B", "C", "D"], "answer_index": 0, "explanation": "..."}
  ]
}
Flashcards limit: maximum 15.
Quiz limit: exactly 10 questions.
"""

def extract_json(raw: str) -> Dict[str, Any]:
    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from LLM: {e}")
        raise ValueError("Invalid JSON returned by LLM")

class AIProvider(ABC):
    @abstractmethod
    async def analyze_document(self, text: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def chat(self, query: str, context: str) -> str:
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def is_configured(self) -> bool:
        pass

class BaseOpenAIProvider(AIProvider):
    def __init__(self, name: str, api_key_env: str, base_url: str, model: str):
        self._name = name
        self.api_key = os.environ.get(api_key_env)
        self.base_url = base_url
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url) if self.api_key else None

    @property
    def name(self) -> str:
        return self._name
        
    @property
    def is_configured(self) -> bool:
        return self.client is not None

    async def analyze_document(self, text: str) -> Dict[str, Any]:
        if not self.is_configured:
            raise ValueError(f"{self.name} is not configured.")
            
        user_prompt = f"Document Text:\n{text[:20000]}" # Guard against massive docs for now
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": MASTER_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return extract_json(response.choices[0].message.content.strip())

    async def chat(self, query: str, context: str) -> str:
        if not self.is_configured:
            raise ValueError(f"{self.name} is not configured.")
            
        system = "You are an AI Learning Assistant. Use the provided context to answer."
        user_prompt = f"Context:\n{context}\n\nQuestion: {query}"
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

class GroqProvider(BaseOpenAIProvider):
    def __init__(self):
        super().__init__(
            name="Groq",
            api_key_env="GROQ_API_KEY",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.3-70b-versatile"
        )

class OpenRouterProvider(BaseOpenAIProvider):
    def __init__(self):
        super().__init__(
            name="OpenRouter",
            api_key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            model="google/gemini-3.5-flash"
        )
        
class GeminiProvider(BaseOpenAIProvider):
    def __init__(self):
        super().__init__(
            name="Gemini",
            api_key_env="GEMINI_API_KEY",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            model="gemini-2.5-flash"
        )

class AIProviderManager:
    def __init__(self):
        self.providers = [
            GroqProvider(),
            OpenRouterProvider(),
            GeminiProvider()
        ]

    async def execute_with_fallback(self, func_name: str, *args, **kwargs) -> Any:
        last_error = None
        for provider in self.providers:
            if not provider.is_configured:
                logger.warning(f"Skipping {provider.name}: API key missing.")
                continue
                
            retries = 2
            for attempt in range(retries):
                try:
                    logger.info(f"Attempting {func_name} with {provider.name} (Attempt {attempt+1}/{retries})")
                    func = getattr(provider, func_name)
                    return await func(*args, **kwargs), provider.name
                except Exception as e:
                    last_error = e
                    logger.warning(f"{provider.name} failed during {func_name}: {e}")
                    await asyncio.sleep(1) # Short delay before retry
        
        raise RuntimeError(f"All AI providers failed. Last error: {last_error}")

    async def analyze_document(self, text: str) -> tuple[Dict[str, Any], str]:
        return await self.execute_with_fallback("analyze_document", text)

    async def chat(self, query: str, context: str) -> tuple[str, str]:
        return await self.execute_with_fallback("chat", query, context)
