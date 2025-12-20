# Преобразование текста в речь с помощью PyTorch.

# pip install git+https://github.com/as-ideas/DeepPhonemizer.git

import sys
import torch
import torchaudio
import matplotlib.pyplot as plt
import soundfile as sf  # Для сохранения WAV

# -------------------------------
# Проверка Python и устройства
# -------------------------------
print("Python executable:", sys.executable)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# -------------------------------
# Загрузка TTS пайплайна
# -------------------------------
bundle = torchaudio.pipelines.TACOTRON2_WAVERNN_PHONE_LJSPEECH

# Text processor
processor = bundle.get_text_processor()

# Tacotron2 на GPU
tacotron2 = bundle.get_tacotron2().to(device)

# WaveRNN на CPU (стабильнее на Windows)
vocoder = bundle.get_vocoder().cpu()

# -------------------------------
# Входной текст
# -------------------------------
text = "If you wanna be OK, love the woman every day!"

# -------------------------------
# Inference
# -------------------------------
with torch.inference_mode():
    # Преобразуем текст в тензор
    processed, lengths = processor(text)
    processed = processed.to(device)
    lengths = lengths.to(device)

    # Tacotron2: text -> mel-spectrogram
    spec, spec_lengths, _ = tacotron2.infer(processed, lengths)

    # WaveRNN: mel -> waveform
    waveforms, wave_lengths = vocoder(spec.cpu(), spec_lengths.cpu())

# -------------------------------
# Визуализация
# -------------------------------
plt.figure(figsize=(16, 5))
plt.imshow(spec[0].cpu().detach(), origin="lower", aspect="auto")
plt.title("Generated Mel-Spectrogram")
plt.colorbar()
plt.tight_layout()
plt.show()

plt.figure(figsize=(16, 4))
plt.plot(waveforms[0].cpu().detach())
plt.title("Generated Waveform")
plt.tight_layout()
plt.show()

# -------------------------------
# Сохранение аудио
# -------------------------------
sf.write("tts_output.wav", waveforms[0].cpu().detach().numpy(), samplerate=vocoder.sample_rate)
print("Saved to tts_output.wav")
