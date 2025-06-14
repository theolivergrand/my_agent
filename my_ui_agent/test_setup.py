#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работоспособности веб-приложения
"""

import os
import sys
import tempfile
from PIL import Image, ImageDraw

def create_test_image():
    """Создает тестовое изображение UI"""
    # Создаем изображение 800x600
    img = Image.new('RGB', (800, 600), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Рисуем некоторые UI элементы
    # Заголовок
    draw.rectangle([50, 50, 750, 100], fill=(70, 130, 180), outline=(0, 0, 0))
    draw.text((60, 65), "Game Title", fill=(255, 255, 255))
    
    # Кнопки
    draw.rectangle([100, 150, 200, 200], fill=(34, 139, 34), outline=(0, 0, 0))
    draw.text((110, 170), "START", fill=(255, 255, 255))
    
    draw.rectangle([250, 150, 350, 200], fill=(220, 20, 60), outline=(0, 0, 0))
    draw.text((260, 170), "EXIT", fill=(255, 255, 255))
    
    # Панель статистики
    draw.rectangle([500, 150, 700, 300], fill=(255, 255, 255), outline=(0, 0, 0))
    draw.text((510, 160), "Score: 1234", fill=(0, 0, 0))
    draw.text((510, 180), "Level: 5", fill=(0, 0, 0))
    draw.text((510, 200), "Lives: 3", fill=(0, 0, 0))
    
    # Полоса здоровья
    draw.rectangle([50, 500, 300, 530], fill=(255, 0, 0), outline=(0, 0, 0))
    draw.rectangle([50, 500, 200, 530], fill=(0, 255, 0))
    draw.text((60, 505), "Health: 80%", fill=(255, 255, 255))
    
    # Сохраняем в временный файл
    temp_path = os.path.join(tempfile.gettempdir(), "test_ui_screenshot.png")
    img.save(temp_path)
    print(f"✅ Тестовое изображение создано: {temp_path}")
    return temp_path

def test_agent_import():
    """Тестирует импорт основных компонентов"""
    try:
        from agent import UIAnalysisAgent, MOBILE_GAMING_UI_TAXONOMY
        print("✅ Успешный импорт UIAnalysisAgent")
        
        # Проверяем таксономию
        total_tags = sum(len(tags) for tags in MOBILE_GAMING_UI_TAXONOMY.values())
        print(f"✅ Таксономия загружена: {len(MOBILE_GAMING_UI_TAXONOMY)} категорий, {total_tags} тегов")
        
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта агента: {e}")
        return False

def test_web_app_import():
    """Тестирует импорт веб-приложения"""
    try:
        from web_app import app
        print("✅ Успешный импорт Flask приложения")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта веб-приложения: {e}")
        print("   Возможно, не установлены зависимости: pip install -r requirements.txt")
        return False

def test_directories():
    """Проверяет наличие необходимых директорий"""
    required_dirs = ['templates', 'static', 'uploads', 'training_dataset']
    all_exist = True
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Директория {dir_name} существует")
        else:
            print(f"❌ Директория {dir_name} не найдена")
            all_exist = False
    
    return all_exist

def test_templates():
    """Проверяет наличие шаблонов"""
    templates = ['index.html', 'annotate.html', 'dataset.html']
    all_exist = True
    
    for template in templates:
        template_path = os.path.join('templates', template)
        if os.path.exists(template_path):
            print(f"✅ Шаблон {template} найден")
        else:
            print(f"❌ Шаблон {template} не найден")
            all_exist = False
    
    return all_exist

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование UI Dataset Web App")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Тест 1: Проверка директорий
    print("\n📁 Тест 1: Проверка структуры директорий")
    if not test_directories():
        all_tests_passed = False
    
    # Тест 2: Проверка шаблонов
    print("\n📄 Тест 2: Проверка HTML шаблонов")
    if not test_templates():
        all_tests_passed = False
    
    # Тест 3: Импорт агента
    print("\n🤖 Тест 3: Импорт UI Analysis Agent")
    if not test_agent_import():
        all_tests_passed = False
    
    # Тест 4: Импорт веб-приложения
    print("\n🌐 Тест 4: Импорт Flask приложения")
    if not test_web_app_import():
        all_tests_passed = False
    
    # Тест 5: Создание тестового изображения
    print("\n🖼️  Тест 5: Создание тестового изображения")
    try:
        test_image_path = create_test_image()
        print(f"   Используйте это изображение для тестирования: {test_image_path}")
    except Exception as e:
        print(f"❌ Ошибка создания тестового изображения: {e}")
        all_tests_passed = False
    
    # Итоговый результат
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 Все тесты прошли успешно!")
        print("   Готов к запуску: python run_web_app.py")
    else:
        print("⚠️  Некоторые тесты не прошли")
        print("   Проверьте ошибки выше и устраните их")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
