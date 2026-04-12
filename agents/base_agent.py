"""Base agent class with LLM integration."""
import os
from abc import ABC, abstractmethod
from anthropic import Anthropic
from message_bus import Message, message_bus

class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, name: str):
        self.name = name
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-haiku-4-5-20251001"
        self.last_processed_message_id = None

    def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call Claude API."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"❌ LLM Error in {self.name}: {str(e)}")
            raise

    def send_message(self, to_agent: str, message_type: str, payload: dict, parent_id=None) -> Message:
        """Send a structured message to another agent."""
        msg = Message(
            from_agent=self.name,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            parent_message_id=parent_id
        )
        message_bus.send_message(msg)
        return msg

    def get_messages(self) -> list:
        """Get all messages for this agent."""
        return message_bus.get_messages(self.name)

    def get_new_messages(self) -> list:
        """Get new messages since last check."""
        new_msgs = message_bus.get_new_messages(self.name, self.last_processed_message_id)
        if new_msgs:
            self.last_processed_message_id = new_msgs[-1].message_id
        return new_msgs

    @abstractmethod
    def run(self):
        """Run the agent's main logic. Must be implemented by subclasses."""
        pass
