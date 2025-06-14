import os
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

# Существующие импорты
from agent import UIAnalysisAgent
from constants import MOBILE_GAMING_UI_TAXONOMY, ALL_UI_TAGS

# Новые гибридные агенты
try:
    from hybrid_vision_agent import HybridUIVisionAgent
    HYBRID_AVAILABLE = True
except ImportError:
    HYBRID_AVAILABLE = False
    logging.warning("Гибридный агент недоступен")

class EnhancedUIAnalysisAgent(UIAnalysisAgent):
    """Расширенный агент с поддержкой гибридного AI Vision анализа"""
    
    def __init__(self, credentials=None, anthropic_api_key=None, enable_hybrid=True):
        """
        Инициализация расширенного агента
        
        Args:
            credentials: Google OAuth2 credentials
            anthropic_api_key: API ключ для Claude Vision
            enable_hybrid: Включить гибридный анализ
        """
        # Инициализация базового агента
        super().__init__(credentials)
        
        # Инициализация гибридного анализа
        self.hybrid_agent = None
        self.hybrid_enabled = False
        
        if enable_hybrid and HYBRID_AVAILABLE:
            try:
                self.hybrid_agent = HybridUIVisionAgent(
                    anthropic_api_key=anthropic_api_key,
                    enable_phi=True,
                    enable_claude=bool(anthropic_api_key)
                )
                self.hybrid_enabled = True
                logging.info("✅ Гибридный AI Vision агент активирован")
            except Exception as e:
                logging.error(f"❌ Ошибка инициализации гибридного агента: {str(e)}")
        
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def get_analysis_capabilities(self) -> Dict[str, bool]:
        """Получить доступные возможности анализа"""
        capabilities = {
            "google_vision": bool(self.client),
            "hybrid_vision": self.hybrid_enabled,
            "phi_vision": False,
            "claude_vision": False
        }
        
        if self.hybrid_agent:
            available_services = self.hybrid_agent.get_available_services()
            capabilities["phi_vision"] = "phi" in available_services
            capabilities["claude_vision"] = "claude" in available_services
        
        return capabilities
    
    async def analyze_screenshot_enhanced(self, image_path: str, analysis_method: str = "auto") -> Dict:
        """
        Расширенный анализ скриншота с использованием множественных AI сервисов
        
        Args:
            image_path: Путь к изображению
            analysis_method: Метод анализа ('auto', 'google_only', 'hybrid', 'phi', 'claude')
        
        Returns:
            Словарь с результатами анализа
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Изображение не найдено: {image_path}")
        
        logging.info(f"🎯 Начинаю анализ: {image_path.name}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "image_path": str(image_path),
            "analysis_method": analysis_method,
            "capabilities": self.get_analysis_capabilities()
        }
        
        # Выбор метода анализа
        if analysis_method == "auto":
            analysis_method = self._choose_optimal_method()
        
        # Google Vision анализ (базовый)
        if analysis_method in ["auto", "google_only", "hybrid"] and self.client:
            logging.info("🔄 Google Vision анализ...")
            try:
                google_results = self.analyze_image(str(image_path))
                results["google_vision"] = google_results
                logging.info(f"✅ Google Vision: {google_results['statistics']}")
            except Exception as e:
                logging.error(f"❌ Google Vision ошибка: {str(e)}")
                results["google_vision_error"] = str(e)
        
        # Гибридный AI Vision анализ
        if analysis_method in ["hybrid", "phi", "claude"] and self.hybrid_enabled:
            logging.info("🔄 Гибридный AI Vision анализ...")
            try:
                # Выбор стратегии для гибридного анализа
                if analysis_method == "hybrid":
                    strategy = "hybrid"
                elif analysis_method == "phi":
                    strategy = "phi"
                elif analysis_method == "claude":
                    strategy = "claude"
                else:
                    strategy = "auto"
                
                hybrid_results = await self.hybrid_agent.smart_ui_analysis(
                    str(image_path), strategy
                )
                results["hybrid_vision"] = hybrid_results
                logging.info(f"✅ Гибридный анализ: {hybrid_results.get('method_used', 'unknown')}")
            except Exception as e:
                logging.error(f"❌ Гибридный анализ ошибка: {str(e)}")
                results["hybrid_vision_error"] = str(e)
        
        # Объединение и анализ результатов
        results["combined_analysis"] = self._combine_all_results(results)
        results["confidence_score"] = self._calculate_overall_confidence(results)
        
        # Сохранение в обучающий датасет
        self._save_enhanced_learning_data(results)
        
        logging.info(f"🎉 Анализ завершен. Confidence: {results['confidence_score']:.2f}")
        return results
    
    def _choose_optimal_method(self) -> str:
        """Автоматический выбор оптимального метода анализа"""
        capabilities = self.get_analysis_capabilities()
        
        if capabilities["hybrid_vision"]:
            return "hybrid"
        elif capabilities["claude_vision"]:
            return "claude"
        elif capabilities["phi_vision"]:
            return "phi"
        elif capabilities["google_vision"]:
            return "google_only"
        else:
            raise Exception("Нет доступных методов анализа")
    
    def _combine_all_results(self, results: Dict) -> Dict:
        """Объединение результатов всех анализов"""
        combined = {
            "summary": {},
            "ui_elements_consensus": [],
            "text_analysis": {},
            "recommendations": []
        }
        
        # Анализ Google Vision результатов
        if "google_vision" in results:
            gv = results["google_vision"]
            combined["summary"]["google_objects"] = gv.get("statistics", {}).get("objects_count", 0)
            combined["summary"]["google_texts"] = gv.get("statistics", {}).get("texts_count", 0)
            combined["text_analysis"]["google_extracted"] = len(gv.get("texts", []))
        
        # Анализ гибридных результатов
        if "hybrid_vision" in results:
            hv = results["hybrid_vision"]
            combined["summary"]["hybrid_method"] = hv.get("method_used", "unknown")
            combined["summary"]["hybrid_confidence"] = hv.get("confidence_score", 0)
            
            # Рекомендации на основе доступных сервисов
            if "phi_analysis" in hv and "claude_analysis" in hv:
                combined["recommendations"].append("Используйте консенсус Phi + Claude для максимальной точности")
            elif "claude_analysis" in hv:
                combined["recommendations"].append("Claude Vision дал детальный анализ UI структуры")
            elif "phi_analysis" in hv:
                combined["recommendations"].append("Phi Vision обеспечил быстрый локальный анализ")
        
        return combined
    
    def _calculate_overall_confidence(self, results: Dict) -> float:
        """Расчет общей уверенности в результатах"""
        confidence_factors = []
        
        # Google Vision factor
        if "google_vision" in results:
            gv_stats = results["google_vision"].get("statistics", {})
            if gv_stats.get("objects_count", 0) > 0 or gv_stats.get("texts_count", 0) > 0:
                confidence_factors.append(0.7)
        
        # Hybrid Vision factor
        if "hybrid_vision" in results:
            hv_confidence = results["hybrid_vision"].get("confidence_score", 0)
            confidence_factors.append(hv_confidence)
        
        # Среднее значение с бонусом за множественные источники
        if confidence_factors:
            base_confidence = sum(confidence_factors) / len(confidence_factors)
            # Бонус за использование нескольких источников
            multiple_sources_bonus = 0.1 if len(confidence_factors) > 1 else 0
            return min(base_confidence + multiple_sources_bonus, 0.99)
        else:
            return 0.3
    
    def _save_enhanced_learning_data(self, results: Dict):
        """Сохранение расширенных данных обучения"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Создание директории для расширенных данных
        enhanced_dir = Path("learning_data") / "enhanced"
        enhanced_dir.mkdir(parents=True, exist_ok=True)
        
        # Сохранение полного анализа
        full_analysis_path = enhanced_dir / f"enhanced_analysis_{timestamp}.json"
        with open(full_analysis_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Сохранение сводки для быстрого анализа
        summary_path = enhanced_dir / f"summary_{timestamp}.json"
        summary_data = {
            "timestamp": results["timestamp"],
            "image_path": results["image_path"],
            "method": results["analysis_method"],
            "confidence": results["confidence_score"],
            "capabilities_used": results["capabilities"],
            "summary": results["combined_analysis"]["summary"]
        }
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"💾 Данные сохранены: {full_analysis_path.name}")
    
    async def batch_analyze_screenshots(self, 
                                       image_directory: str, 
                                       pattern: str = "*.png",
                                       max_files: int = None,
                                       analysis_method: str = "auto") -> List[Dict]:
        """
        Массовый анализ скриншотов
        
        Args:
            image_directory: Директория с изображениями
            pattern: Паттерн файлов (например, "*.png", "*.jpg")
            max_files: Максимальное количество файлов для обработки
            analysis_method: Метод анализа
        
        Returns:
            Список результатов анализа
        """
        image_dir = Path(image_directory)
        if not image_dir.exists():
            raise FileNotFoundError(f"Директория не найдена: {image_dir}")
        
        # Поиск файлов изображений
        image_files = list(image_dir.glob(pattern))
        if max_files:
            image_files = image_files[:max_files]
        
        if not image_files:
            logging.warning(f"Файлы изображений не найдены в {image_dir} с паттерном {pattern}")
            return []
        
        logging.info(f"🚀 Начинаю массовый анализ {len(image_files)} файлов...")
        
        results = []
        for i, image_file in enumerate(image_files):
            logging.info(f"📸 Обрабатываю {i+1}/{len(image_files)}: {image_file.name}")
            
            try:
                result = await self.analyze_screenshot_enhanced(
                    str(image_file), 
                    analysis_method
                )
                results.append(result)
                
                # Небольшая пауза между запросами для API rate limiting
                if i % 5 == 0 and i > 0:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logging.error(f"❌ Ошибка обработки {image_file.name}: {str(e)}")
                results.append({
                    "timestamp": datetime.now().isoformat(),
                    "image_path": str(image_file),
                    "error": str(e)
                })
        
        # Сохранение результатов массового анализа
        batch_results_path = self._save_batch_results(results)
        logging.info(f"🎉 Массовый анализ завершен. Результаты: {batch_results_path}")
        
        return results
    
    def _save_batch_results(self, results: List[Dict]) -> Path:
        """Сохранение результатов массового анализа"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_dir = Path("learning_data") / "batch_analysis"
        batch_dir.mkdir(parents=True, exist_ok=True)
        
        # Статистика
        successful = [r for r in results if "error" not in r]
        failed = [r for r in results if "error" in r]
        
        batch_summary = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) if results else 0,
            "average_confidence": sum(r.get("confidence_score", 0) for r in successful) / len(successful) if successful else 0,
            "failed_files": [r["image_path"] for r in failed]
        }
        
        # Сохранение полных результатов
        full_results_path = batch_dir / f"batch_full_{timestamp}.json"
        with open(full_results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Сохранение сводки
        summary_path = batch_dir / f"batch_summary_{timestamp}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(batch_summary, f, ensure_ascii=False, indent=2)
        
        logging.info(f"📊 Статистика: {batch_summary['successful']}/{batch_summary['total_files']} успешно")
        
        return full_results_path
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.hybrid_agent:
            self.hybrid_agent.cleanup()
        logging.info("🧹 Расширенный агент очищен")
