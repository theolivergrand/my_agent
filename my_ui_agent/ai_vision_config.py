# Конфигурация AI Vision сервисов
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Загрузка переменных окружения
load_dotenv()

class AIVisionConfig:
    """Конфигурация для AI Vision сервисов"""
    
    def __init__(self):
        self.setup_logging()
        self.check_environment()
    
    def setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ai_vision.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_environment(self):
        """Проверка окружения и доступности сервисов"""
        self.logger.info("🔍 Проверка конфигурации AI Vision сервисов...")
        
        # Проверка Google Cloud Vision
        self.google_vision_available = self._check_google_vision()
        
        # Проверка Anthropic Claude
        self.claude_available = self._check_claude()
        
        # Проверка Phi Vision (PyTorch + Transformers)
        self.phi_available = self._check_phi()
        
        # Вывод статуса
        self._print_status()
    
    def _check_google_vision(self) -> bool:
        """Проверка Google Cloud Vision API"""
        try:
            # Проверка переменных окружения
            gcp_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if gcp_credentials and Path(gcp_credentials).exists():
                from google.cloud import vision
                client = vision.ImageAnnotatorClient()
                self.logger.info("✅ Google Cloud Vision: ДОСТУПЕН")
                return True
            else:
                self.logger.warning("⚠️ Google Cloud Vision: ОТСУТСТВУЮТ CREDENTIALS")
                return False
        except ImportError:
            self.logger.error("❌ Google Cloud Vision: БИБЛИОТЕКА НЕ УСТАНОВЛЕНА")
            return False
        except Exception as e:
            self.logger.error(f"❌ Google Cloud Vision: ОШИБКА - {str(e)}")
            return False
    
    def _check_claude(self) -> bool:
        """Проверка Anthropic Claude API"""
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                from anthropic import Anthropic
                client = Anthropic(api_key=api_key)
                self.logger.info("✅ Anthropic Claude: ДОСТУПЕН")
                return True
            else:
                self.logger.warning("⚠️ Anthropic Claude: ОТСУТСТВУЕТ API_KEY")
                return False
        except ImportError:
            self.logger.error("❌ Anthropic Claude: БИБЛИОТЕКА НЕ УСТАНОВЛЕНА")
            return False
        except Exception as e:
            self.logger.error(f"❌ Anthropic Claude: ОШИБКА - {str(e)}")
            return False
    
    def _check_phi(self) -> bool:
        """Проверка Phi Vision (PyTorch + Transformers)"""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoProcessor
            
            # Проверка доступности CUDA
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                self.logger.info("✅ Phi Vision: ДОСТУПЕН (CUDA)")
            else:
                self.logger.info("✅ Phi Vision: ДОСТУПЕН (CPU)")
            return True
        except ImportError as e:
            self.logger.error(f"❌ Phi Vision: БИБЛИОТЕКИ НЕ УСТАНОВЛЕНЫ - {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Phi Vision: ОШИБКА - {str(e)}")
            return False
    
    def _print_status(self):
        """Вывод статуса всех сервисов"""
        self.logger.info("\n" + "="*50)
        self.logger.info("📊 СТАТУС AI VISION СЕРВИСОВ")
        self.logger.info("="*50)
        self.logger.info(f"Google Cloud Vision: {'✅ ДОСТУПЕН' if self.google_vision_available else '❌ НЕДОСТУПЕН'}")
        self.logger.info(f"Anthropic Claude:    {'✅ ДОСТУПЕН' if self.claude_available else '❌ НЕДОСТУПЕН'}")
        self.logger.info(f"Phi Vision:          {'✅ ДОСТУПЕН' if self.phi_available else '❌ НЕДОСТУПЕН'}")
        self.logger.info("="*50)
        
        available_count = sum([self.google_vision_available, self.claude_available, self.phi_available])
        if available_count == 0:
            self.logger.error("🚨 НИ ОДИН СЕРВИС НЕ ДОСТУПЕН!")
        elif available_count == 1:
            self.logger.warning("⚠️ ДОСТУПЕН ТОЛЬКО ОДИН СЕРВИС")
        else:
            self.logger.info(f"🎉 ДОСТУПНО {available_count}/3 СЕРВИСОВ")
    
    def get_recommended_setup(self) -> dict:
        """Получить рекомендуемую настройку"""
        recommendations = {
            "strategy": "none",
            "primary_service": None,
            "fallback_service": None,
            "setup_instructions": []
        }
        
        if self.claude_available and self.phi_available:
            recommendations["strategy"] = "hybrid"
            recommendations["primary_service"] = "claude"
            recommendations["fallback_service"] = "phi"
            recommendations["setup_instructions"].append("Используйте гибридную стратегию для лучшего качества")
        
        elif self.claude_available:
            recommendations["strategy"] = "claude_only"
            recommendations["primary_service"] = "claude"
            recommendations["setup_instructions"].append("Используйте Claude для высококачественного анализа")
        
        elif self.phi_available:
            recommendations["strategy"] = "phi_only"
            recommendations["primary_service"] = "phi"
            recommendations["setup_instructions"].append("Используйте Phi для быстрого локального анализа")
        
        elif self.google_vision_available:
            recommendations["strategy"] = "google_only"
            recommendations["primary_service"] = "google"
            recommendations["setup_instructions"].append("Используйте Google Vision для базового анализа")
        
        else:
            recommendations["setup_instructions"] = [
                "Настройте хотя бы один AI Vision сервис:",
                "1. Для Claude: получите API ключ на console.anthropic.com",
                "2. Для Phi: установите PyTorch и Transformers",
                "3. Для Google: настройте Google Cloud credentials"
            ]
        
        return recommendations

# Настройки по умолчанию
DEFAULT_CONFIG = {
    "ANTHROPIC_API_KEY": None,  # Устанавливается через .env
    "GOOGLE_APPLICATION_CREDENTIALS": None,  # Устанавливается через .env
    "PHI_MODEL_NAME": "microsoft/Phi-3.5-vision-instruct",
    "CLAUDE_MODEL_NAME": "claude-3-5-sonnet-20241022",
    "MAX_TOKENS": 1000,
    "TEMPERATURE": 0.7,
    "BATCH_SIZE": 5,
    "RATE_LIMIT_DELAY": 1.0,
}

def create_env_template():
    """Создание шаблона .env файла"""
    env_template = """# AI Vision Configuration
# Получите API ключ на: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Путь к JSON файлу с credentials от Google Cloud
# Получите на: https://console.cloud.google.com/
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/google-credentials.json

# Опциональные настройки
PHI_MODEL_NAME=microsoft/Phi-3.5-vision-instruct
CLAUDE_MODEL_NAME=claude-3-5-sonnet-20241022
MAX_TOKENS=1000
TEMPERATURE=0.7
"""
    
    env_path = Path(".env")
    if not env_path.exists():
        with open(env_path, 'w') as f:
            f.write(env_template)
        print(f"✅ Создан шаблон .env файла: {env_path}")
        print("📝 Заполните его своими API ключами")
    else:
        print("⚠️ Файл .env уже существует")

if __name__ == "__main__":
    # Создание шаблона .env если нужно
    create_env_template()
    
    # Проверка конфигурации
    config = AIVisionConfig()
    recommendations = config.get_recommended_setup()
    
    print("\n" + "="*50)
    print("🎯 РЕКОМЕНДАЦИИ ПО НАСТРОЙКЕ")
    print("="*50)
    print(f"Стратегия: {recommendations['strategy']}")
    if recommendations['primary_service']:
        print(f"Основной сервис: {recommendations['primary_service']}")
    if recommendations['fallback_service']:
        print(f"Резервный сервис: {recommendations['fallback_service']}")
    
    print("\nИнструкции:")
    for instruction in recommendations['setup_instructions']:
        print(f"• {instruction}")
    print("="*50)
