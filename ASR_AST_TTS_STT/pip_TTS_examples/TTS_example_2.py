# pip install --cache-dir D:\.conda\new_pip_cashe TTS - установилось в allpy311 без ошибок


from TTS.api import TTS
import torch
import torchaudio

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True)
tts.to(torch.device("cuda"))
tts.tts_to_file(text="My first text to speech!", file_path="output.wav")
