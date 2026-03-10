try:
    from g4f.client import Client
    G4F_AVAILABLE = True
except ImportError:
    G4F_AVAILABLE = False

class G4FEngine:

    def __init__(self, model):
        if not G4F_AVAILABLE:
            raise Exception("g4f library not installed. Install with: pip install g4f")
        self.client = Client()
        self.model = model

    def stream(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"g4f error: {str(e)}")