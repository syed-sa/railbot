import json
from typing import Dict, Any
from app.services.llm.llm_client import LLMClient


class ParamExtractor:
    """Extracts parameters for intents using LLM."""

    def __init__(self):
        self.llm = LLMClient()

    async def extract(self, intent: str, message: str) -> Dict[str, Any]:
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
        * DD-MM-YYYY
        * DD/MM/YY
        * DD-MM-YY
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
                    "train_no": "Train number",
                    "source": "Source station code",
                    "destination": "Destination station code",
                    "date": "Journey date (YYYY-MM-DD)",
                    "class": "Class code (optional, default: SL)",
                },
                "live_station": {"hours": "Number of hours to look ahead"},
                "search_train": {"query": "Train name or number to search"},
                "search_station": {"query": "Station name to search"},
        }
        return schemas.get(intent, {})
