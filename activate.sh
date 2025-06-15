#!/bin/bash
echo "🚀 Активация виртуального окружения my_agent..."
cd "$(dirname "$0")/../my_agent"
source venv/bin/activate
echo "✅ Виртуальное окружение активировано"
echo "📁 Текущая директория: $(pwd)"
echo "🐍 Python версия: $(python --version)"
echo "📦 Pip версия: $(pip --version)"
echo "🔧 Переменные окружения загружены из my_ui_agent/.env"
