import os
from .resources import CompletionsResource
import openai

class _ChatGPTClient:
    # NOTE: this is a singleton class, hence the prefix
    def __init__(self) -> None:
        self.openai = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.completions_resource = CompletionsResource(
            openai=self.openai
        )

    @property
    def completions(self) -> CompletionsResource:
        return self.completions_resource



chatgpt_client = _ChatGPTClient()