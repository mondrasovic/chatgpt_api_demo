from __future__ import annotations

import abc
import dataclasses
import enum
import json
import os
from typing import TYPE_CHECKING

import openai
import requests

if TYPE_CHECKING:
    from numbers import Number
    from typing import Iterable, Iterator, Sequence


class SenderRole(enum.Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"

    @classmethod
    def from_str(cls, role_string: str) -> SenderRole:
        for member in cls:
            if member.value == role_string:
                return member
        raise ValueError(f"unrecognized role {role_string}")


@dataclasses.dataclass(frozen=True)
class Message:
    sender_role: SenderRole
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.sender_role.value, "content": self.content}


class ChatGPTAccessor:
    OPENAI_URL = "https://api.openai.com/v1/chat/completions"

    def __init__(self, environ_var_name: str = "OPENAI_API_KEY") -> None:
        openai.api_key = os.getenv(environ_var_name)

    def query(
        self,
        messages: Iterable[Message],
        temperature: float = 1.0,
        top_probability: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        n_choices: int = 1,
    ) -> Sequence[Message]:
        self._check_in_range(temperature, 0.0, 2.0, "temperature")
        self._check_in_range(top_probability, 0.0, 1.0, "top probability")
        self._check_in_range(presence_penalty, -2.0, 2.0, "presence penalty")
        self._check_in_range(frequency_penalty, -2.0, 2.0, "frequency penalty")
        self._check_in_range(n_choices, 0, 1024, "no. of choices")

        input_messages = [message.to_dict() for message in messages]
        if not input_messages:
            raise ValueError("no message provided for the query")

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": input_messages,
            "temperature": temperature,
            "top_p": top_probability,
            "n": n_choices,
            "stream": False,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
        }

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {openai.api_key}"}

        response = requests.post(self.OPENAI_URL, headers=headers, json=payload, stream=False)
        output_messages = list(self._json_to_messages(response.content))

        return output_messages

    @staticmethod
    def _check_in_range(value: Number, min_val: Number, max_val: Number, description: str) -> None:
        if not (min_val <= value <= max_val):
            raise ValueError(
                f"{description} not in range, expected <{min_val}, {max_val}>, got {value}"
            )

    @staticmethod
    def _json_to_messages(response_content: bytes) -> Iterator[Message]:
        dict_content = json.loads(response_content)
        for choice in dict_content["choices"]:
            message = choice["message"]
            yield Message(SenderRole.from_str(message["role"]), message["content"])


class Model(abc.ABC):
    def __init__(self) -> None:
        self._history = []

    @property
    def history(self) -> Iterable[Message]:
        return self._history

    @abc.abstractmethod
    def handle_prompt(
        self,
        message: Message,
        temperature: float = 1.0,
        top_probability: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
    ) -> None:
        pass

    def clear_history(self) -> None:
        self._history.clear()

    def _add_message(self, message: Message) -> None:
        self._history.append(message)


class ChatBotModel(Model):
    def __init__(self) -> None:
        super().__init__()

        self.gpt_accessor = ChatGPTAccessor()

    def handle_prompt(
        self,
        message: Message,
        temperature: float = 1.0,
        top_probability: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
    ) -> None:
        self._add_message(message)
        response_messages = self.gpt_accessor.query(
            self.history, temperature, top_probability, presence_penalty, frequency_penalty
        )
        response_message = response_messages[0]
        self._add_message(response_message)
