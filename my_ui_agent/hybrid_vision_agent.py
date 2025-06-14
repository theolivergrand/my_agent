import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

# Импорты с проверкой доступности
try:
    from phi_vision_agent import PhiVisionAgent
    PHI_AVAILABLE = True
except ImportError:
    PHI_AVAILABLE = False
    logging.warning("Phi Vision недоступен. Установите torch и transformers.")

try:
    from claude_vision_agent import ClaudeVisionAgent
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    logging.warning("Claude Vision недоступен. Установите anthropic.")

from constants import UI_ELEMENTS, GAMING_UI_TAGS

class HybridUIVisionAgent:
    def __init__(self, anthropic_api_key: str = None, enable_phi: bool = True, enable_claude: bool = True):
        self.phi_agent = None
        self.claude_agent = None
        
        # Инициализация Phi Vision
        if enable_phi and PHI_AVAILABLE:
            try:
                self.phi_agent = PhiVisionAgent()
                logging.info("✅ Phi Vision активирован")
            except Exception as e:
                logging.error(f"❌ Ошибка инициализации Phi Vision: {str(e)}")
        
        # Инициализация Claude Vision
        if enable_claude and CLAUDE_AVAILABLE and anthropic_api_key:
            try:
                self.claude_agent = ClaudeVisionAgent(anthropic_api_key)
                logging.info("✅ Claude Vision активирован")
            except Exception as e:
                logging.error(f"❌ Ошибка инициализации Claude Vision: {str(e)}")
        
        self.ui_taxonomy = UI_ELEMENTS
        self.gaming_tags = GAMING_UI_TAGS
        
        # Логирование доступных сервисов
        available_services = []
        if self.phi_agent:
            available_services.append("Phi Vision")
        if self.claude_agent:
            available_services.append("Claude Vision")
        
        if available_services:
            logging.info(f"🚀 Гибридный агент инициализирован с сервисами: {', '.join(available_services)}")
        else:
            logging.warning("⚠️ Ни один сервис Vision не доступен!")
    
    def get_available_services(self) -> List[str]:
        """Получить список доступных сервисов"""
        services = []
        if self.phi_agent:
            services.append("phi")
        if self.claude_agent:
            services.append("claude")
        return services
    
    async def analyze_ui_with_claude(self, image_path: str, analysis_type: str = "comprehensive") -> str:
        """Анализ UI через Claude"""
        if not self.claude_agent:
            return "Claude Vision недоступен"
        
        if analysis_type == "comprehensive":
            return await self.claude_agent.analyze_ui_comprehensive(
                image_path, self.ui_taxonomy, self.gaming_tags
            )
        else:
            return await self.claude_agent.analyze_ui_quick(image_path)
    
    def analyze_ui_with_phi(self, image_path: str) -> str:
        """Анализ UI через Phi"""
        if not self.phi_agent:
            return "Phi Vision недоступен"
        
        return self.phi_agent.analyze_ui_elements(image_path)
    
    async def smart_ui_analysis(self, image_path: str, strategy: str = "auto") -> Dict:
        """Интеллектуальный UI анализ"""
        results = {
            "image_path": str(image_path),
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy,
            "available_services": self.get_available_services()
        }
        
        # Автоматический выбор стратегии
        if strategy == "auto":
            strategy = self._choose_strategy()
        
        # Выполнение анализа согласно стратегии
        if strategy == "phi" and self.phi_agent:
            logging.info("🔄 Анализ через Phi Vision...")
            results["phi_analysis"] = self.analyze_ui_with_phi(image_path)
            results["method_used"] = "phi_only"
        
        elif strategy == "claude" and self.claude_agent:
            logging.info("🔄 Анализ через Claude Vision...")
            results["claude_analysis"] = await self.analyze_ui_with_claude(image_path, "comprehensive")
            results["method_used"] = "claude_only"
        
        elif strategy == "hybrid":
            # Гибридный анализ
            if self.phi_agent:
                logging.info("🔄 Phi Vision анализ...")
                results["phi_analysis"] = self.analyze_ui_with_phi(image_path)
            
            if self.claude_agent:
                logging.info("🔄 Claude Vision анализ...")
                results["claude_analysis"] = await self.analyze_ui_with_claude(image_path, "comprehensive")
            
            results["method_used"] = "hybrid"
            results["combined_insights"] = self._combine_analyses(
                results.get("phi_analysis", ""), 
                results.get("claude_analysis", "")
            )
        
        elif strategy == "fallback":
            # Попытка с резервным вариантом
            if self.phi_agent:
                logging.info("🔄 Попытка анализа через Phi Vision...")
                phi_result = self.analyze_ui_with_phi(image_path)
                results["phi_analysis"] = phi_result
                
                # Если результат неудовлетворительный, пробуем Claude
                if self.claude_agent and self._is_poor_result(phi_result):
                    logging.info("🔄 Fallback к Claude Vision...")
                    results["claude_analysis"] = await self.analyze_ui_with_claude(image_path, "quick")
                    results["method_used"] = "fallback_to_claude"
                else:
                    results["method_used"] = "phi_only"
            elif self.claude_agent:
                logging.info("🔄 Только Claude Vision доступен...")
                results["claude_analysis"] = await self.analyze_ui_with_claude(image_path, "comprehensive")
                results["method_used"] = "claude_only"
        
        # Расчет confidence score
        results["confidence_score"] = self._calculate_confidence(results)
        
        return results
    
    def _choose_strategy(self) -> str:
        """Автоматический выбор стратегии"""
        if self.phi_agent and self.claude_agent:
            return "hybrid"
        elif self.claude_agent:
            return "claude"
        elif self.phi_agent:
            return "phi"
        else:
            return "none"
    
    def _is_poor_result(self, result: str) -> bool:
        """Проверка качества результата"""
        if not result or len(result) < 50:
            return True
        
        poor_indicators = ["error", "не удалось", "failed", "недоступен"]
        return any(indicator in result.lower() for indicator in poor_indicators)
    
    def _combine_analyses(self, phi_result: str, claude_result: str) -> Dict:
        """Объединение результатов анализа"""
        return {
            "phi_overview": phi_result[:200] + "..." if len(phi_result) > 200 else phi_result,
            "claude_detailed": claude_result[:300] + "..." if len(claude_result) > 300 else claude_result,
            "recommendation": self._generate_recommendation(phi_result, claude_result),
            "consensus_points": self._find_consensus(phi_result, claude_result)
        }
    
    def _generate_recommendation(self, phi_result: str, claude_result: str) -> str:
        """Генерация рекомендации на основе результатов"""
        if phi_result and claude_result:
            return "Используйте Claude для детальной аннотации, Phi для массовой обработки"
        elif claude_result:
            return "Используйте результат Claude для высокого качества анализа"
        elif phi_result:
            return "Используйте результат Phi для быстрого анализа"
        else:
            return "Нет доступных результатов анализа"
    
    def _find_consensus(self, phi_result: str, claude_result: str) -> List[str]:
        """Поиск консенсуса между результатами"""
        if not phi_result or not claude_result:
            return []
        
        # Простой поиск общих ключевых слов
        phi_words = set(phi_result.lower().split())
        claude_words = set(claude_result.lower().split())
        
        common_ui_terms = {
            "button", "menu", "form", "input", "text", "image", "icon", 
            "кнопка", "меню", "форма", "текст", "изображение", "иконка"
        }
        
        consensus = list((phi_words & claude_words) & common_ui_terms)
        return consensus[:5]  # Топ 5 общих терминов
    
    def _calculate_confidence(self, results: Dict) -> float:
        """Расчет уверенности в результатах"""
        method = results.get("method_used", "none")
        
        if method == "hybrid":
            return 0.95
        elif method in ["claude_only", "fallback_to_claude"]:
            return 0.90
        elif method == "phi_only":
            return 0.75
        else:
            return 0.30
    
    async def batch_ui_analysis(self, image_paths: List[str], use_smart_filtering: bool = True) -> List[Dict]:
        """Массовый анализ UI скриншотов"""
        results = []
        
        for i, image_path in enumerate(image_paths):
            logging.info(f"📸 Обрабатываю {i+1}/{len(image_paths)}: {Path(image_path).name}")
            
            try:
                if use_smart_filtering:
                    # Умная фильтрация: сначала быстрый анализ
                    result = await self.smart_ui_analysis(image_path, "fallback")
                else:
                    # Полный гибридный анализ для всех
                    result = await self.smart_ui_analysis(image_path, "hybrid")
                
                results.append(result)
                
            except Exception as e:
                logging.error(f"Ошибка обработки {image_path}: {str(e)}")
                results.append({
                    "image_path": str(image_path),
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    def save_analysis_results(self, results: Union[Dict, List[Dict]], output_dir: str = "analysis_results"):
        """Сохранение результатов анализа"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if isinstance(results, dict):
            # Одиночный результат
            filename = f"ui_analysis_{timestamp}.json"
        else:
            # Массовые результаты
            filename = f"batch_ui_analysis_{timestamp}.json"
        
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logging.info(f"💾 Результаты сохранены: {filepath}")
        return filepath
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.phi_agent:
            self.phi_agent.cleanup()
        logging.info("🧹 Гибридный агент очищен")
