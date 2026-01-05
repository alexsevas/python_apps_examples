'''
conda activate yolo8p311

Запускаем DeepSeek у себя на компе с помощью Python
— работает локально (после скачивания весов);
— легко встраивается в Telegram/Discord/CLI;
— можно ускорить на GPU через device_map="auto".
Если памяти мало — есть квантованные версии (4bit/8bit) и GGUF.

pip install -U transformers accelerate torch
'''


from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "deepseek-ai/deepseek-coder-6.7b-base"

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    trust_remote_code=True,
    torch_dtype=torch.float16,   # если GPU поддерживает fp16
    device_map="auto"            # если есть GPU — будет использовать её
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
        do_sample=True,      # ВАЖНО: иначе temperature не влияет
        temperature=0.7,
        top_p=0.9
    )

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
