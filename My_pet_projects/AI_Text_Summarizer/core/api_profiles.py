import os
from dotenv import load_dotenv

load_dotenv()

class APIProfiles:

    def __init__(self):

        self.openai = os.getenv("OPENAI_API_KEY")
        self.google = os.getenv("GOOGLE_API_KEY")

    def available_engines(self):

        engines = ["Ollama"]

        if self.openai:
            engines.append("OpenAI")

        if self.google:
            engines.append("Google")

        try:
            import g4f
            engines.append("g4f")
        except:
            pass

        return engines