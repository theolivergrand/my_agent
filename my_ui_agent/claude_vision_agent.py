import asyncio
import base64
import json
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("Anthropic не установлен. Claude Vision будет недоступен.")

class ClaudeVisionAgent:
    def __init__(self, api_key: Optional[str] = None):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library не установлен. Установите: pip install anthropic")
        
        if not api_key:
            raise ValueError("API ключ Anthropic обязателен")
        
        self.client = Anthropic(api_key=api_key)
        logging.info("ClaudeVisionAgent инициализирован")
    
    def encode_image(self, image_path: str) -> str:
        """Кодирование изображения для Claude"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logging.error(f"Ошибка кодирования изображения {image_path}: {str(e)}")
            raise
    
    async def analyze_image(self, image_path: str, prompt: str = "Describe this image") -> str:
        """Анализ изображения через Claude Vision"""
        try:
            image_data = self.encode_image(image_path)
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            logging.error(f"Ошибка анализа через Claude: {str(e)}")
            return f"Claude analysis error: {str(e)}"
    
    async def analyze_ui_comprehensive(self, image_path: str, ui_taxonomy: List[str], gaming_tags: List[str]) -> str:
        """Комплексный анализ UI элементов"""
        prompt = f"""
Проанализируй этот UI скриншот максимально детально:

1. **UI ЭЛЕМЕНТЫ**: Найди и опиши все элементы из этого списка:
{', '.join(ui_taxonomy)}

2. **GAMING UI**: Определи наличие gaming-специфичных элементов:
{', '.join(gaming_tags)}

3. **СТРУКТУРА И ДИЗАЙН**: 
   - Общий макет и композицию
   - Иерархию элементов
   - Цветовую схему и палитру
   - Типографику и шрифты
   - Стиль дизайна (flat, material, skeuomorphic и т.д.)

4. **ФУНКЦИОНАЛЬНОСТЬ**: 
   - Назначение каждого найденного элемента
   - Возможные пользовательские действия
   - Навигационные паттерны
   - UX принципы

5. **ПОЗИЦИОНИРОВАНИЕ**:
   - Приблизительные координаты элементов
   - Размеры и пропорции
   - Выравнивание и отступы

Ответь в структурированном JSON формате:
{{
  "ui_elements": [
    {{
      "type": "тип элемента",
      "description": "описание",
      "position": "позиция на экране",
      "function": "функциональное назначение",
      "confidence": 0.95
    }}
  ],
  "gaming_elements": ["список gaming элементов"],
  "layout": {{
    "type": "тип макета",
    "hierarchy": "описание иерархии",
    "color_scheme": "цветовая схема",
    "style": "стиль дизайна"
  }},
  "functionality": {{
    "primary_actions": ["основные действия"],
    "navigation": "навигационная структура",
    "user_flow": "пользовательский сценарий"
  }},
  "technical_details": {{
    "platform": "платформа (web/mobile/desktop)",
    "framework_hints": "возможный фреймворк",
    "responsive": "адаптивность"
  }}
}}
"""
        return await self.analyze_image(image_path, prompt)
    
    async def analyze_ui_quick(self, image_path: str) -> str:
        """Быстрый анализ UI"""
        prompt = """
Быстро проанализируй основные UI элементы:
- Тип интерфейса (web/mobile/desktop/gaming)
- Основные интерактивные элементы (кнопки, формы, меню)
- Цветовая схема
- Общее назначение экрана

Ответ кратко, по пунктам.
"""
        return await self.analyze_image(image_path, prompt)
    
    async def compare_ui_elements(self, image_paths: List[str]) -> str:
        """Сравнение UI элементов на нескольких изображениях"""
        if len(image_paths) > 4:
            raise ValueError("Claude Vision поддерживает максимум 4 изображения за раз")
        
        try:
            content = []
            
            # Добавляем изображения
            for i, image_path in enumerate(image_paths):
                image_data = self.encode_image(image_path)
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data
                    }
                })
            
            # Добавляем текстовый промпт
            content.append({
                "type": "text",
                "text": f"""
Сравни UI элементы на этих {len(image_paths)} изображениях:

1. Общие паттерны дизайна
2. Различия в компонентах
3. Консистентность стиля
4. Эволюция интерфейса (если применимо)
5. Лучшие практики UX

Структурированный анализ с конкретными примерами.
"""
            })
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": content}]
            )
            
            return response.content[0].text
        
        except Exception as e:
            logging.error(f"Ошибка сравнения UI: {str(e)}")
            return f"UI comparison error: {str(e)}"
