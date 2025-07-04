# conda allpy310

# pip install setuptools-rust
# pip install -U openai-whisper

# CMD: whisper -h

import whisper

model = whisper.load_model("large-v3")
result = model.transcribe("C:\\PROJECTS\\_DATA_\\audio_RU_20sec.wav")
print(result["text"])