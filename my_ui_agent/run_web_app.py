#!/usr/bin/env python3
"""
Скрипт для запуска Flask веб-приложения для создания датасета UI элементов
"""

import sys
import os
import subprocess
import logging
from pathlib import Path

def check_requirements():
    """Проверяет наличие необходимых пакетов"""
    try:
        import flask
        import google.cloud.vision
        import PIL
        import numpy
        import werkzeug
        print("✅ Все необходимые пакеты установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует пакет: {e}")
        return False

def install_requirements():
    """Устанавливает необходимые пакеты"""
    print("🔄 Устанавливаем необходимые пакеты...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Пакеты успешно установлены")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка при установке пакетов")
        return False

def check_google_credentials():
    """Проверяет наличие Google Cloud credentials"""
    if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
        creds_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
        if os.path.exists(creds_path):
            print(f"✅ Google Cloud credentials найдены: {creds_path}")
            return True
        else:
            print(f"❌ Файл credentials не найден: {creds_path}")
    else:
        print("⚠️  Переменная GOOGLE_APPLICATION_CREDENTIALS не установлена")
        print("   Установите её, указав путь к JSON файлу с ключами Google Cloud")
    return False

def check_environment():
    """Проверяет, правильно ли настроена среда"""
    issues = []
    
    # Проверка версии Python
    if sys.version_info < (3, 8):
        issues.append("Требуется Python 3.8+")
    
    # Проверка необходимых директорий
    required_dirs = ['uploads', 'training_dataset', 'learning_data', 'templates']
    for dir_name in required_dirs:
        dir_path = Path(__file__).parent / dir_name
        if not dir_path.exists():
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"✅ Создана директория: {dir_name}")
            except Exception as e:
                issues.append(f"Не удается создать директорию {dir_name}: {e}")
    
    # Проверка учетных данных Google Cloud (необязательно)
    if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        print("⚠️  Учетные данные Google Cloud не найдены - Vision API будет отключен")
        print("   Установите переменную окружения GOOGLE_APPLICATION_CREDENTIALS для включения")
    else:
        print("✅ Учетные данные Google Cloud найдены")
    
    # Проверка необходимых пакетов
    required_packages = [
        ('flask', 'Flask'),
        ('PIL', 'Pillow'),
    ]
    
    for package, pip_name in required_packages:
        try:
            __import__(package)
            print(f"✅ {pip_name} установлен")
        except ImportError:
            issues.append(f"Отсутствует пакет: {pip_name}")
    
    return issues

def main():
    """Основная функция запуска"""
    print("🚀 Запуск UI Dataset Web App")
    print("=" * 50)
    
    # Проверяем окружение
    issues = check_environment()
    
    if issues:
        print("\n❌ Обнаружены проблемы в окружении:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nПожалуйста, исправьте эти проблемы перед запуском приложения.")
        return False
    
    print("\n✅ Проверка окружения пройдена!")
    print("\n🌐 Запуск Flask приложения...")
    print("   URL: http://localhost:5000")
    print("   Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    try:
        from .web_app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Не удалось импортировать веб-приложение: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено пользователем")
    except Exception as e:
        print(f"❌ Ошибка приложения: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
