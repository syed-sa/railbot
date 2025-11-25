from app.services.state_manager import StateManager
from app.llm.llm_client import LLMClient

class ChatService:
    def __init__(self):
        self.state_manager = StateManager()
        self.llm = LLMClient()

    def build_prompt(self, history):
        """Convert Redis messages to OpenAI/HF format"""
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]

    async def process_user_message(self, conversation_id: str, user_text: str):
        """
        Process user message asynchronously.
        This should be called from FastAPI endpoints directly.
        """
        # Get previous messages
        history = self.state_manager.get_messages(conversation_id) or []

        # Add user message to state
        self.state_manager.add_message(conversation_id, "user", user_text)

        # Build prompt with history + new message
        prompt = self.build_prompt(history + [{"role": "user", "content": user_text}])

        # Call LLM
        reply = await self.llm.generate(prompt)

        # Save bot reply
        self.state_manager.add_message(conversation_id, "assistant", reply)

        return reply
    
    def clear_conversation(self, conversation_id: str):
        """Clear all messages and state for a conversation"""
        self.state_manager.clear(conversation_id)
    
    def get_conversation_history(self, conversation_id: str):
        """Get full conversation history"""
        return self.state_manager.get_messages(conversation_id) or []