import asyncio
from typing import Dict, Any, List
from fastapi.params import Depends
from app.services.llm.llm_service import LLMService
from app.services.redis.state_manager import StateManager
from app.services.irctc.irctc_client import IRCTCClient, IRCTCClientError


class ChatService:
    HISTORY_LIMIT = 15

    def __init__(
        self,
        state=Depends(StateManager),
        irctc_client: IRCTCClient = Depends(IRCTCClient),
        llm_service=Depends(LLMService),
    ):
        self.state = state
        self.irctc = irctc_client
        self.llm_service = llm_service

    async def handle_user_message(self, conversation_id: str, message: str) -> Dict[str, Any]:
        self._store_message(conversation_id, "user", message)

        conv_state = self.state.get_state(conversation_id)

        # =========================
        # STEP 1 → Detect category
        # =========================
        classification = await self.llm_service.classify_intent(message)
        category = classification["category"]
        intent = classification["intent"]

        # =========================
        # CATEGORY: SMALL TALK
        # =========================
        if category == "small_talk":
            reply = self._handle_small_talk(intent)
            self._store_message(conversation_id, "assistant", reply)
            return {"reply": reply}

        # =========================
        # CATEGORY: OUT OF SCOPE
        # =========================
        if category == "out_of_scope":
            reply = " I can help you with IRCTC train services. Please ask me if you have any questions related to trains, bookings, or PNR status."
            self._store_message(conversation_id, "assistant", reply)
            return {"reply": reply}

        # =========================
        # CATEGORY: DOMAIN (IRCTC)
        # =========================

        # Fresh conversation
        if not conv_state:
            params = await self.llm_service.extract_params(intent, message)
            missing = self._find_missing_params(intent, params)

            conv_state = {
                "intent": intent,
                "params": params,
                "stage": "awaiting_params" if missing else "ready"
            }
            self.state.set_state(conversation_id, conv_state)

            if missing:
                reply = self._ask_for_missing_params(missing)
                self._store_message(conversation_id, "assistant", reply)
                return {"reply": reply}

        # Continue collecting parameters
        elif conv_state["stage"] == "awaiting_params":
            new_params = await self.llm_service.extract_params(conv_state["intent"], message)
            conv_state["params"].update(new_params)

            missing = self._find_missing_params(conv_state["intent"], conv_state["params"])
            if missing:
                self.state.set_state(conversation_id, conv_state)
                reply = self._ask_for_missing_params(missing)
                self._store_message(conversation_id, "assistant", reply)
                return {"reply": reply}

            conv_state["stage"] = "ready"
            self.state.set_state(conversation_id, conv_state)

        # Execute IRCTC API
        response_text = (await self._dispatch(conv_state["intent"], conv_state["params"]))
        response_text = await self.llm_service.to_natural_language(conv_state["intent"], response_text)

        self._store_message(conversation_id, "assistant", response_text)

        self.state.clear(conversation_id)
        return response_text


    # ============================================================
    # SMALL TALK HANDLER
    # ============================================================
    def _handle_small_talk(self, intent: str) -> str:
        responses = {
            "greeting": "👋 Hello! How can I assist you with IRCTC today?",
            "farewell": "👋 Goodbye! Have a safe journey!",
            "thanks": "😊 You're welcome!",
            "how_are_you": "I'm doing great! How can I help you with IRCTC services?"
        }
        return responses.get(intent)

    # ============================================================
    # UTILS (unchanged)
    # ============================================================
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
            if intent == "train_between_stations":
                return await self.irctc.trains_between_stations_v3(params["source"], params["destination"], params["date"])
            if intent == "pnr_status":
                return await self.irctc.get_pnr_status_v3(params["pnr"])
            if intent == "seat_availability":
                return await self.irctc.check_seat_availability(
                    params["train_no"], params["source"], params["destination"], params["date"], params.get("class", "SL")
                )
            if intent == "train_schedule":
                return await self.irctc.get_train_schedule(params["train_no"])
            if intent == "live_station":
                return await self.irctc.get_live_station(params["hours"])
            if intent == "search_train":
                return await self.irctc.search_train(params["query"])
            if intent == "search_station":
                return await self.irctc.search_station(params["query"])

            return "Unknown intent. Please rephrase."
        except IRCTCClientError as e:
            return f"IRCTC API Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    def _find_missing_params(self, intent: str, params: Dict[str, Any]) -> List[str]:
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
        missing = []
        for f in required.get(intent, []):
            v = params.get(f)
            if not v or v in ("", None, "null"):
                missing.append(f)
        return missing

    def _ask_for_missing_params(self, missing: List[str]) -> str:
        names = {
            "source": "source station",
            "destination": "destination station",
            "date": "journey date",
            "train_no": "train number",
            "pnr": "PNR number",
            "hours": "number of hours",
            "query": "search keyword",
            "class": "class type"
        }
        readable = [names.get(f, f) for f in missing]
        if len(readable) == 1:
            return f"Please provide the {readable[0]}."
        if len(readable) == 2:
            return f"Please provide the {readable[0]} and {readable[1]}."
        return f"I need: {', '.join(readable[:-1])}, and {readable[-1]}."
