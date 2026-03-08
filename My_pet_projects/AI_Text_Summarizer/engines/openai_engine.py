from openai import OpenAI
import os

class OpenAIEngine:

    def __init__(self, model):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = model

    def stream(self, prompt):
        with self.client.responses.stream(
            model=self.model,
            input=prompt
        ) as stream:
            for event in stream:
                if event.type == "response.output_text.delta":
                    yield event.delta