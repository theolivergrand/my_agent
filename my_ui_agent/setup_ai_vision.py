#!/usr/bin/env python3
"""
Скрипт для решения проблем с активацией AI Vision сервисов
"""

import subprocess
import sys
import os
from pathlib import Path
import json

class AIVisionSetup:
    """Автоматическая настройка AI Vision сервисов"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
    
    def run_setup(self):
        """Запуск полной настройки"""
        print("🚀 Настройка AI Vision сервисов для проекта")
        print("=" * 50)
        
        # 1. Проверка Python окружения
        self.check_python_environment()
        
        # 2. Установка зависимостей
        self.install_dependencies()
        
        # 3. Настройка GPU (если доступно)
        self.setup_gpu_support()
        
        # 4. Создание конфигурационных файлов
        self.create_config_files()
        
        # 5. Тест всех сервисов
        self.test_services()
        
        # 6. Вывод результатов
        self.print_summary()
    
    def check_python_environment(self):
        """Проверка Python окружения"""
        print("🔍 Проверка Python окружения...")
        
        # Версия Python
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor >= 8:
            self.success.append(f"Python {python_version.major}.{python_version.minor} ✅")
        else:
            self.errors.append(f"Требуется Python 3.8+, найден {python_version.major}.{python_version.minor}")
        
        # Pip
        try:
            import pip
            self.success.append("pip доступен ✅")
        except ImportError:
            self.errors.append("pip не найден")
    
    def install_dependencies(self):
        """Установка зависимостей"""
        print("📦 Установка зависимостей...")
        
        # Базовые зависимости
        base_packages = [
            "torch",
            "transformers",
            "anthropic",
            "pillow",
            "numpy",
            "requests",
            "python-dotenv"
        ]
        
        # Google Cloud зависимости
        google_packages = [
            "google-cloud-vision",
            "google-auth-oauthlib"
        ]
        
        # Установка базовых пакетов
        self._install_packages(base_packages, "Базовые AI пакеты")
        
        # Установка Google Cloud пакетов
        self._install_packages(google_packages, "Google Cloud пакеты")
        
        # Специальная установка PyTorch для GPU (если доступно)
        self._install_pytorch()
    
    def _install_packages(self, packages, description):
        """Установка списка пакетов"""
        print(f"  📥 {description}...")
        
        for package in packages:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package, "--upgrade"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.success.append(f"{package} установлен ✅")
            except subprocess.CalledProcessError:
                self.warnings.append(f"Не удалось установить {package}")
    
    def _install_pytorch(self):
        """Специальная установка PyTorch"""
        print("  🔥 Установка PyTorch...")
        
        try:
            # Проверка наличия CUDA
            import torch
            if torch.cuda.is_available():
                print("    🎮 CUDA доступна, PyTorch уже установлен")
                self.success.append("PyTorch с CUDA ✅")
            else:
                print("    💻 Используется CPU версия PyTorch")
                self.success.append("PyTorch CPU ✅")
        except ImportError:
            # Установка PyTorch
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "torch", "torchvision", "torchaudio", "--index-url", 
                    "https://download.pytorch.org/whl/cpu"
                ])
                self.success.append("PyTorch установлен ✅")
            except subprocess.CalledProcessError:
                self.errors.append("Ошибка установки PyTorch")
    
    def setup_gpu_support(self):
        """Настройка GPU поддержки"""
        print("🎮 Проверка GPU поддержки...")
        
        try:
            import torch
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0)
                self.success.append(f"GPU: {gpu_name} ({gpu_count} устройств) ✅")
                
                # Проверка памяти GPU
                memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                if memory_gb >= 6:
                    self.success.append(f"GPU память: {memory_gb:.1f}GB (достаточно для Phi-3.5) ✅")
                else:
                    self.warnings.append(f"GPU память: {memory_gb:.1f}GB (может быть недостаточно)")
            else:
                self.warnings.append("GPU не доступно, будет использоваться CPU")
        except ImportError:
            self.warnings.append("PyTorch не установлен, GPU проверка пропущена")
    
    def create_config_files(self):
        """Создание конфигурационных файлов"""
        print("📝 Создание конфигурационных файлов...")
        
        # Создание .env файла
        env_path = Path(".env")
        if not env_path.exists():
            env_content = """# AI Vision Configuration
# Anthropic API Key - получите на: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google Cloud Credentials - путь к JSON файлу
# Получите на: https://console.cloud.google.com/
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/google-credentials.json

# Настройки модели
PHI_MODEL_NAME=microsoft/Phi-3.5-vision-instruct
CLAUDE_MODEL_NAME=claude-3-5-sonnet-20241022
MAX_TOKENS=1000
TEMPERATURE=0.7
BATCH_SIZE=5
"""
            with open(env_path, 'w') as f:
                f.write(env_content)
            self.success.append(".env файл создан ✅")
        else:
            self.warnings.append(".env файл уже существует")
        
        # Создание директорий для данных
        dirs_to_create = [
            "learning_data/enhanced",
            "learning_data/batch_analysis", 
            "analysis_results",
            "logs"
        ]
        
        for dir_path in dirs_to_create:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            self.success.append(f"Директория {dir_path} создана ✅")
    
    def test_services(self):
        """Тестирование всех сервисов"""
        print("🧪 Тестирование AI Vision сервисов...")
        
        # Тест Phi Vision
        self._test_phi_vision()
        
        # Тест Claude Vision
        self._test_claude_vision()
        
        # Тест Google Vision
        self._test_google_vision()
    
    def _test_phi_vision(self):
        """Тест Phi Vision"""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoProcessor
            
            # Проверка доступности модели (без загрузки)
            model_name = "microsoft/Phi-3.5-vision-instruct"
            processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
            self.success.append("Phi Vision: модель доступна ✅")
            
        except ImportError:
            self.warnings.append("Phi Vision: зависимости не установлены")
        except Exception as e:
            self.warnings.append(f"Phi Vision: ошибка - {str(e)[:50]}...")
    
    def _test_claude_vision(self):
        """Тест Claude Vision"""
        try:
            import anthropic
            
            # Проверка наличия API ключа
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key and api_key != 'your_anthropic_api_key_here':
                client = anthropic.Anthropic(api_key=api_key)
                self.success.append("Claude Vision: API ключ настроен ✅")
            else:
                self.warnings.append("Claude Vision: нужно настроить ANTHROPIC_API_KEY в .env")
                
        except ImportError:
            self.warnings.append("Claude Vision: библиотека anthropic не установлена")
        except Exception as e:
            self.warnings.append(f"Claude Vision: ошибка - {str(e)[:50]}...")
    
    def _test_google_vision(self):
        """Тест Google Vision"""
        try:
            from google.cloud import vision
            
            # Проверка наличия credentials
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_path and Path(credentials_path).exists():
                client = vision.ImageAnnotatorClient()
                self.success.append("Google Vision: credentials настроены ✅")
            else:
                self.warnings.append("Google Vision: нужно настроить GOOGLE_APPLICATION_CREDENTIALS")
                
        except ImportError:
            self.warnings.append("Google Vision: библиотека google-cloud-vision не установлена")
        except Exception as e:
            self.warnings.append(f"Google Vision: ошибка - {str(e)[:50]}...")
    
    def print_summary(self):
        """Вывод итогового отчета"""
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ НАСТРОЙКИ AI VISION")
        print("=" * 60)
        
        if self.success:
            print(f"\n✅ УСПЕШНО ({len(self.success)}):")
            for item in self.success:
                print(f"  • {item}")
        
        if self.warnings:
            print(f"\n⚠️ ПРЕДУПРЕЖДЕНИЯ ({len(self.warnings)}):")
            for item in self.warnings:
                print(f"  • {item}")
        
        if self.errors:
            print(f"\n❌ ОШИБКИ ({len(self.errors)}):")
            for item in self.errors:
                print(f"  • {item}")
        
        print("\n" + "=" * 60)
        
        # Рекомендации
        print("🎯 СЛЕДУЮЩИЕ ШАГИ:")
        
        if not self.errors:
            print("  1. Настройте API ключи в .env файле")
            print("  2. Запустите тест: python test_ai_vision_setup.py")
            print("  3. Используйте enhanced_agent.py для анализа")
        else:
            print("  1. Исправьте ошибки выше")
            print("  2. Повторите установку")
        
        print("=" * 60)

def main():
    """Главная функция"""
    try:
        setup = AIVisionSetup()
        setup.run_setup()
    except KeyboardInterrupt:
        print("\n❌ Установка прервана пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {str(e)}")

if __name__ == "__main__":
    main()
