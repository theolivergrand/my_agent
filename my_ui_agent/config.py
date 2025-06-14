# Конфигурация Flask приложения
import os
from pathlib import Path

class Config:
    """Базовая конфигурация"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Папки приложения
    BASE_DIR = Path(__file__).parent
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    DATASET_FOLDER = BASE_DIR / 'training_dataset'
    STATIC_FOLDER = BASE_DIR / 'static'
    TEMPLATE_FOLDER = BASE_DIR / 'templates'
    
    # Ограничения загрузки
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    
    # Google Cloud Vision API
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Настройки интерфейса
    ITEMS_PER_PAGE = 12
    ANNOTATION_TIMEOUT = 300  # 5 минут на аннотацию
    
    # Настройки датасета
    DATASET_VERSION = '1.0'
    TAXONOMY_VERSION = 'mobile_gaming_v1'

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key-required'

class TestingConfig(Config):
    """Конфигурация для тестирования"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

# Выбор конфигурации на основе переменной окружения
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Возвращает текущую конфигурацию"""
    return config[os.environ.get('FLASK_ENV', 'default')]
