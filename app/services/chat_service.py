from typing import Dict, Any

from fastapi.params import Depends
from app.services.state_manager import StateManager
from app.services.intents.intent_classifier import IntentClassifier
from app.services.intents.param_extractor import ParamExtractor
from app.services.irctc_client import IRCTCClient, IRCTCClientError


class ChatService:
    """Service to handle chat interactions with users."""
    HISTORY_LIMIT = 15  # cap message history

    def __init__(self,state = Depends (StateManager), intent_classifier: IntentClassifier = Depends(IntentClassifier), param_extractor: ParamExtractor = Depends(ParamExtractor), irctc_client: IRCTCClient = Depends(IRCTCClient)):
        self.state = state
        self.intent_classifier = intent_classifier
        self.param_extractor = param_extractor
        self.irctc = irctc_client

    async def handle_user_message(self, conversation_id: str, message: str) -> Dict[str, Any]:
        """Main method to handle user messages."""
        self._store_message(conversation_id, "user", message)

        conv_state = self.state.get_state(conversation_id)

        
        if not conv_state:
            intent = self.intent_classifier.classify(message)
            params = self.param_extractor.extract(intent, message)

            missing = self._find_missing(intent, params)
            stage = "awaiting_params" if missing else "ready"

            conv_state = {"intent": intent, "params": params, "stage": stage}
            self.state.set_state(conversation_id, conv_state)

            if missing:
                return {"reply": self._ask_for_missing_params(missing)}

        
        if conv_state["stage"] == "awaiting_params":
            new_params = self.param_extractor.extract(conv_state["intent"], message)
            conv_state["params"].update({k: v for k, v in new_params.items() if v})

            missing = self._find_missing(conv_state["intent"], conv_state["params"])

            if missing:
                self.state.set_state(conversation_id, conv_state)
                return {"reply": self._ask_for_missing_params(missing)}

            conv_state["stage"] = "ready"
            self.state.set_state(conversation_id, conv_state)

       
        response_text = await self._dispatch(conv_state["intent"], conv_state["params"])

        self._store_message(conversation_id, "assistant", response_text)
        self.state.clear(conversation_id)

        return {"reply": response_text}

   
    def _store_message(self, conversation_id: str, role: str, content: str):
        self.state.add_message(conversation_id, role, content)
        messages = self.state.get_messages(conversation_id)

        if len(messages) > self.HISTORY_LIMIT:
            trimmed = messages[-self.HISTORY_LIMIT:]
            self.state.redis.delete(self.state._key(conversation_id, "messages"))
            for m in trimmed:
                self.state.add_message(conversation_id, m["role"], m["content"])

   
    async def _dispatch(self, intent: str, params: Dict[str, Any]) -> str:
        try:
            if intent == "live_status":
                return await self.irctc.get_train_live_status(params["train_no"], params["date"])

            if intent == "between_stations":
                return await self.irctc.trains_between_stations_v3(
                    params["source"], params["destination"], params["date"]
                )

            if intent == "pnr_status":
                return await self.irctc.get_pnr_status_v3(params["pnr"])

            if intent == "seat_availability":
                return await self.irctc.check_seat_availability(
                    params["train_no"],
                    params["source"],
                    params["destination"],
                    params["date"],
                    params.get("class", "SL")
                )

            if intent == "train_schedule":
                return await self.irctc.get_train_schedule(params["train_no"])

            if intent == "live_station":
                return await self.irctc.get_live_station(params["hours"])

            if intent == "search_train":
                return await self.irctc.search_train(params["query"])

            if intent == "search_station":
                return await self.irctc.search_station(params["query"])

            return "❌ Unknown intent."

        except IRCTCClientError as e:
            return f"⚠️ IRCTC API Error: {e}"

        except Exception as e:
            return f"⚠️ Error: {e}"

    
    def _find_missing(self, intent: str, params: Dict[str, Any]):
        required = {
            "between_stations": ["source", "destination", "date"],
            "pnr_status": ["pnr"],
            "live_status": ["train_no", "date"],
            "train_schedule": ["train_no"],
            "seat_availability": ["train_no", "source", "destination", "date"],
            "live_station": ["hours"],
            "search_train": ["query"],
            "search_station": ["query"]
        }
        fields = required.get(intent, [])
        return [f for f in fields if f not in params]

    def _ask_for_missing_params(self, missing):
        return f"❓ I need the following information: {', '.join(missing)}."
