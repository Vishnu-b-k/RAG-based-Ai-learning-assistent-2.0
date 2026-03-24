# backend/services/llm_service.py
import os
from openai import AsyncOpenAI
from typing import Optional

class LLMService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = "google/gemini-2.0-flash-001"

    async def generate_answer(self, query: str, context: str) -> str:
        """Asynchronous call to the LLM with grounded context."""
        system_prompt = (
            "You are a highly capable AI Learning Assistant and academic tutor. "
            "Use the provided lecture context as the primary foundation for your answer. "
            "HOWEVER, if the student asks a conceptual question or requests further explanation "
            "beyond what is explicitly stated in the text, you MUST use your broad external knowledge "
            "to explain it clearly and helpfully. NEVER just say 'the text doesn't contain the answer' "
            "when you can provide a helpful educational explanation."
        )
        user_prompt = f"Context:\n{context}\n\nQuestion: {query}"
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3, # Professional/Consistent
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
