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

# UI Analysis Settings
ANALYSIS_SETTINGS = {
    'min_element_area': 100,
    'max_element_area': 50000,
    'button_aspect_ratio_range': (0.3, 5.0),
    'input_field_aspect_ratio_min': 2.0,
    'icon_area_threshold': 10000,
    'default_text_confidence': 0.8
}

# Dataset settings
DATASET_SETTINGS = {
    'output_dir': 'training_dataset',
    'learning_data_dir': 'learning_data',
    'annotation_formats': ['yolo', 'coco', 'json'],
    'backup_original_images': True
}

# UI Keywords for classification
UI_KEYWORDS = {
    'action_buttons': ['start', 'play', 'begin', 'continue', 'resume', 'go', 'launch'],
    'menu_buttons': ['menu', 'options', 'settings', 'config', 'preferences'],
    'close_buttons': ['close', 'exit', 'quit', 'cancel', 'dismiss', 'back'],
    'navigation_buttons': ['next', 'previous', 'forward', 'back', 'return'],
    'shop_buttons': ['buy', 'purchase', 'shop', 'store', 'market'],
    'inventory_buttons': ['inventory', 'items', 'equipment', 'gear'],
    'health_indicators': ['health', 'hp', 'life', 'hearts'],
    'mana_indicators': ['mana', 'mp', 'magic', 'energy'],
    'experience_indicators': ['experience', 'exp', 'xp', 'level']
}
