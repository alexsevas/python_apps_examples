# conda allpy310

# pip install setuptools-rust
# pip install -U openai-whisper

import whisper
import pprint

model = whisper.load_model("medium") # Можно выбрать 'base', 'small', 'medium', 'large'
result = model.transcribe("D:\\Projects\\_Data_\\Audio_examples\\audio_RU_20sec.wav")

pprint.pprint(result["text"])