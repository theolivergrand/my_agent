#!/usr/bin/env python3
"""
Скрипт для запуска Flask веб-приложения для создания датасета UI элементов
"""

import sys
import os
import subprocess

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

def main():
    """Основная функция запуска"""
    print("🚀 Запуск UI Dataset Web App")
    print("=" * 50)
    
    # Проверяем пакеты
    if not check_requirements():
        print("\n📦 Пытаемся установить пакеты...")
        if not install_requirements():
            print("❌ Не удалось установить пакеты. Установите их вручную:")
            print("   pip install -r requirements.txt")
            sys.exit(1)
    
    # Проверяем Google Cloud credentials
    if not check_google_credentials():
        print("\n⚠️  Предупреждение: Google Cloud credentials не настроены")
        print("   Анализ изображений может не работать")
        print("   Для настройки см. файл GITHUB_SETUP.md")
    
    # Создаем необходимые папки
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("training_dataset", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    print("\n🌐 Запускаем веб-сервер...")
    print("   Открывайте http://localhost:5000 в браузере")
    print("   Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Запускаем Flask приложение
    try:
        from web_app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка при запуске сервера: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
