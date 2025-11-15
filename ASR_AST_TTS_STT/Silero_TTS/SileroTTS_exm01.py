# conda activate ttsp311

import torch
import torchaudio
import sounddevice as sd

# Загрузка с самой стабильной моделью
model, _ = torch.hub.load(
    'snakers4/silero-models',
    model='silero_tts',
    language='ru',
    speaker='v4_ru'  # Самая новая универсальная модель для русского
)

# Генерация
text = "Привет! Это работает на русском языке!"
# `speaker` should be in aidar, baya, kseniya, xenia, eugene, random
audio = model.apply_tts(text=text, speaker='xenia', sample_rate=48000)

# Воспроизведение
sd.play(audio.numpy(), 48000)
sd.wait()
print("✅ Готово!")