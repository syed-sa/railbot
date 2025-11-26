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
            - search_trains (source, destination, date)
            - live_status (train_number)
            - train_schedule (train_number)
            - seat_availability (train_number, source, destination, date, class)
            - pnr_status (pnr)
            - live_station (station_code, hours)
            - station_search (station_name)
            - train_search (train_name_or_number)
            - unknown

            IMPORTANT RULES:
            - Return ONLY valid intents.
            - Always return JSON only. NO explanations.
            - JSON must be EXACT format:

            {
            "intent": "...",
            "params": {},
            "missing": []
            }
            """
            },
            {"role": "user", "content": message}
        ]

        response = await self.llm.generate(prompt)

        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            return IntentResult(
                intent=Intent.UNKNOWN,
                params={},
                missing=["unable_to_parse"]
            )

        return IntentResult(
            intent=Intent(data.get("intent", "unknown")),
            params=data.get("params", {}),
            missing=data.get("missing", [])
        )
