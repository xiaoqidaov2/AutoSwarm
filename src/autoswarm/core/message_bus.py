from typing import List, Optional, Dict
import logging
from .models import Message


logger = logging.getLogger(__name__)


class MessageBus:
    def __init__(self):
        self.current_step: int = 0
        self.messages_by_step: Dict[int, List[Message]] = {}

    def set_current_step(self, step: int) -> None:
        self.current_step = step

    def send(self, sender_id: str, receiver_id: Optional[str], content: str, broadcast: bool = False) -> str:
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            step=self.current_step,
            broadcast=broadcast
        )
        if self.current_step not in self.messages_by_step:
            self.messages_by_step[self.current_step] = []
        self.messages_by_step[self.current_step].append(message)
        logger.debug(f"Message sent: {sender_id} -> {receiver_id or 'broadcast'}")
        return message.message_id

    def receive(self, agent_id: str, step: int) -> List[Message]:
        if step not in self.messages_by_step:
            return []
        messages = []
        for msg in self.messages_by_step[step]:
            if msg.broadcast or msg.receiver_id == agent_id:
                messages.append(msg)
        logger.debug(f"Agent {agent_id} received {len(messages)} messages at step {step}")
        return messages

    def clear_step(self, step: int) -> None:
        if step in self.messages_by_step:
            del self.messages_by_step[step]
            logger.debug(f"Cleared messages for step {step}")

    def clear_all(self) -> None:
        self.messages_by_step.clear()
        self.current_step = 0
        logger.info("Message bus cleared")
