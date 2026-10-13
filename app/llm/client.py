from openai import OpenAI

from app.core.config import settings


class LLMClient:
    """
    Client for interacting with the configured language model.
    """

    def __init__(self):
        """
        Initialize the OpenAI client.
        """

        self.client = OpenAI()

    def generate(self, prompt: str) -> str:
        """
        Generate a response from the language model.

        Args:
            prompt: Prompt containing the context and user request.

        Returns:
            The generated response as text.
        """

        response = self.client.responses.create(
            model="gpt-5-mini",
            input=prompt,
        )

        return response.output_text