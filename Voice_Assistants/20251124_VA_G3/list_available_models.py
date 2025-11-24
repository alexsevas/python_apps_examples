import google.generativeai as genai

API_KEY = "___"


def list_available_models():
    genai.configure(api_key=API_KEY)

    print("Запрашиваю список моделей...")
    try:
        # Получаем все модели
        all_models = list(genai.list_models())

        print(f"\n=== ДОСТУПНЫЕ МОДЕЛИ ({len(all_models)} всего) ===")
        valid_models = []

        for m in all_models:
            # Нам нужны только те, что поддерживают генерацию контента (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                valid_models.append(m.name)

        print("============================================")

        if valid_models:
            print(f"\nРЕКОМЕНДАЦИЯ: Используйте в коде имя: '{valid_models[0]}'")
            # Попробуем сделать тестовый запрос к первой найденной модели
            test_model_name = valid_models[0]
            print(f"\nТестирую модель: {test_model_name} ...")

            model = genai.GenerativeModel(test_model_name)
            response = model.generate_content("Привет!")
            print(f"ОТВЕТ ПОЛУЧЕН: {response.text}")

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    list_available_models()