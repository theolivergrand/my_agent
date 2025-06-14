import os
from google.cloud import vision
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from collections import Counter
import colorsys
from github_researcher import GitHubUIResearcher

# --- Конфигурация (можно вынести в отдельный файл или переменные окружения) ---
# Если переменная окружения GOOGLE_APPLICATION_CREDENTIALS не установлена глобально,
# можно указать путь к ключу здесь (менее предпочтительно):
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\путь\\к\\вашему\\скачанному-ключу.json"

# --- Функции агента ---

def get_image_from_user():
    """Запрашивает у пользователя путь к изображению."""
    while True:
        image_path = input("Введите полный путь к файлу изображения: ").strip()
        if os.path.exists(image_path):
            try:
                # Попытка открыть изображение для проверки, что это действительно изображение
                Image.open(image_path)
                return image_path
            except Exception as e:
                print(f"Не удалось открыть файл как изображение: {e}. Попробуйте другой файл.")
        else:
            print(f"Файл не найден по пути: {image_path}. Пожалуйста, проверьте путь и попробуйте снова.")

def analyze_image_with_vision_ai(image_path):
    """Отправляет изображение в Google Cloud Vision API и получает результаты."""
    try:
        client = vision.ImageAnnotatorClient()
        print("Отправка изображения в Google Cloud Vision API...")

        with open(image_path, "rb") as image_file:
            content = image_file.read()
        gcp_image = vision.Image(content=content)

        features = [
            {"type_": vision.Feature.Type.OBJECT_LOCALIZATION},
            {"type_": vision.Feature.Type.TEXT_DETECTION},
            # Можно добавить другие функции, например, LABEL_DETECTION
        ]
        
        response = client.annotate_image({"image": gcp_image, "features": features})
        # response = client.batch_annotate_images(requests=[{"image": gcp_image, "features": features}]) # для одного изображения annotate_image проще

        if response.error.message:
            raise Exception(
                f"Ошибка Vision API: {response.error.message}\n"
                "Убедитесь, что API включен и аутентификация настроена правильно."
            )

        localized_objects = response.localized_object_annotations
        text_annotations = response.text_annotations # Первый элемент - весь текст, остальные - блоки/слова

        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ АНАЛИЗА GOOGLE VISION API")
        print("="*50)
        
        # Анализ объектов
        print(f"📦 ОБЪЕКТЫ: {len(localized_objects)}")
        if localized_objects:
            for i, obj in enumerate(localized_objects, 1):
                print(f"   {i}. {obj.name} (уверенность: {obj.score:.1%})")
        else:
            print("   Объекты не найдены")
        
        # Анализ текста
        text_blocks = len(text_annotations) - 1 if text_annotations else 0
        print(f"\n📝 ТЕКСТ: {text_blocks} блоков")
        if text_annotations and len(text_annotations) > 1:
            # Показываем первые 5 текстовых блоков для примера
            print("   Найденный текст (первые 5 блоков):")
            for i, text in enumerate(text_annotations[1:6], 1):
                preview = text.description.replace('\n', ' ').strip()[:30]
                if len(text.description) > 30:
                    preview += "..."
                print(f"   {i}. \"{preview}\"")
            if text_blocks > 5:
                print(f"   ... и еще {text_blocks - 5} блоков")
        else:
            print("   Текст не найден")
        
        print("="*50)
            
        return localized_objects, text_annotations

    except Exception as e:
        print(f"Произошла ошибка при взаимодействии с Google Cloud Vision API: {e}")
        return None, None

def draw_annotations(image_path, objects, texts, output_path="annotated_output.png", ui_analysis=None):
    """Создает качественное аннотированное изображение с улучшенной читаемостью."""
    try:
        # Открываем изображение
        pil_image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(pil_image)
        img_width, img_height = pil_image.size
        
        # Настройка шрифтов разных размеров
        try:
            title_font = ImageFont.truetype("arial.ttf", max(20, img_width // 50))
            label_font = ImageFont.truetype("arial.ttf", max(14, img_width // 80))
            small_font = ImageFont.truetype("arial.ttf", max(12, img_width // 100))
        except IOError:
            title_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Создаем легенду в верхней части изображения
        legend_height = 100
        legend_img = Image.new('RGB', (img_width, legend_height), color='white')
        legend_draw = ImageDraw.Draw(legend_img)
        
        # Рисуем заголовок легенды
        legend_draw.text((10, 10), "НАЙДЕННЫЕ ЭЛЕМЕНТЫ UI:", fill='black', font=title_font)
          # Добавляем цветовые индикаторы
        legend_y = 40
        if objects:
            legend_draw.rectangle([10, legend_y, 30, legend_y + 15], fill='blue', outline='black')
            legend_draw.text((35, legend_y), f"Объекты ({len(objects)})", fill='black', font=label_font)
        
        if texts and len(texts) > 1:
            text_count = len(texts) - 1
            legend_draw.rectangle([200, legend_y, 220, legend_y + 15], fill='red', outline='black')
            legend_draw.text((225, legend_y), f"Текст ({text_count} блоков)", fill='black', font=label_font)
        
        # Добавляем UI элементы в легенду
        if ui_analysis and ui_analysis.get("ui_elements"):
            ui_count = len(ui_analysis["ui_elements"])
            legend_draw.rectangle([400, legend_y, 420, legend_y + 15], fill='green', outline='black')
            legend_draw.text((425, legend_y), f"UI элементы ({ui_count})", fill='black', font=label_font)
        
        # Объединяем легенду с основным изображением
        final_img = Image.new('RGB', (img_width, img_height + legend_height))
        final_img.paste(legend_img, (0, 0))
        final_img.paste(pil_image, (0, legend_height))
        
        # Рисуем на объединенном изображении (смещаем координаты на высоту легенды)
        final_draw = ImageDraw.Draw(final_img)

        # Рисуем рамки для объектов с улучшенным стилем
        for i, obj in enumerate(objects):
            # Денормализуем координаты
            vertices = obj.bounding_poly.normalized_vertices
            box = [
                vertices[0].x * img_width, 
                vertices[0].y * img_height + legend_height,  # Смещение на легенду
                vertices[2].x * img_width, 
                vertices[2].y * img_height + legend_height
            ]
            
            # Рисуем полупрозрачную рамку
            box_color = 'blue'
            final_draw.rectangle(box, outline=box_color, width=4)
            
            # Рисуем фон для подписи
            label = f"#{i+1}: {obj.name}"
            confidence = f"{obj.score:.0%}"
            
            # Позиция подписи
            label_x = box[0] + 5
            label_y = box[1] - 35 if box[1] > legend_height + 35 else box[3] + 5
            
            # Рисуем подложку для текста
            text_bbox = final_draw.textbbox((label_x, label_y), label, font=label_font)
            final_draw.rectangle([text_bbox[0]-3, text_bbox[1]-2, text_bbox[2]+3, text_bbox[3]+2], 
                                fill='white', outline=box_color, width=2)
            
            # Рисуем текст подписи
            final_draw.text((label_x, label_y), label, fill=box_color, font=label_font)
            final_draw.text((label_x, label_y + 20), confidence, fill=box_color, font=small_font)

        # Рисуем рамки для текста с улучшенным стилем
        if texts and len(texts) > 1:
            for i, text_block in enumerate(texts[1:]):
                vertices = text_block.bounding_poly.vertices
                x_coords = [v.x for v in vertices]
                y_coords = [v.y + legend_height for v in vertices]  # Смещение на легенду
                box = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
                
                # Рисуем рамку для текста
                box_color = 'red'
                final_draw.rectangle(box, outline=box_color, width=3)
                
                # Готовим подпись
                text_content = text_block.description.replace('\n', ' ').strip()
                if len(text_content) > 20:
                    text_content = text_content[:17] + "..."
                
                label = f"T{i+1}: {text_content}"
                
                # Позиция подписи
                label_x = box[0] + 3
                label_y = box[1] - 25 if box[1] > legend_height + 25 else box[3] + 3
                
                # Рисуем подложку для текста
                text_bbox = final_draw.textbbox((label_x, label_y), label, font=small_font)
                final_draw.rectangle([text_bbox[0]-2, text_bbox[1]-1, text_bbox[2]+2, text_bbox[3]+1], 
                                    fill='white', outline=box_color, width=1)
                  # Рисуем текст подписи
                final_draw.text((label_x, label_y), label, fill=box_color, font=small_font)
        
        # Рисуем UI элементы (если есть)
        if ui_analysis and ui_analysis.get("ui_elements"):
            ui_elements = ui_analysis["ui_elements"]
            for i, element in enumerate(ui_elements):
                bounds = element.get("bounds", [0, 0, 0, 0])
                
                # Смещаем координаты на высоту легенды
                ui_box = [
                    bounds[0], 
                    bounds[1] + legend_height,
                    bounds[2], 
                    bounds[3] + legend_height
                ]
                
                # Рисуем рамку UI элемента (зеленый цвет)
                ui_color = 'green'
                final_draw.rectangle(ui_box, outline=ui_color, width=2)
                
                # Подпись для UI элемента
                ui_label = f"UI{i+1}: {element.get('type', 'unknown')}"
                ui_label_x = ui_box[0] + 3
                ui_label_y = ui_box[1] - 20 if ui_box[1] > legend_height + 20 else ui_box[3] + 3
                
                # Подложка для текста UI элемента
                ui_text_bbox = final_draw.textbbox((ui_label_x, ui_label_y), ui_label, font=small_font)
                final_draw.rectangle([ui_text_bbox[0]-2, ui_text_bbox[1]-1, ui_text_bbox[2]+2, ui_text_bbox[3]+1], 
                                    fill='lightgreen', outline=ui_color, width=1)
                
                # Текст подписи UI элемента
                final_draw.text((ui_label_x, ui_label_y), ui_label, fill=ui_color, font=small_font)
          # Добавляем статистику в правый верхний угол
        ui_count = len(ui_analysis["ui_elements"]) if ui_analysis and ui_analysis.get("ui_elements") else 0
        stats_text = [
            f"Размер: {img_width}x{img_height}",
            f"Объектов: {len(objects)}",
            f"Текста: {len(texts)-1 if texts and len(texts) > 1 else 0}",
            f"UI элементов: {ui_count}"
        ]
        
        stats_x = img_width - 200
        for i, stat in enumerate(stats_text):
            final_draw.text((stats_x, 60 + i*20), stat, fill='gray', font=small_font)
        
        # Сохраняем улучшенное изображение
        final_img.save(output_path, quality=95)
        print(f"Улучшенное аннотированное изображение сохранено: {output_path}")
        
        # Показываем изображение
        final_img.show()
        return output_path
        
    except Exception as e:
        print(f"Ошибка при создании аннотированного изображения: {e}")
        return None

def get_user_feedback(annotated_image_path, objects, texts):
    """Запрашивает у пользователя обратную связь."""
    print("\n" + "="*50)
    print("ОЦЕНКА РЕЗУЛЬТАТОВ АНАЛИЗА")
    print("="*50)
    print(f"📷 Аннотированное изображение: {annotated_image_path}")
    print("\nПожалуйста, откройте изображение и оцените качество анализа.")
    
    # Показываем сводку найденных элементов
    print(f"🔍 Найдено элементов:")
    print(f"   • Объектов: {len(objects) if objects else 0}")
    print(f"   • Текстовых блоков: {len(texts)-1 if texts and len(texts) > 1 else 0}")
    print("-"*50)

    all_correct = input("Качество анализа (отлично/хорошо/удовлетворительно/плохо): ").strip().lower()
    
    feedback_data = {
        "overall_correctness": all_correct,
        "comments": "",
        "object_feedback": [],
        "text_feedback": []
    }

    if all_correct in ["удовлетворительно", "плохо"]:
        print("\nПомогите улучшить анализ:")
        feedback_data["comments"] = input("• Что было определено неверно? ")
        missing_elements = input("• Какие элементы не были найдены? ")
        if missing_elements:
            feedback_data["comments"] += f" Пропущено: {missing_elements}"

    print("\n✅ Спасибо за обратную связь! Она поможет улучшить алгоритм.")
    print("="*50)
    return feedback_data

def save_learning_data(original_image_path, vision_objects, vision_texts, user_feedback, data_folder="learning_data"):
    """Сохраняет данные для 'обучения' (сбор данных)."""
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    # Создаем уникальное имя для набора данных (например, на основе timestamp)
    import time
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    entry_folder = os.path.join(data_folder, f"entry_{timestamp}")
    os.makedirs(entry_folder)

    # Копируем оригинальное изображение
    from shutil import copy
    base_image_name = os.path.basename(original_image_path)
    copied_image_path = os.path.join(entry_folder, base_image_name)
    copy(original_image_path, copied_image_path)    # Сохраняем результаты Vision API и фидбек пользователя (например, в JSON)
    import json
    data_to_save = {
        "original_image_path_in_entry": base_image_name,
        "vision_api_objects": [{"name": o.name, "score": o.score, "vertices": [(v.x, v.y) for v in o.bounding_poly.normalized_vertices]} for o in vision_objects],
        "vision_api_texts": [{"description": t.description, "vertices": [(v.x, v.y) for v in t.bounding_poly.vertices]} for t in (vision_texts[1:] if vision_texts else [])],
        "user_feedback": user_feedback
    }
    
    with open(os.path.join(entry_folder, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)
    
    print(f"Данные для обучения сохранены в: {entry_folder}")


# --- Функции анализа UI элементов ---

def analyze_ui_elements(image_path):
    """Анализирует UI элементы без OpenCV - используя PIL и базовые алгоритмы."""
    try:
        from PIL import Image, ImageStat
        import numpy as np
        
        # Загрузка изображения
        img = Image.open(image_path)
        print(f"   Размер изображения: {img.size[0]}x{img.size[1]} пикселей")
        
        # Преобразуем в RGB для анализа
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # 1. Простой анализ цветов
        color_analysis = analyze_colors_simple(img)
        
        # 2. Поиск прямоугольных областей (потенциальные кнопки/поля)
        ui_elements = find_rectangular_regions(img)
        
        # 3. Анализ общей структуры
        layout_analysis = analyze_layout_structure(img)
        
        print(f"   Найдено потенциальных UI элементов: {len(ui_elements)}")
        
        return {
            "color_analysis": color_analysis,
            "ui_elements": ui_elements,
            "layout_analysis": layout_analysis,
            "image_size": img.size
        }
        
    except Exception as e:
        print(f"   Ошибка при анализе UI элементов: {e}")
        return {
            "color_analysis": {},
            "ui_elements": [],
            "layout_analysis": {},
            "image_size": (0, 0)
        }

def analyze_colors_simple(img):
    """Простой анализ цветовой схемы изображения."""
    try:
        # Получаем статистику по цветам
        width, height = img.size
        pixels = list(img.getdata())
        
        # Подсчитываем наиболее частые цвета
        color_counts = {}
        for pixel in pixels[::100]:  # Берем каждый 100-й пиксель для ускорения
            color_counts[pixel] = color_counts.get(pixel, 0) + 1
        
        # Сортируем по частоте
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        dominant_colors = sorted_colors[:5]  # Топ 5 цветов
        
        return {
            "dominant_colors": dominant_colors,
            "total_unique_colors": len(color_counts),
            "analysis": "Простой анализ цветов"
        }
    except Exception as e:
        return {"error": str(e)}

def find_rectangular_regions(img):
    """Находит прямоугольные области, которые могут быть UI элементами."""
    try:
        import numpy as np
        
        # Преобразуем изображение в массив numpy
        img_array = np.array(img)
        width, height = img.size
        
        # Ищем области с однородными цветами (потенциальные кнопки)
        ui_elements = []
          # Простой алгоритм: разбиваем изображение на сетку и анализируем каждый блок
        block_size = 80  # Увеличиваем размер блока (было 50)
        min_variance_threshold = 500  # Снижаем порог однородности (было 1000)
        
        for y in range(0, height - block_size, block_size // 2):  # Меньше перекрытия
            for x in range(0, width - block_size, block_size // 2):
                # Извлекаем блок
                block = img_array[y:y+block_size, x:x+block_size]
                
                # Анализируем однородность цвета
                avg_color = np.mean(block, axis=(0, 1))
                color_variance = np.var(block, axis=(0, 1))
                
                # Более строгие критерии для UI элемента
                total_variance = np.sum(color_variance)
                if total_variance < min_variance_threshold:
                    # Дополнительная проверка - не слишком ли темный/светлый
                    brightness = np.mean(avg_color)
                    if 30 < brightness < 220:  # Исключаем слишком темные/светлые области
                        ui_elements.append({
                            "type": "potential_ui_element",
                            "bounds": (x, y, x+block_size, y+block_size),
                            "avg_color": avg_color.tolist(),
                            "confidence": min(0.8, 1.0 - (total_variance / min_variance_threshold))
                        })
        
        return ui_elements
        
    except Exception as e:
        print(f"Ошибка при поиске прямоугольных областей: {e}")
        return []

def analyze_layout_structure(img):
    """Анализирует общую структуру макета."""
    try:
        width, height = img.size
        
        # Определяем тип макета по пропорциям
        aspect_ratio = width / height
        
        if aspect_ratio > 1.5:
            layout_type = "landscape"
        elif aspect_ratio < 0.7:
            layout_type = "portrait"
        else:
            layout_type = "square"
        
        return {
            "type": layout_type,
            "aspect_ratio": aspect_ratio,
            "dimensions": f"{width}x{height}",
            "analysis": "Базовый анализ макета"
        }
        
    except Exception as e:
        return {"error": str(e)}

# --- Функции для классификации элементов ---

def analyze_color_type(rgb_color):
    """Определяет тип цвета (светлый, темный, яркий, приглушенный)."""
    r, g, b = rgb_color
    
    # Конвертируем в HSV для лучшего анализа
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    
    # Определяем яркость
    brightness = v
    saturation = s
    
    if brightness > 0.8:
        if saturation < 0.2:
            return "light_neutral"  # Светлый нейтральный (белый, светло-серый)
        else:
            return "light_vibrant"  # Светлый яркий
    elif brightness < 0.3:
        if saturation < 0.2:
            return "dark_neutral"   # Темный нейтральный (черный, темно-серый)
        else:
            return "dark_vibrant"   # Темный яркий
    else:
        if saturation > 0.6:
            return "vibrant"        # Яркий средний
        else:
            return "muted"          # Приглушенный средний

def determine_color_scheme_type(color_data):
    """Определяет тип цветовой схемы."""
    light_count = sum(1 for c in color_data if "light" in c["color_type"])
    dark_count = sum(1 for c in color_data if "dark" in c["color_type"])
    vibrant_count = sum(1 for c in color_data if "vibrant" in c["color_type"])
    
    if light_count > dark_count:
        if vibrant_count > 2:
            return "light_colorful"
        else:
            return "light_minimal"
    else:
        if vibrant_count > 2:
            return "dark_colorful"
        else:
            return "dark_minimal"

# --- Основной цикл работы агента ---
def main():
    print("\n" + "="*60)
    print("        AI-АГЕНТ ДЛЯ АНАЛИЗА UI ЭЛЕМЕНТОВ")
    print("="*60)
    print("Выберите режим работы:")
    print("1. 📊 Анализ изображения UI")
    print("2. 🔬 Исследование алгоритмов на GitHub")
    print("3. ❌ Выход")
    print("="*60)
    
    choice = input("Введите номер (1-3): ").strip()
    
    if choice == "2":
        research_ui_algorithms()
        return
    elif choice == "3":
        print("👋 До свидания!")
        return
    elif choice != "1":
        print("❌ Неверный выбор. Запуск анализа изображения...")
    
    print("\n" + "="*60)
    print("        РЕЖИМ АНАЛИЗА ИЗОБРАЖЕНИЯ")
    print("="*60)
    print("Возможности:")
    print("• Google Vision API - поиск текста и объектов")
    print("• Компьютерное зрение - анализ форм и контуров") 
    print("• Анализ цветовых схем")
    print("="*60)

    # 1. Получение изображения
    print("\n[1] Загрузка изображения...")
    original_image_path = get_image_from_user()
    if not original_image_path:
        return

    # 2. Анализ с помощью Google Vision API
    print("\n[2] Анализ с помощью Google Vision API...")
    objects, texts = analyze_image_with_vision_ai(original_image_path)
    if objects is None and texts is None:
        print("\n❌ ОШИБКА: Не удалось получить данные от Vision API")
        return
      # 3. Дополнительный анализ UI элементов
    print("\n[3] Дополнительный анализ UI элементов...")
    ui_analysis = analyze_ui_elements(original_image_path)
    
    # Выводим результаты анализа UI
    if ui_analysis and ui_analysis.get("ui_elements"):
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ АНАЛИЗА UI ЭЛЕМЕНТОВ")
        print("="*50)
        
        ui_elements = ui_analysis["ui_elements"]
        print(f"🔲 ПОТЕНЦИАЛЬНЫЕ UI ЭЛЕМЕНТЫ: {len(ui_elements)}")
        
        if ui_elements:
            for i, element in enumerate(ui_elements[:5], 1):  # Показываем первые 5
                bounds = element.get("bounds", [0, 0, 0, 0])
                width = bounds[2] - bounds[0]
                height = bounds[3] - bounds[1]
                print(f"   {i}. {element.get('type', 'unknown')} - {width}x{height}px")
            
            if len(ui_elements) > 5:
                print(f"   ... и еще {len(ui_elements) - 5} элементов")
        
        # Выводим анализ макета
        layout = ui_analysis.get("layout_analysis", {})
        if layout:
            print(f"\n📐 МАКЕТ: {layout.get('type', 'unknown')} ({layout.get('dimensions', 'unknown')})")
        
        # Выводим цветовую схему
        colors = ui_analysis.get("color_analysis", {})
        if colors and colors.get("dominant_colors"):
            print(f"\n🎨 ДОМИНИРУЮЩИЕ ЦВЕТА: {len(colors['dominant_colors'])} найдено")
            
        print("="*50)
    
    # Проверяем результаты анализа
    has_vision_results = (objects and len(objects) > 0) or (texts and len(texts) > 1)
    has_ui_results = ui_analysis and ui_analysis.get("ui_elements") and len(ui_analysis["ui_elements"]) > 0
    
    if not has_vision_results and not has_ui_results:
        print("\n" + "="*50)
        print("⚠️  РЕЗУЛЬТАТ: Элементы UI не найдены")
        print("="*50)
        user_expects_elements = input("Ожидали ли вы найти UI элементы? (да/нет): ").strip().lower()
        if user_expects_elements == 'да':
            print("\nВозможные причины:")
            print("• Изображение слишком размытое или сложное")
            print("• Нестандартный дизайн интерфейса") 
            print("• Требуется настройка параметров анализа")
        print("="*50)
        
        # Сохраняем "пустой" результат для анализа
        feedback_for_empty = {
            "overall_correctness": "плохо (ничего не найдено)", 
            "comments": "Агент не смог найти UI элементы",
            "expected_elements": user_expects_elements == 'да'
        }
        save_enhanced_learning_data(original_image_path, [], [], ui_analysis, feedback_for_empty)
        return

    # 4. Создание аннотированного изображения
    print("\n[4] Создание аннотированного изображения...")
    annotated_image_file = draw_annotations(original_image_path, 
        objects or [], 
        texts or [], 
        "enhanced_annotated_image.png",
        ui_analysis
    )
    
    if not annotated_image_file:
        print("❌ ОШИБКА: Не удалось создать аннотированное изображение")
        return

    # 5. Получение обратной связи
    print("\n[5] Получение обратной связи от пользователя...")
    user_feedback = get_user_feedback(
        annotated_image_file, 
        objects or [], 
        texts or []
    )

    # 6. Сохранение данных для обучения  
    print("\n[6] Сохранение результатов...")
    save_learning_data(original_image_path, objects or [], texts or [], user_feedback)

    print("\n" + "="*60)
    print("✅ АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!")
    print("="*60)
    print("Результаты:")
    print(f"• Аннотированное изображение: {annotated_image_file}")
    print("• Данные сохранены для дальнейшего анализа")
    print("• Обратная связь учтена для улучшения алгоритмов")
    print("="*60)

if __name__ == "__main__":
    main()

def draw_enhanced_annotations(image_path, vision_objects, vision_texts, ui_analysis, output_path="enhanced_annotated_output.png"):
    """Рисует улучшенные аннотации с анализом UI элементов."""
    try:
        pil_image = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(pil_image)
        img_width, img_height = pil_image.size
        
        try:
            font = ImageFont.truetype("arial.ttf", 12)
            title_font = ImageFont.truetype("arial.ttf", 16)
        except IOError:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()

        # Рисуем UI элементы найденные через компьютерное зрение
        if ui_analysis and ui_analysis.get("ui_elements"):
            for i, element in enumerate(ui_analysis["ui_elements"]):
                x, y = element["position"]
                w, h = element["size"]
                element_type = element["type"]
                
                # Выбираем цвет на основе типа элемента
                color_map = {
                    "button": "red",
                    "navigation_bar": "orange", 
                    "sidebar": "purple",
                    "panel": "cyan",
                    "text_area": "yellow",
                    "icon_button": "pink",
                    "large_button": "magenta"
                }
                box_color = color_map.get(element_type, "blue")
                
                # Рисуем рамку
                draw.rectangle([x, y, x + w, y + h], outline=box_color, width=3)
                
                # Добавляем метку с типом элемента
                label = f"UI_{i}: {element_type}"
                text_position = (x + 2, y + 2 if y < img_height - 40 else y - 20)
                draw.text(text_position, label, fill=box_color, font=font)

        # Рисуем объекты от Vision API (синим)
        if vision_objects:
            for i, obj in enumerate(vision_objects):
                box_color = "blue"
                vertices = obj.bounding_poly.normalized_vertices
                box = [
                    vertices[0].x * img_width, vertices[0].y * img_height,
                    vertices[2].x * img_width, vertices[2].y * img_height
                ]
                draw.rectangle(box, outline=box_color, width=2)
                label = f"Obj: {obj.name} ({obj.score:.2f})"
                text_position = (box[0] + 2, box[1] + 2 if box[1] < img_height - 20 else box[1] - 20)
                draw.text(text_position, label, fill=box_color, font=font)

        # Рисуем текстовые блоки от Vision API (зеленым)
        if vision_texts and len(vision_texts) > 1:
            for i, text_block in enumerate(vision_texts[1:]):
                box_color = "green"
                vertices = text_block.bounding_poly.vertices
                x_coords = [v.x for v in vertices]
                y_coords = [v.y for v in vertices]
                box = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]
                
                draw.rectangle(box, outline=box_color, width=1)
                label = f"Txt: {text_block.description.replace(chr(10), ' ')}"[:25]
                text_position = (box[0] + 2, box[1] + 2 if box[1] < img_height - 20 else box[1] - 20)
                draw.text(text_position, label, fill=box_color, font=font)

        # Добавляем информацию о цветовой схеме
        if ui_analysis and ui_analysis.get("color_analysis"):
            color_info = ui_analysis["color_analysis"]
            scheme_type = color_info.get("color_scheme_type", "unknown")
            
            # Рисуем информацию о цветовой схеме в углу
            info_text = f"Цветовая схема: {scheme_type}"
            draw.text((10, 10), info_text, fill="black", font=title_font)
            
            # Рисуем палитру доминирующих цветов
            if "dominant_colors" in color_info:
                for i, color_data in enumerate(color_info["dominant_colors"][:5]):
                    color_rgb = tuple(color_data["rgb"])
                    x_pos = 10 + i * 40
                    y_pos = 35
                    draw.rectangle([x_pos, y_pos, x_pos + 30, y_pos + 20], fill=color_rgb, outline="black")
                    draw.text((x_pos, y_pos + 25), f"{color_data['percentage']:.1f}%", fill="black", font=font)

        pil_image.save(output_path)
        print(f"Улучшенное аннотированное изображение сохранено как: {output_path}")
        pil_image.show()
        return output_path
        
    except Exception as e:
        print(f"Ошибка при создании улучшенных аннотаций: {e}")
        return None

def get_enhanced_user_feedback(annotated_image_path, vision_objects, vision_texts, ui_analysis):
    """Запрашивает расширенную обратную связь с учетом UI анализа."""
    print("\n=== РАСШИРЕННЫЙ АНАЛИЗ UI ЭЛЕМЕНТОВ ===")
    print(f"Аннотированное изображение: {annotated_image_path}")
    
    # Показываем статистику найденных элементов
    ui_count = len(ui_analysis.get("ui_elements", [])) if ui_analysis else 0
    vision_obj_count = len(vision_objects) if vision_objects else 0
    vision_text_count = len(vision_texts) - 1 if vision_texts and len(vision_texts) > 1 else 0
    
    print(f"\nСтатистика анализа:")
    print(f"  🔸 UI элементов (компьютерное зрение): {ui_count}")
    print(f"  🔹 Объектов (Vision API): {vision_obj_count}")  
    print(f"  🔹 Текстовых блоков (Vision API): {vision_text_count}")
    
    # Показываем информацию о цветовой схеме
    if ui_analysis and ui_analysis.get("color_analysis"):
        color_info = ui_analysis["color_analysis"]
        print(f"  🎨 Цветовая схема: {color_info.get('color_scheme_type', 'неопределена')}")
        
        if "dominant_colors" in color_info:
            print("  🎨 Доминирующие цвета:")
            for i, color_data in enumerate(color_info["dominant_colors"][:3]):
                print(f"     {i+1}. {color_data['hex']} ({color_data['percentage']:.1f}%) - {color_data['color_type']}")

    # Показываем типы найденных UI элементов
    if ui_analysis and ui_analysis.get("ui_elements"):
        element_types = {}
        for element in ui_analysis["ui_elements"]:
            elem_type = element["type"]
            element_types[elem_type] = element_types.get(elem_type, 0) + 1
        
        print("  📱 Типы UI элементов:")
        for elem_type, count in element_types.items():
            print(f"     - {elem_type}: {count}")

    # Получаем обратную связь
    print("\n=== ОБРАТНАЯ СВЯЗЬ ===")
    overall_correct = input("Общая оценка качества анализа UI (отлично/хорошо/удовлетворительно/плохо): ").strip().lower()
    
    feedback_data = {
        "overall_correctness": overall_correct,
        "ui_elements_feedback": {},
        "color_scheme_feedback": {},
        "suggestions": "",
        "missing_elements": "",
        "statistics": {
            "ui_elements_found": ui_count,
            "vision_objects_found": vision_obj_count,
            "vision_texts_found": vision_text_count
        }
    }

    if overall_correct in ["удовлетворительно", "плохо"]:
        print("\nДавайте уточним детали:")
        
        # Обратная связь по UI элементам
        ui_elements_correct = input("UI элементы (красные/оранжевые/фиолетовые рамки) найдены корректно? (да/нет/частично): ").strip().lower()
        feedback_data["ui_elements_feedback"]["correctness"] = ui_elements_correct
        
        if ui_elements_correct != "да":
            missing = input("Какие UI элементы пропущены? (кнопки/панели/меню/окна/другое): ")
            feedback_data["missing_elements"] = missing
            
            incorrect = input("Какие найденные элементы неверны?: ")
            feedback_data["ui_elements_feedback"]["incorrect"] = incorrect

        # Обратная связь по цветовой схеме
        if ui_analysis and ui_analysis.get("color_analysis"):
            colors_correct = input("Цветовая схема определена правильно? (да/нет): ").strip().lower()
            feedback_data["color_scheme_feedback"]["correctness"] = colors_correct
            
            if colors_correct == "нет":
                correct_scheme = input("Какая цветовая схема правильная? (светлая/темная/яркая/минималистичная): ")
                feedback_data["color_scheme_feedback"]["correct_scheme"] = correct_scheme

        # Общие предложения
        suggestions = input("Есть ли предложения по улучшению анализа?: ")
        feedback_data["suggestions"] = suggestions

    print("Спасибо за подробную обратную связь!")
    return feedback_data

def save_enhanced_learning_data(original_image_path, vision_objects, vision_texts, ui_analysis, user_feedback, data_folder="enhanced_learning_data"):
    """Сохраняет расширенные данные для обучения включая UI анализ."""
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    # Создаем уникальное имя для набора данных
    import time
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    entry_folder = os.path.join(data_folder, f"ui_analysis_{timestamp}")
    os.makedirs(entry_folder)

    # Копируем оригинальное изображение
    from shutil import copy
    base_image_name = os.path.basename(original_image_path)
    copied_image_path = os.path.join(entry_folder, base_image_name)
    copy(original_image_path, copied_image_path)

    # Сохраняем комплексные результаты анализа
    import json
    data_to_save = {
        "metadata": {
            "timestamp": timestamp,
            "original_image_path": base_image_name,
            "analysis_version": "enhanced_v1.0"
        },
        "vision_api_results": {
            "objects": [
                {
                    "name": o.name, 
                    "score": o.score, 
                    "vertices": [(v.x, v.y) for v in o.bounding_poly.normalized_vertices]
                } for o in vision_objects
            ],
            "texts": [
                {
                    "description": t.description, 
                    "vertices": [(v.x, v.y) for v in t.bounding_poly.vertices]
                } for t in (vision_texts[1:] if vision_texts else [])
            ]
        },
        "ui_analysis": ui_analysis,
        "user_feedback": user_feedback
    }
    
    # Сохраняем в JSON с красивым форматированием
    with open(os.path.join(entry_folder, "enhanced_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)
    
    # Создаем краткий отчет в текстовом формате
    report_path = os.path.join(entry_folder, "analysis_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"=== ОТЧЕТ ПО АНАЛИЗУ UI ЭЛЕМЕНТОВ ===\n")
        f.write(f"Дата и время: {timestamp}\n")
        f.write(f"Изображение: {base_image_name}\n\n")
        
        f.write(f"РЕЗУЛЬТАТЫ VISION API:\n")
        f.write(f"  - Объектов найдено: {len(vision_objects)}\n")
        f.write(f"  - Текстовых блоков: {len(vision_texts) - 1 if vision_texts else 0}\n\n")
        
        if ui_analysis:
            f.write(f"РЕЗУЛЬТАТЫ UI АНАЛИЗА:\n")
            f.write(f"  - UI элементов найдено: {len(ui_analysis.get('ui_elements', []))}\n")
            
            if ui_analysis.get("color_analysis"):
                color_info = ui_analysis["color_analysis"]
                f.write(f"  - Цветовая схема: {color_info.get('color_scheme_type', 'неопределена')}\n")
                if "dominant_colors" in color_info:
                    f.write(f"  - Доминирующие цвета:\n")
                    for i, color_data in enumerate(color_info["dominant_colors"][:3]):
                        f.write(f"    {i+1}. {color_data['hex']} ({color_data['percentage']:.1f}%)\n")
            
            if ui_analysis.get("ui_elements"):
                element_types = {}
                for element in ui_analysis["ui_elements"]:
                    elem_type = element["type"]
                    element_types[elem_type] = element_types.get(elem_type, 0) + 1
                
                f.write(f"  - Типы элементов:\n")
                for elem_type, count in element_types.items():
                    f.write(f"    {elem_type}: {count}\n")
        
        f.write(f"\nОБРАТНАЯ СВЯЗЬ ПОЛЬЗОВАТЕЛЯ:\n")
        f.write(f"  - Общая оценка: {user_feedback.get('overall_correctness', 'не указана')}\n")
        if user_feedback.get("suggestions"):
            f.write(f"  - Предложения: {user_feedback['suggestions']}\n")
        if user_feedback.get("missing_elements"):
            f.write(f"  - Пропущенные элементы: {user_feedback['missing_elements']}\n")
    
    print(f"📊 Расширенные данные анализа сохранены в: {entry_folder}")
    print(f"📋 Краткий отчет: {report_path}")

def research_ui_algorithms():
    """Исследование алгоритмов UI анализа на GitHub"""
    print("\n🔬 === ИССЛЕДОВАНИЕ АЛГОРИТМОВ UI АНАЛИЗА ===")
    print("Поиск лучших решений на GitHub...")
    
    try:
        # Создаем исследователя
        researcher = GitHubUIResearcher()
        
        # Выполняем поиск
        print("🔍 Начинаю поиск репозиториев...")
        repos = researcher.search_ui_analysis_repositories(max_results=20)
        
        if repos:
            # Выводим результаты
            researcher.print_research_summary(repos)
            
            # Сохраняем результаты
            saved_file = researcher.save_research_results(repos)
            
            # Анализируем топ-3 репозитория более детально
            print("\n🔬 ДЕТАЛЬНЫЙ АНАЛИЗ ТОП-3 РЕПОЗИТОРИЕВ:")
            print("=" * 50)
            
            for i, repo in enumerate(repos[:3], 1):
                print(f"\n{i}. {repo['name']} ({repo['stars']} ⭐)")
                print(f"   🔗 {repo['html_url']}")
                
                # Получаем README
                readme = researcher.get_repository_readme(repo['full_name'])
                if readme:
                    # Извлекаем первые 200 символов описания
                    description = readme.replace('\n', ' ')[:200] + "..."
                    print(f"   📄 Описание: {description}")
                
                # Анализируем структуру кода
                code_analysis = researcher.analyze_repository_code(repo['full_name'])
                if 'error' not in code_analysis:
                    print(f"   📁 Файлов: {code_analysis['total_files']}, "
                          f"Кода: {code_analysis['code_files']}")
                    if code_analysis['key_files']:
                        print(f"   🔑 Ключевые файлы: {', '.join(code_analysis['key_files'][:3])}")
                
                print()
            
            # Рекомендации по улучшению
            print("\n💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ АГЕНТА:")
            print("-" * 40)
            
            python_repos = [r for r in repos if r['language'] == 'Python']
            if python_repos:
                print(f"1. 🐍 Изучить Python решения ({len(python_repos)} репозиториев)")
                top_python = python_repos[0]
                print(f"   Рекомендуется: {top_python['name']} - {top_python['html_url']}")
            
            opencv_repos = [r for r in repos if 'opencv' in r['name'].lower() or 
                           'opencv' in r['description'].lower()]
            if opencv_repos:
                print(f"2. 👁️ Интегрировать OpenCV методы ({len(opencv_repos)} репозиториев)")
            
            ml_repos = [r for r in repos if any(keyword in r['description'].lower() 
                       for keyword in ['machine learning', 'deep learning', 'neural'])]
            if ml_repos:
                print(f"3. 🧠 Рассмотреть ML подходы ({len(ml_repos)} репозиториев)")
            
            automation_repos = [r for r in repos if any(keyword in r['description'].lower() 
                               for keyword in ['selenium', 'playwright', 'automation'])]
            if automation_repos:
                print(f"4. 🤖 Изучить автоматизацию тестирования ({len(automation_repos)} репозиториев)")
            
            print(f"\n✅ Результаты исследования сохранены в: {saved_file}")
            
        else:
            print("❌ Репозитории не найдены. Проверьте подключение к интернету.")
            
    except Exception as e:
        print(f"❌ Ошибка при исследовании: {e}")
        print("💡 Убедитесь, что у вас есть доступ к интернету")
        print("💡 Для лучших результатов установите GITHUB_TOKEN в переменные окружения")