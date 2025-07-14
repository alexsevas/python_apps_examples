# CHAT WITH LLM USING THE G4F LIBRARY
#
# conda activate extras2
# pip install -U g4f nodriver platformdirs curl_cffi browser_cookie3

'''
2025-07-13 - cтабильно работают данные модели:

/model 1 - gpt-4
/model 3 - gpt-4o-mini
/model 11 - gpt-4.1-mini
/model 12 - gpt-4.1-nano
/model 10 - gpt-4.1
/model 36 - phi-4
/model 42 - gemini-1.5-flash
/model 43 - gemini-1.5-pro
/model 56 - gemma-3-27b
/model 57 - gemma-3n-e4b
/model 58 - blackboxai
/model 59 - command-r
/model 62 - command-a
/model 66 - qwen-2-vl-72b
/model 70 - qwen-2.5-coder-32b
/model 72 - qwen-2.5-max
/model 73 - qwen-2.5-vl-72b (режет текст, разобраться)
/model 74 - qwen-3-235b
/model 81 - qwq-32b
/model 93 - deepseek-r1-0528
/model 94 - deepseek-r1-0528-turbo
/model 98 - grok-3-mini
/model 102 - sonar-reasoning
/model 103 - sonar-reasoning-pro
/model 104 - r1-1776 (ризонинг)
/model 105 - nemotron-70b (Долго)
/model 112 - evil
'''

import g4f
import time
import asyncio
import os
from datetime import datetime
from g4f import Provider
from g4f.models import Model, ModelUtils


# Создаем папку для cookies, если её нет
def ensure_cookie_dir():
    appdata = os.getenv('APPDATA')
    if appdata is None:
        appdata = os.path.expanduser('~')
    cookie_dir = os.path.join(appdata, 'g4f', 'cookies')
    if not os.path.exists(cookie_dir):
        os.makedirs(cookie_dir, exist_ok=True)
        print(f"📁 Создана папка для cookies: {cookie_dir}")
    return cookie_dir


# Получаем список доступных текстовых провайдеров
def get_available_text_providers():
    excluded_keywords = [
        'vision', 'image', 'img', 'dall-e', 'clip', 'whisper', 'flux',
        'tts', 'speech', 'audio', 'ocr', 'stable-diffusion', 'sd'
    ]

    providers = []
    print("🔍 Сканирую доступные провайдеры...")

    for attr in dir(Provider):
        if attr.startswith('__') or attr == 'BaseProvider':
            continue

        provider = getattr(Provider, attr)
        if not hasattr(provider, 'model') and not hasattr(provider, 'supported_models'):
            continue

        # Проверяем, является ли модель текстовой
        if hasattr(provider, 'model'):
            model_name = provider.model
            if any(kw in model_name.lower() for kw in excluded_keywords):
                continue
        elif hasattr(provider, 'supported_models'):
            if any(any(kw in m.lower() for kw in excluded_keywords) for m in provider.supported_models):
                continue

        providers.append(provider)

    print(f"✅ Найдено {len(providers)} текстовых провайдеров")
    return providers


# Получаем список доступных текстовых моделей
def get_available_text_models():
    excluded_keywords = [
        'vision', 'image', 'img', 'dall-e', 'clip', 'whisper', 'flux',
        'tts', 'speech', 'audio', 'ocr', 'stable-diffusion', 'sd'
    ]

    print("🔍 Сканирую доступные модели...")
    models = [
        model for model in ModelUtils.convert
        if not any(keyword in model.lower() for keyword in excluded_keywords)
    ]
    print(f"✅ Найдено {len(models)} текстовых моделей")
    return models


# Асинхронная функция для получения потокового ответа от модели
async def get_streaming_response(model, messages):
    try:
        print("🔄 Пробую основной провайдер...")
        start_time = time.time()

        # Пробуем потоковый режим с основным провайдером
        try:
            response_stream = g4f.ChatCompletion.create_async(
                model=model,
                messages=messages,
                stream=True
            )
            print("✅ Основной провайдер сработал!")
            return response_stream, start_time, "основной"
        except Exception as stream_error:
            print(f"❌ Потоковый режим не поддерживается: {str(stream_error)}")
            # Пробуем обычный режим
            response_coro = g4f.ChatCompletion.create_async(
                model=model,
                messages=messages,
            )
            response = await response_coro
            print("✅ Основной провайдер сработал (обычный режим)!")
            return response, start_time, "основной"

    except Exception as e:
        print(f"❌ Основной провайдер не сработал: {str(e)}")
        print("🔄 Начинаю перебор альтернативных провайдеров...")

        # Пробуем разные провайдеры, пока не найдем работающий
        providers = get_available_text_providers()
        print(f"📋 Найдено {len(providers)} доступных провайдеров")

        for i, provider in enumerate(providers, 1):
            try:
                print(f"🔄 [{i}/{len(providers)}] Пробую провайдер: {provider.__name__}")
                start_time = time.time()

                # Сначала пробуем потоковый режим
                try:
                    response_stream = g4f.ChatCompletion.create_async(
                        model=model,
                        messages=messages,
                        provider=provider,
                        stream=True
                    )
                    print(f"✅ Провайдер {provider.__name__} сработал (потоковый режим)!")
                    return response_stream, start_time, provider.__name__
                except Exception as stream_error:
                    print(f"⚠️ Потоковый режим не поддерживается, пробую обычный...")
                    response_coro = g4f.ChatCompletion.create_async(
                        model=model,
                        messages=messages,
                        provider=provider
                    )
                    response = await response_coro
                    print(f"✅ Провайдер {provider.__name__} сработал (обычный режим)!")
                    return response, start_time, provider.__name__

            except Exception as provider_error:
                print(f"❌ Провайдер {provider.__name__} не сработал: {str(provider_error)}")
                continue

        print("❌ Все провайдеры не сработали")
        return f"Все провайдеры не сработали. Ошибка: {str(e)}", 0, "ошибка"


# Функция для отображения списка моделей
def show_model_list(models, current_model=None):
    print("\n📚 Доступные текстовые модели:")
    for i, model in enumerate(models, 1):
        prefix = "➤ " if current_model and model == current_model else "  "
        print(f"{prefix}{i}. {model}")


# Основной цикл чата
async def chat_with_model(selected_model, text_models, messages=None):
    if messages is None:
        messages = []

    print(f"\n🚀 Начат чат с моделью: {selected_model}")
    print(
        "💬 Введите сообщение (команды: /list - модели, /model N - сменить модель, /clear - очистить историю, /exit - выход)")
    print("=" * 50)

    session_start_time = datetime.now()
    print(f"⏱ Время начала сессии: {session_start_time.strftime('%H:%M:%S')}")

    while True:
        try:
            user_input = input("\nВы: ").strip()

            # Обработка команд
            if user_input.lower() == '/exit':
                print("\nСессия завершена.")
                session_duration = datetime.now() - session_start_time
                print(f"⏱ Общая продолжительность сессии: {session_duration}")
                return messages

            if user_input.lower() == '/list':
                show_model_list(text_models, selected_model)
                continue

            if user_input.lower() == '/clear':
                messages = []
                print("\n🔄 История диалога очищена")
                continue

            if user_input.lower().startswith('/model'):
                parts = user_input.split()
                if len(parts) > 1:
                    try:
                        new_index = int(parts[1]) - 1
                        if 0 <= new_index < len(text_models):
                            new_model = text_models[new_index]
                            if new_model == selected_model:
                                print(f"ℹ️ Вы уже используете модель {selected_model}")
                            else:
                                print(f"\n🔄 Смена модели: {selected_model} → {new_model}")
                                selected_model = new_model
                        else:
                            print(f"❌ Недопустимый номер модели. Введите число от 1 до {len(text_models)}")
                    except ValueError:
                        print("❌ Неверный формат команды. Используйте: /model НОМЕР")
                else:
                    show_model_list(text_models, selected_model)
                continue

            # Обычное сообщение пользователя
            messages.append({"role": "user", "content": user_input})

            print(f"\n⌛ {selected_model} думает...")
            result = await get_streaming_response(selected_model, messages)

            if len(result) == 3:
                response, response_start_time, provider_name = result

                if isinstance(response, str):
                    # Обычный режим (не потоковый)
                    response_time = time.time() - response_start_time
                    messages.append({"role": "assistant", "content": response})
                    print(f"\n{selected_model}: {response}")
                    print(f"⏱ Время ответа: {response_time:.2f} секунд")
                else:
                    # Потоковый режим
                    print(f"\n{selected_model} ({provider_name}): ", end="", flush=True)
                    full_response = ""

                    try:
                        # Обрабатываем потоковый ответ
                        async for chunk in response:
                            if chunk:
                                print(chunk, end="", flush=True)
                                full_response += str(chunk)
                        print()  # Новая строка после завершения

                        response_time = time.time() - response_start_time
                        messages.append({"role": "assistant", "content": full_response})
                        print(f"⏱ Время ответа: {response_time:.2f} секунд")
                    except Exception as stream_error:
                        print(f"\n❌ Ошибка потокового вывода: {str(stream_error)}")
                        if full_response:
                            messages.append({"role": "assistant", "content": full_response})
            else:
                # Ошибка
                error_message = result
                print(f"\n❌ {error_message}")

            print("-" * 50)

        except KeyboardInterrupt:
            print("\n\nСессия прервана пользователем.")
            return messages
        except Exception as e:
            print(f"\n⚠️ Произошла ошибка: {str(e)}")
            print("Попробуйте еще раз или смените модель (/model)")


# Главная функция
async def main():
    print("🚀 Инициализация программы...")

    # Убедимся, что папка для cookies существует
    print("📁 Проверяю папку для cookies...")
    ensure_cookie_dir()

    # Получаем список текстовых моделей
    print("🔍 Загружаю список доступных моделей...")
    text_models = get_available_text_models()

    if not text_models:
        print("❌ Не найдено доступных текстовых моделей.")
        return

    print("✅ Инициализация завершена!")

    # Начальный выбор модели
    show_model_list(text_models)

    current_messages = []
    selected_model = None

    while True:
        try:
            if not selected_model:
                choice = int(input("\n👉 Введите номер модели для чата: "))
                if 1 <= choice <= len(text_models):
                    selected_model = text_models[choice - 1]
                    print(f"🔄 Инициализирую модель: {selected_model}")
                else:
                    print(f"❌ Пожалуйста, введите число от 1 до {len(text_models)}")
                    continue

            # Запускаем чат с выбранной моделью
            current_messages = await chat_with_model(
                selected_model,
                text_models,
                current_messages
            )

            # После завершения чата спрашиваем о дальнейших действиях
            print("\nВыберите действие:")
            print("1. Продолжить чат с текущей моделью")
            print("2. Выбрать другую модель")
            print("3. Выйти")

            action = input("Ваш выбор (1-3): ").strip()

            if action == '3':
                print("\nДо свидания!")
                break
            elif action == '2':
                selected_model = None
                show_model_list(text_models)
            elif action != '1':
                print("⏩ Продолжаем с текущей моделью...")

        except ValueError:
            print("❌ Пожалуйста, введите корректный номер")
        except KeyboardInterrupt:
            print("\n\nПрограмма завершена.")
            break


if __name__ == "__main__":
    # Добавляем обработку событий для Windows
    if os.name == 'nt':
        import asyncio

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())