# app/llm/llm_client.py

import httpx
from app.core.config import get_settings

settings = get_settings()


class LLMClient:
    def __init__(self):
        self.api_url = settings.HF_API_URL
        self.api_key = settings.HF_API_KEY

    async def generate(self, messages: list):
        payload = {
            "model": settings.HF_MODEL_NAME,  # Example: "meta-llama/Meta-Llama-3-8B-Instruct"
            "messages": messages,
            "max_tokens": 256,
            "temperature": 0.3
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=40.0) as client:
            response = await client.post(self.api_url, json=payload, headers=headers)

        response.raise_for_status()
        data = response.json()

        # HF API responds like OpenAI: { choices: [ { message: { content: "..." } } ] }
        return data["choices"][0]["message"]["content"]
