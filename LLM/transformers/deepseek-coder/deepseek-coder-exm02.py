'''
conda activate yolo8p311

pip install -U transformers accelerate torch

Запускаем DeepSeek у себя на компе с помощью Python
Рекомендации:
1. Проверьте доступную память GPU: Модель 6.7B требует около 13-14GB VRAM в формате float16. Убедитесь, что у вашей
видеокарты достаточно памяти.
2. Если нет GPU или недостаточно памяти: Уберите параметры `dtype` и `device_map`, чтобы модель загружалась на CPU:

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    trust_remote_code=True,
)

3. Для лучшей производительности на Windows: Включение Developer Mode действительно улучшит производительность кэширования
и сэкономит место на диске в долгосрочной перспективе.
'''


import os
# Отключаем предупреждение о symlinks (опционально)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "deepseek-ai/deepseek-coder-6.7b-base"

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    trust_remote_code=True,
    dtype=torch.float16,        # Исправлено: torch_dtype -> dtype
    device_map="auto"           # Теперь работает после установки accelerate
)
model.eval()

prompt = "Напиши telegram бота обратной связи на aiogram"

inputs = tokenizer(prompt, return_tensors="pt")
device = next(model.parameters()).device
inputs = {k: v.to(device) for k, v in inputs.items()}

with torch.inference_mode():
    outputs = model.generate(
        **inputs,
        max_new_tokens=180,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )

print(tokenizer.decode(outputs[0], skip_special_tokens=True))