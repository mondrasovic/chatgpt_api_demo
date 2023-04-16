from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from app.model import Message, SenderRole

if TYPE_CHECKING:
    from app.model import Model
    from app.view import View


class Controller(abc.ABC):
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.view.set_controller(self)

    @abc.abstractmethod
    def handle_prompt_message(self, role: str, content: str) -> None:
        pass

    @abc.abstractmethod
    def clear_history(self) -> None:
        pass


class ChatBotController(Controller):
    def handle_prompt_message(self, role: str, content: str) -> None:
        sender_role = SenderRole.from_str(role)
        message = Message(sender_role, content)
        if message.sender_role == SenderRole.ASSISTANT:
            raise ValueError(f"prompt message cannot have the assistant as the sender")

        self.model.handle_prompt(
            message,
            self.view.temperature,
            self.view.top_probability,
            self.view.presence_penalty,
            self.view.frequency_penalty,
        )
        self.update_history()

        if message.sender_role == SenderRole.SYSTEM:
            pass

    def update_history(self) -> None:
        self.view.clear_history()
        for message in self.model.history:
            self.view.add_message(role=message.sender_role.value, content=message.content)

    def clear_history(self) -> None:
        self.model.clear_history()
        self.view.clear_history()
