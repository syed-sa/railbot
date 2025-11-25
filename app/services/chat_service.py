from app.services.state_manager import StateManager
from app.llm.llm_client import LLMClient
import asyncio

class ChatService:
    def __init__(self):
        self.state_manager = StateManager()
        self.llm = LLMClient()

    def build_prompt(self, history):
        # Convert Redis messages → OpenAI/HF format
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]

    async def process_user_message_async(self, conversation_id: str, user_text: str):
        # Get previous messages
        history = self.state_manager.get_messages(conversation_id) or []

        # Add user message
        self.state_manager.add_message(conversation_id, "user", user_text)

        # Build prompt
        prompt = self.build_prompt(history + [{"role": "user", "content": user_text}])

        # Call LLM
        reply = await self.llm.generate(prompt)

        # Save bot reply
        self.state_manager.add_message(conversation_id, "assistant", reply)

        return reply

    # Sync wrapper for FastAPI
    def process_user_message(self, conversation_id: str, user_text: str):
        return asyncio.run(
            self.process_user_message_async(conversation_id, user_text)
        )
