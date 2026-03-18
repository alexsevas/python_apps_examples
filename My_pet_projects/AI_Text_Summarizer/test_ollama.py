"""
Тестовый скрипт для проверки работы Ollama
"""

from core.ollama_helper import OllamaHelper
import time

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
    
    # Проверка загруженных моделей
    print("\n4. Проверка моделей в памяти...")
    loaded_models = helper.get_loaded_models()
    if loaded_models:
        print(f"   В памяти загружено {len(loaded_models)} моделей:")
        for model_info in loaded_models:
            model_name = model_info.get("name", "unknown")
            size_vram = model_info.get("size_vram", 0) / (1024**3)  # В GB
            print(f"   🔥 {model_name} (VRAM: {size_vram:.2f} GB)")
    else:
        print("   ✅ Нет моделей в памяти")
    
    # Тест выгрузки моделей
    if loaded_models:
        print("\n5. Тест выгрузки моделей...")
        print("   Выгружаем все модели из памяти...")
        success = helper.unload_all_models()
        if success:
            print("   ✅ Команда выгрузки выполнена")
        else:
            print("   ⚠️  Ошибка при выгрузке")
        
        # Проверяем снова через 2 секунды
        print("   Ждем 2 секунды...")
        time.sleep(2)
        
        loaded_after = helper.get_loaded_models()
        if not loaded_after:
            print("   ✅ Все модели успешно выгружены из памяти!")
        else:
            print(f"   ⚠️  В памяти все еще {len(loaded_after)} моделей:")
            for model_info in loaded_after:
                print(f"      {model_info.get('name', 'unknown')}")
    
    print("\n" + "=" * 50)
    print("Тест завершен!")
    print("=" * 50)
    print("\nДля проверки памяти GPU используйте команду:")
    print("  ollama ps")

if __name__ == "__main__":
    test_ollama()
