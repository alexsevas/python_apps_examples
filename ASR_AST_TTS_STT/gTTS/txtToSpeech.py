# conda activate allpy310, allpy311

# pip install gTTS
# online Работа - использует интернет-соединение

from gtts import gTTS
import os

file = open("data/test.txt", "r").read()

speech = gTTS(text=file, lang='en', slow=False)
speech.save("test.mp3")
os.system("test.mp3")
