import logging
from abc import abstractmethod
from openai import OpenAI


logger = logging.getLogger(__name__)


class BaseResource:
    def __init__(self, openai: OpenAI) -> None:
        self.openai = openai

    @property
    @abstractmethod
    def resource(self) -> str:
        raise NotImplementedError("Resource not implemented.")
