"""Manages the state and message history of conversations using Redis."""
import json
from typing import Optional
from redis import Redis
from app.core.config import get_settings

settings = get_settings()


# Add connection pooling for better performance
class StateManager:
    def __init__(self, host: str, port: int, db: int):
        self.redis = Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
            max_connections=10  
        )
        self.ttl = 3600
        self.max_history = 20


    def health_check(self) -> bool:
        """Check if Redis is accessible"""
        try:
            return self.redis.ping()
        except Exception:
            return False

    def _key(self, conversation_id: str, suffix: str) -> str:
        return f"chat:{conversation_id}:{suffix}"

    
    def add_message(self, conversation_id: str, role: str, content: str):
        """Add a message to the conversation history."""
        key = self._key(conversation_id, "messages")
        entry = json.dumps({"role": role, "content": content})

        self.redis.rpush(key, entry)

        # Limit to last 20 messages
        self.redis.ltrim(key, -self.max_history, -1)

        # Reset TTL
        self.redis.expire(key, self.ttl)

    def get_messages(self, conversation_id: str):
        """Retrieve the conversation history."""
        key = self._key(conversation_id, "messages")
        raw = self.redis.lrange(key, 0, -1)
        return [json.loads(m) for m in raw]

    
    def set_state(self, conversation_id: str, state_data: dict):
        """Set the conversation state."""
        key = self._key(conversation_id, "state")
        self.redis.set(key, json.dumps(state_data))
        self.redis.expire(key, self.ttl)

    def get_state(self, conversation_id: str) -> Optional[dict]:
        """Retrieve the conversation state."""
        key = self._key(conversation_id, "state")
        raw = self.redis.get(key)
        if not raw:
            return None
        return json.loads(raw)

    def clear(self, conversation_id: str):
        """Clear the conversation state and message history."""
        self.redis.delete(self._key(conversation_id, "messages"))
        self.redis.delete(self._key(conversation_id, "state"))
