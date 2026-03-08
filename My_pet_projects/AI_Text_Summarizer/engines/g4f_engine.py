import g4f

class G4FEngine:

    def __init__(self, model):
        self.model = model


    def stream(self, prompt):
        response = g4f.ChatCompletion.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            stream=True
        )
        for r in response:
            delta = r["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]