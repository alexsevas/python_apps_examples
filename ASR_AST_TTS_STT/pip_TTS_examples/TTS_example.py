# pip install --cache-dir D:\.conda\new_pip_cashe TTS - установилось в allpy311 без ошибок


from TTS.api import TTS

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True, gpu=True)
tts.tts_to_file(text="My first text to speech with HiFiGAN!", file_path="output.wav")

'''
1) gpu will be deprecated. Please use tts.to(device) - Это предупреждение говорит, что в будущих версиях Coqui TTS нужно делать так:

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True)
tts.to(torch.device("cuda"))
tts.tts_to_file(text="My first text to speech!", file_path="output.wav")

2) torch.load weights_only=False — обычное предупреждение безопасности, оно никак не мешает синтезу.
3) Время синтеза ~0.66 с для одного предложения → очень быстро, Real-time factor <1, что значит работает быстрее реального времени.
'''


