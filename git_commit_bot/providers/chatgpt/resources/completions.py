from typing import Iterable
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from .base import BaseResource

class CompletionsResource(BaseResource):
    def __init__(self, openai: OpenAI) -> None:
        super().__init__(openai)
        
    @property
    def resource(self) -> str:
        return "completions"

    def create(
        self,
        model: str,
        messages: Iterable[ChatCompletionMessageParam],
        max_tokens: int,
        temperature: float
    ) -> ChatCompletion:
        return self.openai.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
