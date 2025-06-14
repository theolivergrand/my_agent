import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from PIL import Image
import requests
import logging

class PhiVisionAgent:
    def __init__(self, model_name="microsoft/Phi-3.5-vision-instruct"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.processor = None
        self.model_name = model_name
        self.initialized = False
        
        logging.info(f"PhiVisionAgent инициализирован для устройства: {self.device}")
    
    def _lazy_load_model(self):
        """Ленивая загрузка модели для экономии памяти"""
        if not self.initialized:
            try:
                logging.info(f"Загрузка модели {self.model_name}...")
                
                # Загрузка модели и процессора
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    trust_remote_code=True,
                    device_map="auto" if self.device == "cuda" else None
                )
                
                if self.device == "cpu":
                    self.model = self.model.to(self.device)
                
                self.processor = AutoProcessor.from_pretrained(
                    self.model_name,
                    trust_remote_code=True
                )
                
                self.initialized = True
                logging.info("Модель Phi Vision успешно загружена")
                
            except Exception as e:
                logging.error(f"Ошибка загрузки модели Phi Vision: {str(e)}")
                raise
    
    def analyze_image(self, image_path, prompt="Describe this image"):
        """Анализ изображения с помощью Phi Vision"""
        try:
            self._lazy_load_model()
            
            # Загрузка изображения
            if image_path.startswith('http'):
                image = Image.open(requests.get(image_path, stream=True).raw)
            else:
                image = Image.open(image_path)
            
            # Подготовка входных данных
            messages = [
                {"role": "user", "content": f"<|image_1|>\n{prompt}"}
            ]
            
            # Обработка
            inputs = self.processor.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            inputs = self.processor(
                inputs, 
                [image], 
                return_tensors="pt"
            ).to(self.device)
            
            # Генерация ответа
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=500,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            # Декодирование результата
            response = self.processor.decode(
                outputs[0], 
                skip_special_tokens=True
            )
            
            # Извлечение ответа ассистента
            if "assistant" in response:
                return response.split("assistant")[-1].strip()
            else:
                return response.strip()
                
        except Exception as e:
            logging.error(f"Ошибка анализа изображения: {str(e)}")
            return f"Ошибка анализа изображения: {str(e)}"
    
    def analyze_ui_elements(self, image_path):
        """Специализированный анализ UI элементов"""
        prompt = """
Проанализируй UI элементы на этом скриншоте:

1. Найди и опиши все интерактивные элементы:
   - Кнопки (buttons)
   - Поля ввода (input fields)
   - Меню (menus)
   - Иконки (icons)
   - Ссылки (links)

2. Определи тип интерфейса:
   - Web приложение
   - Mobile приложение
   - Desktop приложение
   - Gaming UI

3. Опиши структуру:
   - Основные функциональные блоки
   - Навигационные элементы
   - Цветовую схему

Ответ структурируй по пунктам.
"""
        return self.analyze_image(image_path, prompt)
    
    def multi_image_analysis(self, image_paths, prompt="Compare these images"):
        """Анализ нескольких изображений"""
        try:
            self._lazy_load_model()
            
            images = []
            for path in image_paths:
                if path.startswith('http'):
                    img = Image.open(requests.get(path, stream=True).raw)
                else:
                    img = Image.open(path)
                images.append(img)
            
            # Создание сообщения с несколькими изображениями
            image_tokens = " ".join([f"<|image_{i+1}|>" for i in range(len(images))])
            messages = [
                {"role": "user", "content": f"{image_tokens}\n{prompt}"}
            ]
            
            inputs = self.processor.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            inputs = self.processor(
                inputs, 
                images, 
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=500,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            response = self.processor.decode(
                outputs[0], 
                skip_special_tokens=True
            )
            
            if "assistant" in response:
                return response.split("assistant")[-1].strip()
            else:
                return response.strip()
                
        except Exception as e:
            logging.error(f"Ошибка анализа множественных изображений: {str(e)}")
            return f"Ошибка анализа изображений: {str(e)}"
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.model is not None:
            del self.model
            del self.processor
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self.initialized = False
            logging.info("Модель Phi Vision выгружена из памяти")
