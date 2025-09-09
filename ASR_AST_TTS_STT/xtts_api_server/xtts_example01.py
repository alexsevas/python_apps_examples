# Пример использования xtts-api-server через API

# conda activate allpy311 (любое ENV с requests)
# запустить D:\AI\t-0.2.0\xtts\xtts_wav2lip.bat (ENV xtts)

import requests
import os

text = "Это пример текста для синтэза речи. Раз, два, три, четыри, пять - вышел зайчик побухать."
speaker_id = "faramir"  # ID спикера (если используется предварительно обученная модель)
language = "ru"  # Язык текста (например, "en" для английского)
url = "http://localhost:8020/tts_stream?text=" + text + "&speaker_wav=" + speaker_id + "&language=" + language

response = requests.get(url)
if response.status_code == 200:
    # Сохраняем полученный WAV-файл
    with open("output.wav", "wb") as f:
        f.write(response.content)
else:
    print("Ошибка:", response.text)

# Воспроизводим файл
os.system("start output.wav")  # Для Windows


# Примеры голосов: D:\AI\talk-llama-fast-0.2.0\xtts\speakers