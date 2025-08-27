

from nemo.collections.asr.models import ASRModel

asr_model = ASRModel.from_pretrained("nvidia/canary-1b-v2")

output = asr_model.transcribe(['audio.wav'], source_lang='en', target_lang='en')
print(output[0].text)

output = asr_model.transcribe(['audio.wav'],
                             source_lang='en',
                             target_lang='fr',
                             timestamps=True)
