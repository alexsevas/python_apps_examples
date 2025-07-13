# conda activate extras2

# pip install -U g4f
# pip install -U nodriver platformdirs

import g4f
import time
import asyncio
from datetime import datetime
from g4f.models import ModelUtils

# Фильтрация текстовых моделей
def get_text_models():
    excluded_keywords = [
        'vision', 'image', 'img', 'dall-e', 'clip', 'whisper', 'flux',
        'tts', 'speech', 'audio', 'ocr', 'stable-diffusion', 'sd'
    ]

    return [
        model for model in ModelUtils.convert
        if not any(keyword in model.lower() for keyword in excluded_keywords)
    ]

# Асинхронная функция для получения ответа от модели
async def get_model_response(model, messages):
    try:
        start_time = time.time()
        response = await g4f.ChatCompletion.create_async(
            model=model,
            messages=messages,
        )
        response_time = time.time() - start_time
        return response, response_time
    except Exception as e:
        return f"Ошибка: {str(e)}", 0

# Основной цикл чата
async def chat_with_model(model_name):
    print(f"\n🚀 Начат чат с моделью: {model_name}")
    print("💬 Введите ваше сообщение (или 'exit' для выхода)")
    print("=" * 50)

    messages = []
    start_time = datetime.now()
    print(f"⏱ Время начала сессии: {start_time.strftime('%H:%M:%S')}")

    while True:
        user_input = input("\nВы: ")

        if user_input.lower() == 'exit':
            print("\nСессия завершена.")
            session_duration = datetime.now() - start_time
            print(f"⏱ Общая продолжительность сессии: {session_duration}")
            return

        messages.append({"role": "user", "content": user_input})

        print(f"\n⌛ {model_name} думает...")
        response, response_time = await get_model_response(model_name, messages)

        messages.append({"role": "assistant", "content": response})

        print(f"\n{model_name}: {response}")
        print(f"⏱ Время ответа: {response_time:.2f} секунд")
        print("-" * 50)

# Главная функция
async def main():
    # Получаем список текстовых моделей
    text_models = get_text_models()

    if not text_models:
        print("❌ Не найдено доступных текстовых моделей.")
        return

    # Выводим список моделей с номерами
    print("\n📚 Доступные текстовые модели:")
    for i, model in enumerate(text_models, 1):
        print(f"{i}. {model}")

    # Выбор модели
    while True:
        try:
            choice = int(input("\n👉 Введите номер модели для чата: "))
            if 1 <= choice <= len(text_models):
                selected_model = text_models[choice - 1]
                break
            else:
                print(f"❌ Пожалуйста, введите число от 1 до {len(text_models)}")
        except ValueError:
            print("❌ Пожалуйста, введите корректный номер")

    # Запускаем чат с выбранной моделью
    await chat_with_model(selected_model)

if __name__ == "__main__":
    asyncio.run(main())