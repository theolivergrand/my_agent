#!/usr/bin/env python3
"""
Демонстрационный скрипт для работы с гибридным AI Vision агентом
"""

import asyncio
import sys
from pathlib import Path

# Добавляем текущую директорию в path
sys.path.append(str(Path(__file__).parent))

async def demo_hybrid_vision():
    """Демонстрация работы гибридного AI Vision агента"""
    
    print("🎯 ДЕМОНСТРАЦИЯ ГИБРИДНОГО AI VISION АГЕНТА")
    print("=" * 50)
    
    try:
        # Импорт с обработкой ошибок
        from enhanced_agent import EnhancedUIAnalysisAgent
        
        # Создание агента
        print("🤖 Создание Enhanced UI Analysis Agent...")
        agent = EnhancedUIAnalysisAgent(
            anthropic_api_key=None,  # Будет получен из .env
            enable_hybrid=True
        )
        
        # Проверка возможностей
        capabilities = agent.get_analysis_capabilities()
        print("📊 Доступные возможности:")
        for service, available in capabilities.items():
            status = "✅ ДОСТУПЕН" if available else "❌ НЕДОСТУПЕН"
            print(f"  • {service}: {status}")
        
        # Поиск изображений для анализа
        print("\n🔍 Поиск изображений для анализа...")
        
        # Возможные пути к изображениям
        image_paths = []
        search_locations = [
            "uploads/*.png",
            "learning_data/*/*.png", 
            "*.png",
            "*.jpg"
        ]
        
        for pattern in search_locations:
            found = list(Path(".").glob(pattern))
            image_paths.extend(found)
        
        if not image_paths:
            print("⚠️ Изображения не найдены. Создание тестового изображения...")
            
            # Создание простого тестового изображения
            try:
                import matplotlib.pyplot as plt
                import matplotlib.patches as patches
                
                fig, ax = plt.subplots(1, 1, figsize=(8, 6))
                ax.set_xlim(0, 100)
                ax.set_ylim(0, 100)
                
                # Рисуем простой UI
                # Заголовок
                header = patches.Rectangle((10, 80), 80, 15, linewidth=2, 
                                         edgecolor='blue', facecolor='lightblue')
                ax.add_patch(header)
                ax.text(50, 87, 'UI Header', ha='center', va='center', fontsize=12, weight='bold')
                
                # Кнопки
                btn1 = patches.Rectangle((10, 50), 25, 15, linewidth=2, 
                                       edgecolor='green', facecolor='lightgreen')
                ax.add_patch(btn1)
                ax.text(22.5, 57, 'Button 1', ha='center', va='center', fontsize=10)
                
                btn2 = patches.Rectangle((40, 50), 25, 15, linewidth=2, 
                                       edgecolor='red', facecolor='lightcoral')
                ax.add_patch(btn2)
                ax.text(52.5, 57, 'Button 2', ha='center', va='center', fontsize=10)
                
                # Поле ввода
                input_field = patches.Rectangle((10, 20), 60, 15, linewidth=2, 
                                              edgecolor='gray', facecolor='white')
                ax.add_patch(input_field)
                ax.text(40, 27, 'Text Input Field', ha='center', va='center', fontsize=10)
                
                ax.set_title('Test UI Screenshot', fontsize=14, weight='bold')
                ax.set_xticks([])
                ax.set_yticks([])
                
                # Сохранение
                test_image_path = Path("demo_test_ui.png")
                plt.savefig(test_image_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                image_paths = [test_image_path]
                print(f"✅ Создано тестовое изображение: {test_image_path}")
                
            except ImportError:
                print("❌ Matplotlib не доступен для создания тестового изображения")
                print("💡 Поместите изображения в директорию 'uploads/' или текущую папку")
                return
        
        # Выбираем первое изображение для демонстрации
        demo_image = image_paths[0]
        print(f"🖼️ Используем для демонстрации: {demo_image}")
        
        # Анализ изображения
        print(f"\n🔄 Анализ изображения '{demo_image.name}'...")
        
        try:
            result = await agent.analyze_screenshot_enhanced(
                str(demo_image),
                analysis_method="auto"
            )
            
            print("✅ Анализ завершен!")
            print(f"📊 Confidence Score: {result.get('confidence_score', 0):.2f}")
            print(f"🛠️ Метод анализа: {result.get('analysis_method', 'unknown')}")
            
            # Вывод результатов по сервисам
            if 'google_vision' in result:
                gv = result['google_vision']
                stats = gv.get('statistics', {})
                print(f"🔍 Google Vision: {stats.get('objects_count', 0)} объектов, {stats.get('texts_count', 0)} текстов")
            
            if 'hybrid_vision' in result:
                hv = result['hybrid_vision']
                method = hv.get('method_used', 'unknown')
                confidence = hv.get('confidence_score', 0)
                print(f"🤖 Hybrid Vision: {method}, confidence {confidence:.2f}")
                
                # Показать результаты анализа
                if 'phi_analysis' in hv:
                    phi_result = hv['phi_analysis']
                    print(f"⚡ Phi Vision: {phi_result[:100]}...")
                
                if 'claude_analysis' in hv:
                    claude_result = hv['claude_analysis']
                    print(f"🧠 Claude Vision: {claude_result[:100]}...")
            
            # Объединенный анализ
            if 'combined_analysis' in result:
                combined = result['combined_analysis']
                print(f"\n📋 Объединенный анализ:")
                summary = combined.get('summary', {})
                for key, value in summary.items():
                    print(f"  • {key}: {value}")
                
                recommendations = combined.get('recommendations', [])
                if recommendations:
                    print(f"💡 Рекомендации:")
                    for rec in recommendations:
                        print(f"  • {rec}")
        
        except Exception as e:
            print(f"❌ Ошибка анализа: {str(e)}")
            print("💡 Возможные причины:")
            print("  • API ключи не настроены в .env файле")
            print("  • Сервисы недоступны")
            print("  • Проблемы с изображением")
        
        # Демонстрация массового анализа (если есть несколько изображений)
        if len(image_paths) > 1:
            print(f"\n📁 Демонстрация массового анализа ({len(image_paths)} изображений)...")
            
            try:
                batch_results = await agent.batch_analyze_screenshots(
                    str(Path(image_paths[0]).parent),
                    pattern="*.png",
                    max_files=3,
                    analysis_method="auto"
                )
                
                successful = len([r for r in batch_results if "error" not in r])
                print(f"✅ Массовый анализ: {successful}/{len(batch_results)} успешно")
                
            except Exception as e:
                print(f"❌ Ошибка массового анализа: {str(e)}")
        
        # Очистка ресурсов
        print(f"\n🧹 Очистка ресурсов...")
        agent.cleanup()
        
        print(f"\n🎉 Демонстрация завершена!")
        print(f"📁 Результаты сохранены в learning_data/enhanced/")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Запустите сначала: python setup_ai_vision.py")
    
    except Exception as e:
        print(f"💥 Критическая ошибка: {str(e)}")

def print_usage_info():
    """Информация об использовании"""
    print("\n" + "=" * 60)
    print("📖 ИНФОРМАЦИЯ ОБ ИСПОЛЬЗОВАНИИ")
    print("=" * 60)
    print("Этот скрипт демонстрирует работу гибридного AI Vision агента.")
    print("\nПеред использованием убедитесь, что:")
    print("1. ✅ Установлены зависимости: pip install -r requirements.txt")
    print("2. ✅ Настроен .env файл с API ключами")
    print("3. ✅ Есть изображения для анализа")
    print("\nДля настройки:")
    print("• python setup_ai_vision.py - автоматическая настройка")
    print("• python test_ai_vision_setup.py - тестирование системы")
    print("• python demo_hybrid_vision.py - эта демонстрация")
    print("=" * 60)

async def main():
    """Главная функция"""
    try:
        await demo_hybrid_vision()
    except KeyboardInterrupt:
        print("\n❌ Демонстрация прервана пользователем")
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {str(e)}")
    finally:
        print_usage_info()

if __name__ == "__main__":
    asyncio.run(main())
