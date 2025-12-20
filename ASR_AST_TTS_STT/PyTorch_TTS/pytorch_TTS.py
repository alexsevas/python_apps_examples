# Преобразование текста в речь с помощью PyTorch.


import torchaudio
import torch
import matplotlib.pyplot as plt
import IPython.display

bundle = torchaudio.pipelines.TACOTRON2_WAVERNN_PHONE_LJSPEECH

processor = bundle.get_text_processor()
tacotron2 = bundle.get_tacotron2().to(device)  # Move model to the desired device
vocoder = bundle.get_vocoder().to(device)      # Move model to the desired device

text = " My first text to speech!"

with torch.inference_mode():
    processed, lengths = processor(text)
    processed = processed.to(device)      # Move processed text data to the device
    lengths = lengths.to(device)          # Move lengths data to the device
    spec, spec_lengths, _ = tacotron2.infer(processed, lengths)
    waveforms, lengths = vocoder(spec, spec_lengths)


fig, [ax1, ax2] = plt.subplots(2, 1, figsize=(16, 9))
ax1.imshow(spec[0].cpu().detach(), origin="lower", aspect="auto")  # Display the generated spectrogram
ax2.plot(waveforms
             [0].cpu().detach())                             # Display the generated waveform7. Play the generated audio using IPython.display.Audio
IPython.display.Audio(waveforms[0:1].cpu(), rate=vocoder.sample_rate)