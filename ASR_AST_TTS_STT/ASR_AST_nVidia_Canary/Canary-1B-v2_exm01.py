

from nemo.collections.asr.models import ASRModel

asr_model = ASRModel.from_pretrained("nvidia/canary-1b-v2")

output = asr_model.transcribe(['audio.wav'], source_lang='en', target_lang='en')
print(output[0].text)

output = asr_model.transcribe(['audio.wav'],
                             source_lang='en',
                             target_lang='fr',
                             timestamps=True)


'''
NVIDIA Canary-1B-v2
Мощная модель с 1 миллиардом параметров для автоматического распознавания речи (ASR) и перевода речи (AST) для 25 европейских языков

🔘Ключевые возможности

Многозадачность:
- Распознавание речи для всех 25 языков
- Перевод с английского на 24 языка 
- Перевод на английский с 24 языков

Поддерживаемые языки:
Болгарский, хорватский, чешский, датский, голландский, английский, эстонский, финский, французский, немецкий, греческий, 
венгерский, итальянский, латышский, литовский, мальтийский, польский, португальский, румынский, словацкий, словенский, 
испанский, шведский, русский, украинский

🔘Производительность

Скорость vs качество:
- Сравнимое качество с моделями в 3 раза больше
- До 10 раз быстрее аналогов
- Автоматическая пунктуация и капитализация
- Точные временные метки на уровне слов и сегментов

Результаты на бенчмарках:
- ASR WER: 7.15% (среднее по HuggingFace Open ASR Leaderboard)
- Перевод X→En COMET: 79.30 (Fleurs-24)
- Перевод En→X COMET: 84.56 (Fleurs-24)

ASR Performance (https://huggingface.co/nvidia/canary-1b-v2/resolve/main/plots/asr.png)
Translation Performance X-En (https://huggingface.co/nvidia/canary-1b-v2/resolve/main/plots/x_en.png)
Translation Performance En-X (https://huggingface.co/nvidia/canary-1b-v2/resolve/main/plots/en_x.png)

🔘Области применения

✅Конверсационный ИИ
✅Голосовые помощники 
✅Сервисы транскрипции
✅Генерация субтитров
✅Платформы голосовой аналитики

🔘Техническая архитектура

- Энкодер: FastConformer (32 слоя)
- Декодер: Transformer (8 слоев)
- Токенизатор: SentencePiece (16,384 токенов)
- Всего параметров: 978 миллионов

🔘 Устойчивость к шумам

- Без шума: 2.18% WER
- SNR 0dB: 5.08% WER
- SNR -5dB: 19.38% WER

🔘Обучающие данные

Модель обучена на 1.7 миллиона часов аудиоданных:
- 660,000 часов ASR
- 360,000 часов X→En перевода
- 690,000 часов En→X перевода

🔘Лицензия

Модель доступна под лицензией CC-BY-4.0 для коммерческого и некоммерческого использования.

Попробовать: Hugging Face Demo (https://huggingface.co/spaces/nvidia/canary-1b-v2)
'''