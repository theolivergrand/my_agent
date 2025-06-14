#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы всех AI Vision сервисов
"""

import asyncio
import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Добавляем текущую директорию в path
sys.path.append(str(Path(__file__).parent))

# Импорт наших модулей
try:
    from ai_vision_config import AIVisionConfig
    from enhanced_agent import EnhancedUIAnalysisAgent
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что все файлы находятся в одной директории")
    sys.exit(1)

class AIVisionTester:
    """Тестер всех AI Vision сервисов"""
    
    def __init__(self):
        self.config = AIVisionConfig()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {}
        }
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("🧪 ЗАПУСК ТЕСТОВ AI VISION СЕРВИСОВ")
        print("=" * 50)
        
        # 1. Тест конфигурации
        await self.test_configuration()
        
        # 2. Тест создания агента
        await self.test_agent_creation()
        
        # 3. Тест с тестовым изображением
        await self.test_image_analysis()
        
        # 4. Тест массового анализа
        await self.test_batch_analysis()
        
        # 5. Сохранение результатов
        self.save_test_results()
        
        # 6. Итоговый отчет
        self.print_final_report()
    
    async def test_configuration(self):
        """Тест конфигурации"""
        print("🔧 Тест конфигурации...")
        
        test_result = {
            "test_name": "configuration",
            "status": "success",
            "details": {
                "google_vision": self.config.google_vision_available,
                "claude_vision": self.config.claude_available,
                "phi_vision": self.config.phi_available
            },
            "message": "Конфигурация проверена"
        }
        
        available_services = sum([
            self.config.google_vision_available,
            self.config.claude_available,
            self.config.phi_available
        ])
        
        if available_services == 0:
            test_result["status"] = "failed"
            test_result["message"] = "Ни один сервис не доступен"
        elif available_services == 1:
            test_result["status"] = "warning"
            test_result["message"] = "Доступен только один сервис"
        
        self.results["tests"].append(test_result)
        print(f"  {'✅' if test_result['status'] == 'success' else '⚠️' if test_result['status'] == 'warning' else '❌'} {test_result['message']}")
    
    async def test_agent_creation(self):
        """Тест создания агента"""
        print("🤖 Тест создания агента...")
        
        try:
            # Получаем API ключ для Claude
            anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_api_key == 'your_anthropic_api_key_here':
                anthropic_api_key = None
            
            # Создаем агента
            agent = EnhancedUIAnalysisAgent(
                anthropic_api_key=anthropic_api_key,
                enable_hybrid=True
            )
            
            # Проверяем возможности
            capabilities = agent.get_analysis_capabilities()
            
            test_result = {
                "test_name": "agent_creation",
                "status": "success",
                "details": capabilities,
                "message": f"Агент создан с {sum(capabilities.values())} активными сервисами"
            }
            
            # Сохраняем агент для дальнейших тестов
            self.agent = agent
            
        except Exception as e:
            test_result = {
                "test_name": "agent_creation",
                "status": "failed",
                "details": {"error": str(e)},
                "message": f"Ошибка создания агента: {str(e)}"
            }
            self.agent = None
        
        self.results["tests"].append(test_result)
        print(f"  {'✅' if test_result['status'] == 'success' else '❌'} {test_result['message']}")
    
    async def test_image_analysis(self):
        """Тест анализа изображения"""
        print("🖼️ Тест анализа изображения...")
        
        if not self.agent:
            test_result = {
                "test_name": "image_analysis",
                "status": "skipped",
                "details": {},
                "message": "Агент не создан, тест пропущен"
            }
        else:
            # Создаем тестовое изображение или используем существующее
            test_image_path = self.create_test_image()
            
            try:
                # Запускаем анализ
                analysis_result = await self.agent.analyze_screenshot_enhanced(
                    test_image_path, 
                    analysis_method="auto"
                )
                
                test_result = {
                    "test_name": "image_analysis",
                    "status": "success",
                    "details": {
                        "confidence_score": analysis_result.get("confidence_score", 0),
                        "methods_used": analysis_result.get("analysis_method", "unknown"),
                        "services_available": len(analysis_result.get("capabilities", {}))
                    },
                    "message": f"Анализ выполнен, confidence: {analysis_result.get('confidence_score', 0):.2f}"
                }
                
            except Exception as e:
                test_result = {
                    "test_name": "image_analysis",
                    "status": "failed",
                    "details": {"error": str(e)},
                    "message": f"Ошибка анализа: {str(e)}"
                }
        
        self.results["tests"].append(test_result)
        print(f"  {'✅' if test_result['status'] == 'success' else '❌' if test_result['status'] == 'failed' else '⏭️'} {test_result['message']}")
    
    def create_test_image(self):
        """Создание тестового изображения"""
        # Проверяем существующие изображения
        possible_paths = [
            "uploads/f3afbec86c89421f88469ece197e8384_Screenshot_2025-01-27_170812.png",
            "learning_data/entry_20250614-022417/Screenshot 2025-01-27 170812.png",
            "test_image.png"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        # Создаем простое тестовое изображение
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Создаем изображение 400x300
            img = Image.new('RGB', (400, 300), color='white')
            draw = ImageDraw.Draw(img)
            
            # Рисуем простой UI
            # Заголовок
            draw.rectangle([10, 10, 390, 50], fill='blue')
            draw.text((20, 20), "Test UI Header", fill='white')
            
            # Кнопки
            draw.rectangle([10, 70, 120, 110], fill='green')
            draw.text((30, 85), "Button 1", fill='white')
            
            draw.rectangle([140, 70, 250, 110], fill='red')
            draw.text((165, 85), "Button 2", fill='white')
            
            # Текстовое поле
            draw.rectangle([10, 130, 390, 170], fill='lightgray', outline='black')
            draw.text((20, 145), "Text Input Field", fill='black')
            
            # Меню
            draw.rectangle([10, 190, 390, 290], fill='lightblue', outline='navy')
            draw.text((20, 210), "Menu Item 1", fill='navy')
            draw.text((20, 230), "Menu Item 2", fill='navy')
            draw.text((20, 250), "Menu Item 3", fill='navy')
            
            # Сохраняем
            test_path = "test_ui_image.png"
            img.save(test_path)
            print(f"  📸 Создано тестовое изображение: {test_path}")
            return test_path
            
        except Exception as e:
            print(f"  ⚠️ Не удалось создать тестовое изображение: {e}")
            return None
    
    async def test_batch_analysis(self):
        """Тест массового анализа"""
        print("📁 Тест массового анализа...")
        
        if not self.agent:
            test_result = {
                "test_name": "batch_analysis",
                "status": "skipped",
                "details": {},
                "message": "Агент не создан, тест пропущен"
            }
        else:
            # Ищем директории с изображениями
            test_directories = ["uploads", "learning_data", "."]
            images_found = []
            
            for directory in test_directories:
                if Path(directory).exists():
                    for ext in ["*.png", "*.jpg", "*.jpeg"]:
                        images_found.extend(list(Path(directory).glob(ext)))
            
            if not images_found:
                test_result = {
                    "test_name": "batch_analysis",
                    "status": "skipped",
                    "details": {},
                    "message": "Изображения для тестирования не найдены"
                }
            else:
                try:
                    # Берем первые 2 изображения для быстрого теста
                    test_images = images_found[:2]
                    
                    batch_results = await self.agent.batch_analyze_screenshots(
                        str(test_images[0].parent),
                        pattern=test_images[0].name,
                        max_files=2,
                        analysis_method="auto"
                    )
                    
                    test_result = {
                        "test_name": "batch_analysis",
                        "status": "success",
                        "details": {
                            "images_processed": len(batch_results),
                            "successful_analyses": len([r for r in batch_results if "error" not in r])
                        },
                        "message": f"Обработано {len(batch_results)} изображений"
                    }
                    
                except Exception as e:
                    test_result = {
                        "test_name": "batch_analysis",
                        "status": "failed",
                        "details": {"error": str(e)},
                        "message": f"Ошибка массового анализа: {str(e)}"
                    }
        
        self.results["tests"].append(test_result)
        print(f"  {'✅' if test_result['status'] == 'success' else '❌' if test_result['status'] == 'failed' else '⏭️'} {test_result['message']}")
    
    def save_test_results(self):
        """Сохранение результатов тестирования"""
        # Подсчет статистики
        total_tests = len(self.results["tests"])
        successful = len([t for t in self.results["tests"] if t["status"] == "success"])
        failed = len([t for t in self.results["tests"] if t["status"] == "failed"])
        skipped = len([t for t in self.results["tests"] if t["status"] == "skipped"])
        warnings = len([t for t in self.results["tests"] if t["status"] == "warning"])
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "warnings": warnings,
            "success_rate": successful / total_tests if total_tests > 0 else 0
        }
        
        # Сохранение в файл
        results_dir = Path("test_results")
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"ai_vision_test_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Результаты тестирования сохранены: {results_file}")
    
    def print_final_report(self):
        """Итоговый отчет"""
        summary = self.results["summary"]
        
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ AI VISION")
        print("=" * 60)
        
        print(f"Всего тестов: {summary['total_tests']}")
        print(f"✅ Успешно: {summary['successful']}")
        print(f"❌ Неудачно: {summary['failed']}")
        print(f"⏭️ Пропущено: {summary['skipped']}")
        print(f"⚠️ Предупреждения: {summary['warnings']}")
        print(f"📈 Успешность: {summary['success_rate']:.1%}")
        
        print("\n🎯 РЕКОМЕНДАЦИИ:")
        
        if summary['success_rate'] >= 0.75:
            print("  ✅ Система готова к использованию!")
            print("  • Запустите enhanced_agent.py для анализа UI")
            print("  • Используйте web_app.py для веб-интерфейса")
        elif summary['success_rate'] >= 0.5:
            print("  ⚠️ Частичная готовность системы")
            print("  • Настройте дополнительные API ключи")
            print("  • Проверьте failed тесты выше")
        else:
            print("  ❌ Система требует настройки")
            print("  • Запустите setup_ai_vision.py")
            print("  • Настройте .env файл с API ключами")
        
        print("=" * 60)

async def main():
    """Главная функция"""
    try:
        tester = AIVisionTester()
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n❌ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка тестирования: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
