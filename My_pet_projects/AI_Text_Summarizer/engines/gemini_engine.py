import google.generativeai as genai
import os

class GeminiEngine:

    def __init__(self, model):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise Exception("GOOGLE_API_KEY not found in environment")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def stream(self, prompt):
        try:
            for chunk in self.model.generate_content(
                prompt,
                stream=True
            ):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise Exception(f"Gemini error: {str(e)}")