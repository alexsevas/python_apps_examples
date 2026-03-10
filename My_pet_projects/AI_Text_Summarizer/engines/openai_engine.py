from openai import OpenAI
import os

class OpenAIEngine:

    def __init__(self, model):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def stream(self, prompt):
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"OpenAI error: {str(e)}")