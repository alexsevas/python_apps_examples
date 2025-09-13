# conda activate g4fpy311

# Модели pywhispercpp хранятся по умолчанию тут: AppData\Local\pywhispercpp\pywhispercpp\models

'''
pywhispercpp — это Python-обёртка над whisper.cpp (C/C++ реализация OpenAI Whisper на основе библиотеки ggml).
По умолчанию pip-колёсики — CPU-only; GPU (CUDA) работает только если вы соберёте/установите пакет с поддержкой CUDA
(или соберёте whisper.cpp с -DGGML_CUDA=1). whisper.cpp даёт маленький объём памяти, поддержку квантованных моделей и
несколько бэкендов (CUDA, Vulkan, CoreML, OpenVINO, OpenBLAS), поэтому в ряде сценариев (offline, на CPU или на Apple
Silicon) он предпочтительнее OpenAI-PyTorch Whisper; но при доступе к мощному GPU и когда важна максимальная точность —
оригинальная PyTorch-реализация иногда предпочтительнее.

whisper.cpp — это лёгкая, чисто C/C++ реализация inference для архитектуры Whisper, построенная на низкоуровневой
библиотеке ggml. В ней реализованы все этапы pipeline: предобработка аудио → mel-спектр → encoder/decoder transformer
inference → декодинг (greedy / beam / timestamping). Код ориентирован на минимальные зависимости и низкий расход памяти.

Ключевые особенности:
поддержка integer quantization (Q5/Q8 и др.),
смешанной F16/F32 точности, нулевые (минимальные) runtime-алокации,
использование SIMD/AVX/NEON на CPU.
'''

from pywhispercpp.model import Model

#model = Model('medium-q5_0') #загрузка модели из папки по умолчанию (или из интернета при ее отсутствии)
#model = Model('large-v3-turbo-q5_0')
#model = Model('large-v3-turbo')
model = Model("D:/AI/TalkLlamaFast/TalkLlama/ggml-medium-q5_0.bin") #загрузка модели из своего файла


#segments = model.transcribe('D:/397901813-bba1ac0a-fe6b-4947-b58d-ba99306d0339.mp3')
segments = model.transcribe('D:/audio_2_20-09-2023_13-02-08.ogg', language="ru")

for segment in segments:
    print(segment.text)



'''
Invalid model name `llarge-v3-turbo-q5_0`, available models are: ['base', 'base-q5_1', 'base-q8_0', 'base.en', 
'base.en-q5_1', 'base.en-q8_0', 'large-v1', 'large-v2', 'large-v2-q5_0', 'large-v2-q8_0', 'large-v3', 
'large-v3-q5_0', 'large-v3-turbo', 'large-v3-turbo-q5_0', 'large-v3-turbo-q8_0', 'medium', 'medium-q5_0', 
'medium-q8_0', 'medium.en', 'medium.en-q5_0', 'medium.en-q8_0', 'small', 'small-q5_1', 'small-q8_0', 'small.en', 
'small.en-q5_1', 'small.en-q8_0', 'tiny', 'tiny-q5_1', 'tiny-q8_0', 'tiny.en', 'tiny.en-q5_1', 'tiny.en-q8_0']
whisper_init_from_file_with_params_no_state: loading model from '(null)'
'''