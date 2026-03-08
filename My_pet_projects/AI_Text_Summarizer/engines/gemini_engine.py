import google.generativeai as genai
import os

class GeminiEngine:

    def __init__(self, model):
        genai.configure(
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.model = genai.GenerativeModel(model)


    def stream(self, prompt):
        for chunk in self.model.generate_content(
            prompt,
            stream=True
        ):
            if chunk.text:
                yield chunk.text