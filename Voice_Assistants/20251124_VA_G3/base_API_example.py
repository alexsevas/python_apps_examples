import google.generativeai as genai
import pprint

# 1. Вставь свой API ключ сюда
API_KEY = "___"


def test_gemini():
    print(f"1. Настройка API ключа...")
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        print(f"Ошибка конфигурации: {e}")
        return

    # 2. Проверка доступности моделей (Тест соединения)
    print("2. Проверка соединения с серверами Google...")
    try:
        # Пытаемся получить список моделей. Если тут упадет - значит нет сети/VPN
        models = list(genai.list_models())
        print(f"   Успешно! Доступно моделей: {len(models)}")
        # Для отладки можно вывести названия, например:
        # for m in models:
        #     if 'generateContent' in m.supported_generation_methods:
        #         print(m.name)
    except Exception as e:
        print(f"ОШИБКА СОЕДИНЕНИЯ: {e}")
        print("СОВЕТ: Если вы в РФ, убедитесь, что включен VPN (Tunneled mode) или системный прокси.")
        return

    # 3. Тестовый запрос
    print("3. Отправка тестового запроса (gemini-2.5-flash)...")
    try:
        # Используем gemini-1.5-flash, она быстрее чем gemini-pro
        model = genai.GenerativeModel('gemini-2.5-flash')

        #response = model.generate_content("Привет! Напиши одно предложение о том, как у тебя дела.")
        response = model.generate_content("Подробно расскажи о том,как возникла Вселенная и чем все может закончится в итоге")

        print("\n=== ОТВЕТ ОТ GEMINI ===")
        pprint.pprint(response.text)
        print("=======================")

    except Exception as e:
        print(f"ОШИБКА ГЕНЕРАЦИИ: {e}")


if __name__ == "__main__":
    test_gemini()