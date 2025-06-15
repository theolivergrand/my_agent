import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавление путей для импорта модулей из подпапок
sys.path.append(str(Path(__file__).parent / "my_ui_agent"))

# Загрузка переменных окружения из my_ui_agent/.env
env_path = Path(__file__).parent / "my_ui_agent" / ".env"
load_dotenv(env_path)

def test_environment():
    print("🔍 Проверка конфигурации...")
    print(f"📁 Рабочая директория: {os.getcwd()}")
    print(f"📄 .env файл: {env_path}")
    
    # Проверка Google Cloud
    gcp_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    if gcp_creds and os.path.exists(gcp_creds):
        print("✅ Google Cloud credentials найдены")
    else:
        print(f"❌ Google Cloud credentials не найдены: {gcp_creds}")
    
    # Проверка Phi Vision
    if os.getenv('PHI_VISION_ENABLED', '').lower() == 'true':
        print("✅ Phi Vision включен")
        try:
            import transformers
            print(f"✅ Transformers версия: {transformers.__version__}")
        except ImportError:
            print("❌ Transformers не установлен")
    
    # Проверка устройства
    try:
        import torch
        device = torch.cuda.is_available()
        print(f"🖥️  CUDA доступна: {device}")
        print(f"🖥️  Устройство: {'cuda' if device else 'cpu'}")
    except ImportError:
        print("❌ PyTorch не установлен")

if __name__ == "__main__":
    test_environment()
