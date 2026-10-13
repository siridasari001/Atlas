from openai import OpenAI

from app.core.config import settings


class LLMClient:
    """
    Client for interacting with the configured language model.
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model="gpt-5-mini",
            input=prompt,
        )

        return response.output_text