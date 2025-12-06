# app/intents/classifier.py
from typing import Dict, Any
import json
from app.services.llm.llm_client import LLMClient

class LLMService:
    def __init__(self):
        self.llm = LLMClient()

    async def classify_intent(self, message: str) -> dict:
        """
        Returns:
        {
            "category": "domain" | "small_talk" | "out_of_scope",
            "intent": "pnr_status" | "greeting" | null
        }
        """
        prompt = [
            {
                "role": "system",
                "content": """
            You are an intent classifier for an IRCTC chatbot.

            Return a JSON with:
            {
            "category": "domain" | "small_talk" | "out_of_scope",
            "intent": "<intent_name or null>"
            }

            ====================
            SMALL TALK INTENTS:
            - greeting (hi, hello, good morning, hey)
            - farewell (bye, good night)
            - thanks (thanks, thank you)
            - how_are_you (how are you?)

            ====================
            DOMAIN INTENTS:
            - train_between_stations
            - live_status
            - train_schedule
            - seat_availability
            - pnr_status
            - live_station
            - search_train
            - search_station

            ====================
            OUT OF SCOPE:
            Anything unrelated to trains or IRCTC.

            STRICT RULES:
            - Return ONLY JSON.
            - No markdown. No explanation.
            """
            },
            {"role": "user", "content": message}
        ]

        response = await self.llm.generate(prompt)

        cleaned = response.strip()
        try:
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            cleaned = cleaned.strip()

            return json.loads(cleaned)
        except Exception:
            return {"category": "out_of_scope", "intent": None}


    async def extract_params(self, intent: str, message: str) -> Dict[str, Any]:
        """
        Extract parameters from a single user message for the given intent.
        Returns a dict with extracted params (may be incomplete).
        """
        # Define what params we're looking for based on intent
        param_schema = self._get_param_schema(intent)

        if not param_schema:
            return {}

        # Build LLM prompt to extract params
        prompt = [
            {
                "role": "system",
                "content": f"""
        You are a parameter extraction assistant for an Indian Railways chatbot.

        Intent: {intent}
        Required parameters: {list(param_schema.keys())}

        Extract these parameters from the user's message:
        {json.dumps(param_schema, indent=2)}

        Return ONLY a valid JSON object. Use null for parameters not found in the message.
        Example: {{"train_no": "12345", "date": "2024-01-15", "source": null}}
        Important:
        - Station names should be   station codes (e.g., "NDLS" for New Delhi")
        - Dates may appear in formats such as:
        * DD/MM/YYYY
        * YYYY-MM-DD
        * DD/MM/YY
        * YY-MM-DD
        - Always convert extracted dates to YYYY-MM-DD format.
        - If year is 2 digits (e.g., 25), interpret it as 20YY → 2025.
        - Train numbers without spaces
        - PNR as a 10-digit string

        """,
            },
            {"role": "user", "content": message},
        ]

        result = await self.llm.generate(prompt)

        # Parse LLM response
        try:
            # Clean up markdown code blocks if LLM wrapped response
            cleaned = result.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            cleaned = cleaned.strip()

            extracted = json.loads(cleaned)

            # Filter out null/empty values
            return {k: v for k, v in extracted.items() if v and v != "null"}

        except (json.JSONDecodeError, IndexError) as e:
            print(f"Failed to parse LLM response: {e}")
            return {}

    def _get_param_schema(self, intent: str) -> Dict[str, str]:
        """Return parameter schema (name -> description) for each intent."""
        schemas = {
                "train_between_stations": {
                    "source": "Source station code",
                    "destination": "Destination station code",
                    "date": "Journey date (YYYY-MM-DD)",
                },
                "pnr_status": {"pnr": "10-digit PNR number"},
                "live_status": {
                    "train_no": "Train number",
                    "date": "Date to check (YYYY-MM-DD)",
                },
                "train_schedule": {"train_no": "Train number"},
                "seat_availability": {
                "train_no": "Train number (e.g., 19038)",
                "source": "Source station code (e.g., ST)",
                "destination": "Destination station code (e.g., BVI)",
                "date": "Journey date (YYYY-MM-DD)",
                "class_type": "Class code (e.g., 2A, SL, 3A)",
                "quota": "Booking quota (e.g., GN)"
                },
                "live_station": {"hours": "Number of hours to look ahead"},
                "search_train": {"query": "Train name or number to search"},
                "search_station": {"query": "Station name to search"},
        }
        return schemas.get(intent, {})


    async def to_natural_language(self, intent, api_response):
        """Convert API JSON response to a natural language answer."""
        prompt = [
            {
                "role": "system",
                "content": """
    You are a strict response formatter for an IRCTC train assistant.
    Use ONLY the data present in the JSON.
    Do NOT hallucinate.
    Produce a short, clear answer.
    """
            },
            {
                "role": "user",
                "content": f"""
    question intent:
    {intent}

    API JSON:
    {api_response}
    """
            }
        ]
        llm_response = await self.llm.generate(prompt)
        text = llm_response
        return text
