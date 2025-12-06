# app/llm/llm_client.py

import json
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
        headers = {"Authorization": f"Bearer {self.api_key}"}
    

        async with httpx.AsyncClient(timeout=40.0) as client:
            response = await client.post(self.api_url, json=payload, headers=headers)

        response.raise_for_status()
        data = response.json()

        # HF API responds like OpenAI: { choices: [ { message: { content: "..." } } ] }
        return data["choices"][0]["message"]["content"]
    

    async def generate_stream(self, messages: list):
        payload = {
            "inputs": messages,
            "stream": True,
            "parameters": {
                "temperature": 0.3,
                "max_new_tokens": 256
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream"
        }

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct", json=payload, headers=headers) as r:
                async for line in r.aiter_lines():
                    if line.strip() == "" or not line.startswith("data:"):
                        continue

                    data = line[len("data: "):]
                    
                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)
                        token = chunk.get("token", {}).get("text", "")
                        if token:
                            yield token
                    except:
                        continue
