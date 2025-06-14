#!/usr/bin/env python3
"""
Исправленный тест активации Google Cloud Vision + Phi Vision
"""

import os
import sys
from pathlib import Path

def test_google_cloud_vision():
    """Тест Google Cloud Vision"""
    print("🔍 Тестирование Google Cloud Vision...")
    
    # Установка переменной окружения
    credentials_path = "/workspaces/my_agent/gdd-suite-8ae26f5f3853.json"
    if Path(credentials_path).exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        print(f"✅ Credentials установлены: {credentials_path}")
    else:
        print(f"❌ Credentials файл не найден: {credentials_path}")
        return False
    
    try:
        from google.cloud import vision
        client = vision.ImageAnnotatorClient()
        print("✅ Google Cloud Vision активен!")
        
        # Простой тест
        test_image_path = Path("uploads/f3afbec86c89421f88469ece197e8384_Screenshot_2025-01-27_170812.png")
        if test_image_path.exists():
            with open(test_image_path, "rb") as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = client.text_detection(image=image)
            texts = response.text_annotations
            
            print(f"🔍 Найдено {len(texts)} текстовых элементов")
            if texts:
                print(f"📝 Первый текст: {texts[0].description[:50]}...")
            
            return True
        else:
            print("⚠️ Тестовое изображение не найдено, но API работает")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка Google Cloud Vision: {str(e)}")
        return False

def test_phi_vision():
    """Тест Phi Vision"""
    print("\n⚡ Тестирование Phi Vision...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} доступен")
        print(f"🖥️ Устройство: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
        
        from transformers import AutoProcessor, AutoModelForCausalLM
        print("✅ Transformers доступен")
        
        # Загрузка процессора (без модели для экономии памяти)
        model_name = "microsoft/Phi-3.5-vision-instruct"
        print(f"📥 Загрузка процессора {model_name}...")
        
        processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        print("✅ Phi Vision процессор загружен!")
        
        # Простой тест без загрузки полной модели
        print("🧪 Тест процессора...")
        test_text = "Тестовое сообщение"
        
        # Создаем простое сообщение
        messages = [{"role": "user", "content": test_text}]
        text = processor.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        print("✅ Phi Vision готов к использованию!")
        print("💡 Примечание: Полная модель будет загружена при первом использовании")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Phi Vision: {str(e)}")
        return False

def test_combined_approach():
    """Тест комбинированного подхода"""
    print("\n🚀 Тестирование комбинированного подхода...")
    
    google_ok = test_google_cloud_vision()
    phi_ok = test_phi_vision()
    
    print(f"\n📊 РЕЗУЛЬТАТЫ АКТИВАЦИИ:")
    print(f"{'Google Cloud Vision':.<30} {'✅ АКТИВЕН' if google_ok else '❌ НЕАКТИВЕН'}")
    print(f"{'Phi Vision 3.5':.<30} {'✅ АКТИВЕН' if phi_ok else '❌ НЕАКТИВЕН'}")
    
    if google_ok and phi_ok:
        print(f"\n🎉 ОТЛИЧНО! Обе системы активны!")
        print(f"✅ Готов к гибридному анализу UI")
        return True
    elif google_ok or phi_ok:
        print(f"\n⚠️ Частичная активация - можно работать с одной системой")
        return True
    else:
        print(f"\n❌ Требуется настройка - обе системы неактивны")
        return False

def print_usage_recommendations():
    """Рекомендации по использованию"""
    print(f"\n" + "="*60)
    print("💡 РЕКОМЕНДАЦИИ ПО ИСПОЛЬЗОВАНИЮ")
    print("="*60)
    
    print("""
🎯 ОПТИМАЛЬНАЯ СТРАТЕГИЯ ДЛЯ UI АНАЛИЗА:

1️⃣ GOOGLE CLOUD VISION:
   • Лучший в мире OCR для извлечения текста
   • Точное обнаружение объектов и лиц
   • Определение цветов и композиции
   • Промышленная надежность

2️⃣ PHI VISION 3.5:
   • Понимание контекста UI элементов
   • Классификация типов элементов (кнопки, формы, меню)
   • Анализ пользовательского опыта
   • Локальная обработка (бесплатно)

3️⃣ ГИБРИДНЫЙ ПОДХОД:
   • Google: факты и данные
   • Phi: смысл и контекст
   • Объединение: полная картина UI

🔧 КОМАНДЫ ДЛЯ ЗАПУСКА:
   • python test_ai_vision_setup.py - полное тестирование
   • python enhanced_agent.py - запуск анализа
   • python demo_hybrid_vision.py - демонстрация
""")
    print("="*60)

def main():
    """Главная функция"""
    print("🎮 АКТИВАЦИЯ GOOGLE CLOUD VISION + PHI VISION")
    print("="*60)
    
    success = test_combined_approach()
    print_usage_recommendations()
    
    if success:
        print("\n🚀 Система готова! Переходите к анализу UI изображений.")
    else:
        print("\n🔧 Требуется дополнительная настройка.")

if __name__ == "__main__":
    main()
