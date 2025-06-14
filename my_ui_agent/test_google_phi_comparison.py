#!/usr/bin/env python3
"""
Тест сравнения Google Cloud Vision + Phi Vision для UI анализа
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime

# Добавляем текущую директорию в path
sys.path.append(str(Path(__file__).parent))

try:
    from enhanced_agent import EnhancedUIAnalysisAgent
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что все файлы находятся в одной директории")
    sys.exit(1)

class GooglePhiComparison:
    """Сравнение Google Cloud Vision + Phi Vision"""
    
    def __init__(self):
        self.agent = None
    
    async def run_comparison_test(self):
        """Запуск теста сравнения"""
        print("🔍 ТЕСТ: Google Cloud Vision + Phi Vision для UI анализа")
        print("=" * 60)
        
        # 1. Инициализация агента
        await self._init_agent()
        
        # 2. Создание тестового UI изображения
        test_image = self._create_test_ui_image()
        
        # 3. Анализ через разные методы
        await self._compare_analysis_methods(test_image)
        
        # 4. Анализ существующих изображений
        await self._analyze_existing_images()
        
        # 5. Итоговые рекомендации
        self._print_recommendations()
    
    async def _init_agent(self):
        """Инициализация агента"""
        print("🤖 Инициализация Enhanced UI Analysis Agent...")
        
        try:
            self.agent = EnhancedUIAnalysisAgent(
                anthropic_api_key=None,  # Claude отключен
                enable_hybrid=True
            )
            
            capabilities = self.agent.get_analysis_capabilities()
            print("📊 Доступные возможности:")
            for service, available in capabilities.items():
                status = "✅ АКТИВЕН" if available else "❌ НЕАКТИВЕН"
                print(f"  • {service}: {status}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации: {str(e)}")
            return False
    
    def _create_test_ui_image(self):
        """Создание тестового UI изображения"""
        print("\n🖼️ Создание тестового UI изображения...")
        
        try:
            # Проверяем существующие изображения
            existing_images = []
            for pattern in ["*.png", "*.jpg", "uploads/*.png", "learning_data/*/*.png"]:
                existing_images.extend(Path(".").glob(pattern))
            
            if existing_images:
                test_image = existing_images[0]
                print(f"✅ Используем существующее изображение: {test_image}")
                return test_image
            
            # Создаем простое тестовое изображение с PIL
            from PIL import Image, ImageDraw, ImageFont
            
            # Создаем изображение 800x600
            img = Image.new('RGB', (800, 600), color='#f0f0f0')
            draw = ImageDraw.Draw(img)
            
            # Заголовок приложения
            draw.rectangle([0, 0, 800, 80], fill='#2196F3')
            draw.text((50, 30), "Mobile App UI Test", fill='white')
            
            # Навигационные кнопки
            draw.rectangle([50, 120, 200, 170], fill='#4CAF50')
            draw.text((80, 140), "Home", fill='white')
            
            draw.rectangle([220, 120, 370, 170], fill='#FF9800')
            draw.text((250, 140), "Profile", fill='white')
            
            draw.rectangle([390, 120, 540, 170], fill='#9C27B0')
            draw.text((420, 140), "Settings", fill='white')
            
            # Поля ввода
            draw.rectangle([50, 220, 550, 270], fill='white', outline='gray', width=2)
            draw.text((60, 240), "Enter username...", fill='gray')
            
            draw.rectangle([50, 290, 550, 340], fill='white', outline='gray', width=2)
            draw.text((60, 310), "Enter password...", fill='gray')
            
            # Чекбоксы
            draw.rectangle([50, 370, 70, 390], fill='white', outline='gray', width=2)
            draw.text((80, 375), "Remember me", fill='black')
            
            draw.rectangle([50, 400, 70, 420], fill='white', outline='gray', width=2)
            draw.text((80, 405), "Terms and conditions", fill='black')
            
            # Кнопка действия
            draw.rectangle([50, 450, 250, 500], fill='#F44336')
            draw.text((120, 470), "LOGIN", fill='white')
            
            # Иконки
            draw.ellipse([600, 200, 650, 250], fill='#03A9F4')
            draw.text((615, 220), "📧", fill='white')
            
            draw.ellipse([600, 270, 650, 320], fill='#8BC34A')
            draw.text((615, 290), "📞", fill='white')
            
            draw.ellipse([600, 340, 650, 390], fill='#E91E63')
            draw.text((615, 360), "⚙️", fill='white')
            
            # Список элементов
            for i, item in enumerate(["News Feed", "Messages", "Notifications", "Gallery"]):
                y = 450 + i * 30
                draw.rectangle([300, y, 550, y + 25], fill='lightblue', outline='blue')
                draw.text((310, y + 5), item, fill='black')
            
            # Сохранение
            test_image_path = Path("google_phi_test_ui.png")
            img.save(test_image_path, dpi=(150, 150))
            print(f"✅ Создано тестовое изображение: {test_image_path}")
            return test_image_path
            
        except Exception as e:
            print(f"⚠️ Не удалось создать тестовое изображение: {e}")
            return None
    
    async def _compare_analysis_methods(self, test_image):
        """Сравнение методов анализа"""
        if not test_image or not self.agent:
            print("⚠️ Тест пропущен - нет изображения или агента")
            return
        
        print(f"\n🔄 Анализ изображения: {test_image.name}")
        print("-" * 50)
        
        methods = [
            ("google_only", "🔍 Только Google Cloud Vision"),
            ("phi", "⚡ Только Phi Vision 3.5"),
            ("hybrid", "🚀 Гибридный анализ (Google + Phi)")
        ]
        
        results = {}
        
        for method_id, method_name in methods:
            print(f"\n{method_name}...")
            
            try:
                start_time = datetime.now()
                
                result = await self.agent.analyze_screenshot_enhanced(
                    str(test_image),
                    analysis_method=method_id
                )
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Сохраняем результаты
                results[method_id] = {
                    "duration": duration,
                    "confidence": result.get("confidence_score", 0),
                    "result": result
                }
                
                print(f"  ✅ Завершено за {duration:.2f}с, confidence: {result.get('confidence_score', 0):.2f}")
                
                # Краткое описание результатов
                if method_id == "google_only" and "google_vision" in result:
                    gv = result["google_vision"]
                    stats = gv.get("statistics", {})
                    print(f"  📊 Google: {stats.get('objects_count', 0)} объектов, {stats.get('texts_count', 0)} текстов")
                
                elif method_id == "phi" and "hybrid_vision" in result:
                    hv = result["hybrid_vision"]
                    if "phi_analysis" in hv:
                        phi_text = hv["phi_analysis"][:100]
                        print(f"  🔍 Phi: {phi_text}...")
                
                elif method_id == "hybrid":
                    combined = result.get("combined_analysis", {})
                    summary = combined.get("summary", {})
                    print(f"  🎯 Гибридный: {len(summary)} параметров анализа")
                
            except Exception as e:
                print(f"  ❌ Ошибка: {str(e)}")
                results[method_id] = {"error": str(e)}
        
        # Сравнение результатов
        self._compare_results(results)
    
    def _compare_results(self, results):
        """Сравнение результатов разных методов"""
        print(f"\n📊 СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
        print("-" * 50)
        
        print("Метод\t\t\tВремя\tТочность\tСтатус")
        for method_id, data in results.items():
            if "error" in data:
                print(f"{method_id:15}\t-\t-\t\t❌ Ошибка")
            else:
                duration = data.get("duration", 0)
                confidence = data.get("confidence", 0)
                print(f"{method_id:15}\t{duration:.2f}с\t{confidence:.2f}\t\t✅ OK")
        
        # Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ ПО ИСПОЛЬЗОВАНИЮ:")
        
        if "google_only" in results and "error" not in results["google_only"]:
            print("  • Google Cloud Vision: Идеален для извлечения текста и базовых объектов")
        
        if "phi" in results and "error" not in results["phi"]:
            print("  • Phi Vision 3.5: Лучше понимает UI контекст и назначение элементов")
        
        if "hybrid" in results and "error" not in results["hybrid"]:
            print("  • Гибридный подход: Максимальная точность, объединяет преимущества обеих моделей")
    
    async def _analyze_existing_images(self):
        """Анализ существующих изображений в проекте"""
        print(f"\n📁 АНАЛИЗ СУЩЕСТВУЮЩИХ ИЗОБРАЖЕНИЙ")
        print("-" * 50)
        
        # Поиск изображений в проекте
        image_locations = [
            "uploads/*.png",
            "learning_data/*/*.png",
            "*.png",
            "*.jpg"
        ]
        
        found_images = []
        for pattern in image_locations:
            found_images.extend(Path(".").glob(pattern))
        
        if not found_images:
            print("⚠️ Дополнительные изображения не найдены")
            return
        
        # Анализируем первые 2 изображения
        for i, image_path in enumerate(found_images[:2]):
            print(f"\n🖼️ Анализ: {image_path.name}")
            
            try:
                result = await self.agent.analyze_screenshot_enhanced(
                    str(image_path),
                    analysis_method="hybrid"
                )
                
                confidence = result.get("confidence_score", 0)
                print(f"  ✅ Уверенность: {confidence:.2f}")
                
                # Показать ключевые результаты
                if "google_vision" in result:
                    gv_stats = result["google_vision"].get("statistics", {})
                    print(f"  📊 Google: {gv_stats.get('texts_count', 0)} текстов")
                
                if "hybrid_vision" in result and "phi_analysis" in result["hybrid_vision"]:
                    phi_preview = result["hybrid_vision"]["phi_analysis"][:80]
                    print(f"  🔍 Phi: {phi_preview}...")
                
            except Exception as e:
                print(f"  ❌ Ошибка: {str(e)}")
    
    def _print_recommendations(self):
        """Итоговые рекомендации"""
        print(f"\n" + "=" * 60)
        print("🎯 ИТОГОВЫЕ РЕКОМЕНДАЦИИ ДЛЯ ВАШЕГО ПРОЕКТА")
        print("=" * 60)
        
        print("""
🔥 ОПТИМАЛЬНАЯ СТРАТЕГИЯ: Google Cloud Vision + Phi Vision 3.5

📋 РАЗДЕЛЕНИЕ ЗАДАЧ:
  • Google Cloud Vision:
    ✅ Извлечение всего текста с UI (OCR)
    ✅ Обнаружение базовых объектов и форм
    ✅ Определение цветов и композиции
    ✅ Высокая точность и стабильность

  • Phi Vision 3.5:
    ✅ Понимание типов UI элементов (кнопки, меню, формы)
    ✅ Анализ пользовательского опыта (UX)
    ✅ Контекстное понимание назначения элементов
    ✅ Классификация gaming/mobile UI паттернов

🚀 ГИБРИДНЫЙ ПОДХОД:
  1. Google извлекает факты (текст, объекты, позиции)
  2. Phi анализирует смысл и контекст UI
  3. Система объединяет результаты в полную картину
  4. Создается максимально информативный датасет

💰 ЭКОНОМИЧЕСКАЯ ЭФФЕКТИВНОСТЬ:
  • Google Cloud Vision: ~$1.50 за 1000 изображений
  • Phi Vision 3.5: Бесплатно (локальная обработка)
  • Отличное соотношение цены и качества!

🎯 ДЛЯ ВАШЕГО UI ДАТАСЕТА:
  • Используйте гибридный режим для обучающих данных
  • Google для массового извлечения текста  
  • Phi для понимания UI паттернов
  • Комбинируйте результаты для ground truth""")
        
        print("=" * 60)

async def main():
    """Главная функция"""
    try:
        tester = GooglePhiComparison()
        await tester.run_comparison_test()
    except KeyboardInterrupt:
        print("\n❌ Тест прерван пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
