import asyncio
from typing import Dict, Any, List
from fastapi.params import Depends
from app.services.state_manager import StateManager
from app.services.intents.intent_classifier import IntentClassifier
from app.services.intents.param_extractor import ParamExtractor
from app.services.irctc_client import IRCTCClient, IRCTCClientError


class ChatService:
    """Service to handle chat interactions with users."""
    HISTORY_LIMIT = 15

    def __init__(
        self,
        state=Depends(StateManager),
        intent_classifier: IntentClassifier = Depends(IntentClassifier),
        param_extractor: ParamExtractor = Depends(ParamExtractor),
        irctc_client: IRCTCClient = Depends(IRCTCClient)
    ):
        self.state = state
        self.intent_classifier = intent_classifier
        self.param_extractor = param_extractor
        self.irctc = irctc_client

    async def handle_user_message(self, conversation_id: str, message: str) -> Dict[str, Any]:
        """Process a user message and return the assistant's reply."""
        self._store_message(conversation_id, "user", message)

        conv_state = self.state.get_state(conversation_id)

        # === STEP 1: New conversation - classify intent ===
        if not conv_state:
            intent= (await self.intent_classifier.classify(message))
 
            # Extract params from initial message
            params = await self.param_extractor.extract(intent, message)
            
            # Check what's still missing
            missing = self._find_missing_params(intent, params)
            # Save state
            conv_state = {
                "intent": intent,
                "params": params,
                "stage": "awaiting_params" if missing else "ready"
            }
            self.state.set_state(conversation_id, conv_state)
            
            # If params missing, ask user
            if missing:
                reply = self._ask_for_missing_params(missing)
                self._store_message(conversation_id, "assistant", reply)
                return {"reply": reply}

        # === STEP 2: Continuing conversation - gather more params ===
        elif conv_state["stage"] == "awaiting_params":
            # Extract params from current message
            new_params = await self.param_extractor.extract(conv_state["intent"], message)
            
            # Merge with existing params (new values override)
            conv_state["params"].update(new_params)
            
            # Check what's still missing
            missing = self._find_missing_params(conv_state["intent"], conv_state["params"])
            
            # If still missing params, ask again
            if missing:
                self.state.set_state(conversation_id, conv_state)
                reply = self._ask_for_missing_params(missing)
                self._store_message(conversation_id, "assistant", reply)
                return {"reply": reply}
            
            # All params collected!
            conv_state["stage"] = "ready"
            self.state.set_state(conversation_id, conv_state)

        # === STEP 3: Execute API call ===
        response_text = await self._dispatch(conv_state["intent"], conv_state["params"])
        
        self._store_message(conversation_id, "assistant", response_text)
        
        self.state.clear(conversation_id)
        
        return {"reply": response_text}



    def _store_message(self, conversation_id: str, role: str, content: str):
        """Store message and maintain history limit."""
        self.state.add_message(conversation_id, role, content)
        messages = self.state.get_messages(conversation_id)

        if len(messages) > self.HISTORY_LIMIT:
            trimmed = messages[-self.HISTORY_LIMIT:]
            self.state.redis.delete(self.state._key(conversation_id, "messages"))
            for m in trimmed:
                self.state.add_message(conversation_id, m["role"], m["content"])




    async def _dispatch(self, intent: str, params: Dict[str, Any]) -> str:
        """Route to appropriate API based on intent."""
        try:
            if intent == "live_status":
                return await self.irctc.get_train_live_status(
                    params["train_no"], 
                    params["date"]
                )

            if intent == "train_between_stations":
                return await self.irctc.trains_between_stations_v3(
                    params["source"], 
                    params["destination"], 
                    params["date"]
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

            return " Unknown intent. Please rephrase your query."
        except IRCTCClientError as e:
            return f" IRCTC API Error: {e}"
        except KeyError as e:
            return f" Missing required parameter: {e}"
        except (TypeError, ValueError, RuntimeError, asyncio.TimeoutError) as e:
            return f" Unexpected error: {e}"




    def  _find_missing_params(self, intent: str, params: Dict[str, Any]) -> List[str]:
        """Check which required params are still missing."""
        required = {
            "train_between_stations": ["source", "destination", "date"],
            "pnr_status": ["pnr"],
            "live_status": ["train_no", "date"],
            "train_schedule": ["train_no"],
            "seat_availability": ["train_no", "source", "destination", "date"],
            "live_station": ["hours"],
            "search_train": ["query"],
            "search_station": ["query"]
        }
        
        required_fields = required.get(intent, [])
        
        # Check which required fields are missing or empty
        missing = []
        for field in required_fields:
            value = params.get(field)
            if not value or value in ("", "null", None):
                missing.append(field)
        
        return missing




    def _ask_for_missing_params(self, missing: List[str]) -> str:
        """Generate a natural question to ask for missing parameters."""
        # Make it more conversational
        field_names = {
            "source": "source station",
            "destination": "destination station",
            "date": "journey date",
            "train_no": "train number",
            "pnr": "PNR number",
            "hours": "number of hours",
            "query": "search query",
            "class": "class type"
        }
        
        readable = [field_names.get(f, f) for f in missing]
        
        if len(readable) == 1:
            return f" Please provide the {readable[0]}."
        elif len(readable) == 2:
            return f" Please provide the {readable[0]} and {readable[1]}."
        else:
            return f" I need the following information: {', '.join(readable[:-1])}, and {readable[-1]}."