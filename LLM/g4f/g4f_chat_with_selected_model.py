# conda activate extras2

# pip install -U g4f
# pip install -U nodriver platformdirs
# pip install -U curl_cffi

import g4f
import time
import pprint
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

            pprint.pprint(f"\n{selected_model}: {response}")
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
    # Получаем список текстовых моделей
    text_models = get_text_models()

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
    asyncio.run(main())

'''
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