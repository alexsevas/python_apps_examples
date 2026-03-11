"""
Тестовый скрипт для проверки работы Ollama
"""

from core.ollama_helper import OllamaHelper

def test_ollama():
    helper = OllamaHelper()
    
    print("=" * 50)
    print("Тест Ollama Helper")
    print("=" * 50)
    
    # Проверка статуса
    print("\n1. Проверка статуса Ollama...")
    is_running = helper.is_running()
    print(f"   Ollama запущена: {is_running}")
    
    if not is_running:
        print("\n   ⚠️  Ollama не запущена!")
        print("   Запустите Ollama командой: ollama serve")
        return
    
    # Получение локальных моделей
    print("\n2. Получение локальных моделей...")
    local_models = helper.get_local_models()
    if local_models:
        print(f"   Найдено {len(local_models)} локальных моделей:")
        for model in local_models:
            print(f"   📦 {model}")
    else:
        print("   ⚠️  Локальные модели не найдены")
        print("   Скачайте модель командой: ollama pull llama3.2")
    
    # Получение облачных моделей
    print("\n3. Получение облачных моделей...")
    cloud_models = helper.get_cloud_models()
    print(f"   Доступно {len(cloud_models)} облачных моделей:")
    for model_info in cloud_models[:5]:  # Показываем первые 5
        print(f"   ☁️  {model_info['name']} - {model_info['description']}")
    print(f"   ... и еще {len(cloud_models) - 5} моделей")
    
    print("\n" + "=" * 50)
    print("Тест завершен!")
    print("=" * 50)

if __name__ == "__main__":
    test_ollama()
