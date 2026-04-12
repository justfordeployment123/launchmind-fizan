"""Message bus for agent-to-agent communication using shared dictionary."""
import json
from datetime import datetime
from uuid import uuid4
from typing import Dict, List, Any, Optional

class Message:
    """Structured message with required schema fields."""

    def __init__(self, from_agent: str, to_agent: str, message_type: str,
                 payload: Dict[str, Any], parent_message_id: Optional[str] = None):
        self.message_id = str(uuid4())
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type  # 'task', 'result', 'revision_request', 'confirmation'
        self.payload = payload
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.parent_message_id = parent_message_id

    def to_dict(self) -> Dict:
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "parent_message_id": self.parent_message_id
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class MessageBus:
    """Shared message bus for all agents."""

    def __init__(self):
        self.messages: Dict[str, List[Message]] = {}
        self.all_messages: List[Message] = []  # Full history

    def send_message(self, message: Message) -> None:
        """Send a message to an agent."""
        agent = message.to_agent
        if agent not in self.messages:
            self.messages[agent] = []

        self.messages[agent].append(message)
        self.all_messages.append(message)

        # Print to console for visibility
        print(f"\n📤 [{message.from_agent.upper()}] → [{message.to_agent.upper()}]")
        print(f"   Type: {message.message_type}")
        print(f"   ID: {message.message_id}")
        print(f"   Payload keys: {list(message.payload.keys())}")

    def get_messages(self, agent: str) -> List[Message]:
        """Get all messages for an agent."""
        return self.messages.get(agent, [])

    def get_new_messages(self, agent: str, last_message_id: Optional[str] = None) -> List[Message]:
        """Get messages for an agent since last_message_id."""
        messages = self.get_messages(agent)
        if last_message_id is None:
            return messages

        found_index = -1
        for i, msg in enumerate(messages):
            if msg.message_id == last_message_id:
                found_index = i
                break

        return messages[found_index + 1:] if found_index >= 0 else messages

    def get_message_history(self) -> List[Dict]:
        """Get complete message history."""
        return [msg.to_dict() for msg in self.all_messages]

    def print_history(self) -> None:
        """Pretty print message history."""
        print("\n" + "="*80)
        print("MESSAGE HISTORY")
        print("="*80)
        for msg in self.all_messages:
            print(f"\n{msg.from_agent} → {msg.to_agent}")
            print(f"  Type: {msg.message_type}")
            print(f"  ID: {msg.message_id}")
            print(f"  Time: {msg.timestamp}")
            print(f"  Payload: {json.dumps(msg.payload, indent=4)}")
        print("\n" + "="*80)


# Global message bus instance
message_bus = MessageBus()
