import json
from app.services.llm.llm_client import LLMClient


class ParamExtractor:
    """Extracts parameters for intents using LLM."""
    def __init__(self):
        self.llm = LLMClient()

    async def extract(self, intent: str, params: dict, message: str):
        """
        Use LLM to extract missing parameters or confirm
        """
        missing = []

        empty_values = (None, "", "null")

        for key, value in params.items():
            
            if value in empty_values:
                        missing.append(key)
             

        prompt = [
            {"role": "system", "content": f"""
            Extract the following missing fields for intent: {intent}
            Required: {missing}
            Return JSON only, example:
            {{ "param": "value", ... }}
            """},
            {"role": "user", "content": message}
        ]

        result = await self.llm.generate(prompt)

        try:
            extracted = json.loads(result)
            for k, v in extracted.items():
                params[k] = v
        except json.JSONDecodeError:
            pass

        still_missing = [k for k, v in params.items() if not v]
        return params, still_missing
