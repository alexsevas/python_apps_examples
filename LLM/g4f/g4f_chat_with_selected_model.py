# conda activate extras2

# pip install -U g4f nodriver platformdirs curl_cffi browser_cookie3

# CHAT WITH LLM USING THE G4F LIBRARY
# 2025-07-13:
# Стабильно работают:
# /model 1 - gpt-4
# /model 3 - gpt-4o-mini
# /model 11 - gpt-4.1-mini
# /model 12 - gpt-4.1-nano
# /model 10 - gpt-4.1
# /model 36 - phi-4
# /model 42 - gemini-1.5-flash
# /model 43 - gemini-1.5-pro
# /model 56 - gemma-3-27b
# /model 57 - gemma-3n-e4b
# /model 58 - blackboxai
# /model 59 - command-r
# /model 62 - command-a
# /model 66 - qwen-2-vl-72b
# /model 70 - qwen-2.5-coder-32b
# /model 72 - qwen-2.5-max
# /model 73 - qwen-2.5-vl-72b (режет текст, разобраться)
# /model 74 - qwen-3-235b
# /model 81 - qwq-32b
# /model 93 - deepseek-r1-0528
# /model 94 - deepseek-r1-0528-turbo
# /model 98 - grok-3-mini
# /model 102 - sonar-reasoning
# /model 103 - sonar-reasoning-pro
# /model 104 - r1-1776 (ризонинг)
# /model 105 - nemotron-70b (Долго)
# /model 112 - evil


import g4f
import time
import asyncio
import os
from datetime import datetime
from g4f import Provider
from g4f.models import Model, ModelUtils


# Создаем папку для cookies, если её нет
def ensure_cookie_dir():
    cookie_dir = os.path.join(os.getenv('APPDATA'), 'g4f', 'cookies')
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

    return providers


# Получаем список доступных текстовых моделей
def get_available_text_models():
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
        # Пробуем разные провайдеры, пока не найдем работающий
        for provider in get_available_text_providers():
            try:
                print(f"⚠️ Проблема с основным провайдером, пробую: {provider.__name__}")
                start_time = time.time()
                response = await g4f.ChatCompletion.create_async(
                    model=model,
                    messages=messages,
                    provider=provider
                )
                response_time = time.time() - start_time
                return response, response_time
            except:
                continue

        return f"Все провайдеры не сработали. Ошибка: {str(e)}", 0


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

    start_time = datetime.now()
    print(f"⏱ Время начала сессии: {start_time.strftime('%H:%M:%S')}")

    while True:
        try:
            user_input = input("\nВы: ").strip()

            # Обработка команд
            if user_input.lower() == '/exit':
                print("\nСессия завершена.")
                session_duration = datetime.now() - start_time
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
            response, response_time = await get_model_response(selected_model, messages)

            messages.append({"role": "assistant", "content": response})

            print(f"\n{selected_model}: {response}")
            print(f"⏱ Время ответа: {response_time:.2f} секунд")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n\nСессия прервана пользователем.")
            return messages
        except Exception as e:
            print(f"\n⚠️ Произошла ошибка: {str(e)}")
            print("Попробуйте еще раз или смените модель (/model)")


# Главная функция
async def main():
    # Убедимся, что папка для cookies существует
    ensure_cookie_dir()

    # Получаем список текстовых моделей
    text_models = get_available_text_models()

    if not text_models:
        print("❌ Не найдено доступных текстовых моделей.")
        return

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

'''
---------
v 0.0.03
---------
CHANGE:
1. Автоматизация работы с cookies:
   - Реализована функция `ensure_cookie_dir()`
   - Автоматическое создание папки `%APPDATA%\g4f\cookies`
   - Устранение ошибок `FileNotFoundError`

2. Динамическая работа с провайдерами:
   - Замена жестко заданных провайдеров (Aichat/DeepAi) на адаптивную систему
   - Функция `get_available_text_providers()` для автоматического определения доступных провайдеров
   - Перебор всех рабочих провайдеров при ошибках

3. Улучшенная обработка ошибок:
   - Многоуровневая система восстановления после сбоев
   - Автоматический переход между провайдерами
   - Понятные сообщения об ошибках для пользователя

4. Повышение стабильности:
   - Двойная фильтрация моделей (текстовые vs мультимодальные)
   - Специальная обработка для Windows (`WindowsSelectorEventLoopPolicy`)
   - Защита от изменений в API библиотеки g4f

5. Автоматизация и адаптивность:
   - Динамическое определение доступных провайдеров
   - Независимость от конкретных имен провайдеров
   - Автоматическое восстановление после ошибок API
   
FIX:
Проблема - Решение 
---------------------
- `FileNotFoundError` (cookies) - Автоматическое создание нужных директорий 
- Ошибки 403 (Copilot) - Динамический выбор альтернативных провайдеров 
- `AttributeError` (провайдеры) - Автоматическое обнаружение доступных провайдеров 
- Проблемы асинхронности (Windows) - Специальная политика событий 
- Нестабильность провайдеров - Последовательный перебор всех доступных вариантов 
- Устаревшие модели - Динамическое обновление списка при запуске 

FINAL:
Программа теперь полностью самодостаточна:
- Автоматически адаптируется к изменениям в библиотеке g4f
- Работает без ручной настройки провайдеров
- Обеспечивает максимальную стабильность через систему автоматического восстановления
- Предоставляет одинаково надежную работу на Windows и других ОС
- Сохраняет пользовательский опыт при изменениях API

---------
v 0.0.02
---------
Новые возможности:

1. Команды для управления чатом:
   - `/list` - показать список доступных моделей
   - `/model N` - сменить модель на указанный номер
   - `/clear` - очистить историю диалога
   - `/exit` - завершить текущую сессию

2. Сохранение контекста:
   - История диалога сохраняется при смене модели
   - Можно продолжить разговор с новой моделью с того же места

3. Интерактивный интерфейс:
   - Текущая модель выделяется в списке (стрелкой ➤)
   - После завершения сессии предлагаются дальнейшие действия
   - Обработка ошибок и некорректного ввода

4. Улучшенная навигация:
   - Возврат к списку моделей без перезапуска программы
   - Продолжение работы с текущей моделью после завершения сессии
   - Возможность очистки истории в любой момент
   
---------
v 0.0.01
---------
1. Фильтрация моделей:
   - Автоматически исключает мультимодальные модели (работающие с изображениями, аудио и т.д.)
   - Оставляет только текстовые модели

2. Интерфейс выбора:
   - Модели выводятся с порядковыми номерами
   - Проверка корректности ввода номера
   - Защита от неверного ввода

3. Чат-режим:
   - Фиксация времени начала сессии
   - Измерение времени ответа для каждого запроса
   - История диалога сохраняется в течение сессии
   - Поддержка многострочного ввода

4. Особенности работы:
   - Использует асинхронные вызовы для стабильной работы
   - Автоматически обрабатывает ошибки API
   - Простой выход по команде "exit"
   - Показывает общее время сессии при завершении

5. Форматирование вывода:
   - Четкое разделение сообщений пользователя и модели
   - Временные метки для каждого ответа
   - Визуальные разделители для удобства чтения

'''