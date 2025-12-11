# app/llm/llm_client.py

import json
import httpx
from app.core.config import get_settings

settings = get_settings()



class LLMClient:
    def __init__(self, api_url: str, api_key: str, model_name: str):
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name


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
        """Stream tokens from Hugging Face API"""
        
        # Ensure messages is in correct format
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        elif isinstance(messages, list) and messages and isinstance(messages[0], str):
            messages = [{"role": "user", "content": messages[0]}]
        
        # OpenAI-compatible payload
        payload = {
            "model": settings.HF_MODEL_NAME,
            "messages": messages,
            "stream": True,
            "max_tokens": 256,
            "temperature": 0.3
        }

        headers = {"Authorization": f"Bearer {self.api_key}"}
        

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                async with client.stream("POST", self.api_url, json=payload, headers=headers) as r:
                    print(f"DEBUG [llm_client]: Response status: {r.status_code}")
                    
                    if r.status_code != 200:
                        # Read error response
                        error_data = await r.aread()
                        error_text = error_data.decode('utf-8', errors='ignore')
                        print(f"DEBUG [llm_client]: API error: {error_text}")
                        yield f"Error {r.status_code}: {error_text[:100]}"
                        return
                    
                    async for line in r.aiter_lines():
                        line = line.strip()
                        if not line:
                            continue
                        
                        print(f"DEBUG [llm_client]: Raw line: {repr(line)}")
                        
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: "
                            
                            if data == "[DONE]":
                                print("DEBUG [llm_client]: Stream complete")
                                break
                            
                            try:
                                chunk = json.loads(data)
                                print(f"DEBUG [llm_client]: Parsed chunk: {chunk}")
                                
                                # OpenAI stream format
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    token = delta.get("content", "")
                                    if token:
                                        yield token
                                # Alternative format
                                elif "content" in chunk:
                                    yield chunk["content"]
                                elif "text" in chunk:
                                    yield chunk["text"]
                                elif "token" in chunk and "text" in chunk["token"]:
                                    yield chunk["token"]["text"]
                                else:
                                    print(f"DEBUG [llm_client]: Unexpected format: {chunk}")
                                    
                            except json.JSONDecodeError as e:
                                print(f"DEBUG [llm_client]: JSON error: {e}, data: {data}")
                                # If not JSON, try as plain text
                                if data and data != "[DONE]":
                                    yield data
                    
            except Exception as e:
                print(f"DEBUG [llm_client]: Exception: {e}")
                yield f"Connection error: {str(e)}"