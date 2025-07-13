# conda activate extras2
# Работает оффлайн - интернет не нужен

import g4f
from g4f.models import ModelUtils

# Фильтр для исключения мультимодальных и специализированных моделей
excluded_keywords = [
    'vision', 'image', 'img', 'dall-e', 'clip', 'whisper', 'tts',
    'speech', 'audio', 'ocr', 'stable-diffusion', 'sd', 'flux'
]

# Получаем и фильтруем модели
text_models = [
    model for model in ModelUtils.convert
    if not any(keyword in model.lower() for keyword in excluded_keywords)
]

print("📚 Рабочие текстовые модели:")
print('\n'.join([f"- {model}" for model in text_models]))
print(f"\nВсего найдено: {len(text_models)} текстовых моделей")


'''
20250713
----------
📚 Рабочие текстовые модели:
- gpt-4
- gpt-4o
- gpt-4o-mini
- o1
- o1-mini
- o3-mini
- o3-mini-high
- o4-mini
- o4-mini-high
- gpt-4.1
- gpt-4.1-mini
- gpt-4.1-nano
- gpt-4.5
- meta-ai
- llama-2-7b
- llama-2-70b
- llama-3-8b
- llama-3-70b
- llama-3.1-8b
- llama-3.1-70b
- llama-3.1-405b
- llama-3.2-1b
- llama-3.2-3b
- llama-3.2-11b
- llama-3.2-90b
- llama-3.3-70b
- llama-4-scout
- llama-4-maverick
- mistral-7b
- mixtral-8x7b
- mistral-nemo
- mistral-small-24b
- mistral-small-3.1-24b
- hermes-2-dpo
- phi-3.5-mini
- phi-4
- phi-4-multimodal
- phi-4-reasoning-plus
- wizardlm-2-7b
- wizardlm-2-8x22b
- gemini-2.0
- gemini-1.5-flash
- gemini-1.5-pro
- gemini-2.0-flash
- gemini-2.0-flash-thinking
- gemini-2.0-flash-thinking-with-apps
- gemini-2.5-flash
- gemini-2.5-pro
- codegemma-7b
- gemma-2b
- gemma-1.1-7b
- gemma-2-9b
- gemma-2-27b
- gemma-3-4b
- gemma-3-12b
- gemma-3-27b
- gemma-3n-e4b
- blackboxai
- command-r
- command-r-plus
- command-r7b
- command-a
- qwen-1.5-7b
- qwen-2-72b
- qwen-2-vl-7b
- qwen-2-vl-72b
- qwen-2.5
- qwen-2.5-7b
- qwen-2.5-72b
- qwen-2.5-coder-32b
- qwen-2.5-1m
- qwen-2.5-max
- qwen-2.5-vl-72b
- qwen-3-235b
- qwen-3-32b
- qwen-3-30b
- qwen-3-14b
- qwen-3-4b
- qwen-3-1.7b
- qwen-3-0.6b
- qwq-32b
- deepseek-v3
- deepseek-r1
- deepseek-r1-turbo
- deepseek-r1-distill-llama-70b
- deepseek-r1-distill-qwen-1.5b
- deepseek-r1-distill-qwen-14b
- deepseek-r1-distill-qwen-32b
- deepseek-prover-v2
- deepseek-prover-v2-671b
- deepseek-v3-0324
- deepseek-v3-0324-turbo
- deepseek-r1-0528
- deepseek-r1-0528-turbo
- janus-pro-7b
- grok-2
- grok-3
- grok-3-mini
- grok-3-r1
- sonar
- sonar-pro
- sonar-reasoning
- sonar-reasoning-pro
- r1-1776
- nemotron-70b
- dolphin-2.6
- dolphin-2.9
- airoboros-70b
- lzlv-70b
- lfm-40b
- aria
- evil

Всего найдено: 112 текстовых моделей
'''