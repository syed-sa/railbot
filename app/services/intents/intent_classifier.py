# app/intents/classifier.py
import json
from app.models.Intent import Intent, IntentResult
from app.services.llm.llm_client import LLMClient


class IntentClassifier:
    def __init__(self):
        self.llm = LLMClient()

    async def classify(self, message: str) -> IntentResult:
        prompt = [
            {
                "role": "system",
                "content": """
            You are an intent classifier for an IRCTC train assistant.

            VALID INTENTS:
            - train_between_stations (source, destination, date)
            - live_status (train_number)
            - train_schedule (train_number)
            - seat_availability (train_number, source, destination, date, class)
            - pnr_status (pnr)
            - live_station (station_code, hours)
            - station_search (station_name)
            - unknown

            IMPORTANT RULES:
            - Return ONLY valid JSON
            - NO explanations or extra text
            - Exact format: {"intent": "train_between_stations"}
            """
            },
            {"role": "user", "content": message}
        ]
        response = await self.llm.generate(prompt)

        try:
            # Clean response (remove markdown if present)
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            cleaned = cleaned.strip()
            
            data = json.loads(cleaned)
            intent_str = data.get("intent", "unknown")
            
            # Validate against enum
            try:
                Intent(intent_str)  # This validates it's a valid intent
                return intent_str
            except ValueError:
                # Invalid intent string
                return Intent.UNKNOWN.value
                
        except (json.JSONDecodeError, KeyError) as e:
                print(f"Failed to parse intent: {e}")
                return Intent.UNKNOWN.value
        
