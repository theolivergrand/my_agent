# Конфигурация для GitHub исследователя
# Этот файл содержит настройки для GitHub MCP Server интеграции

# GitHub Personal Access Token
# Для получения токена:
# 1. Перейдите на https://github.com/settings/tokens
# 2. Нажмите "Generate new token (classic)"
# 3. Выберите scopes: public_repo, read:user
# 4. Скопируйте токен и вставьте ниже

# ВНИМАНИЕ: Не коммитьте этот файл с реальным токеном!
GITHUB_TOKEN = "your_github_token_here"

# Альтернативно, установите переменную окружения:
# set GITHUB_TOKEN=your_token_here  # Windows
# export GITHUB_TOKEN=your_token_here  # Linux/Mac

# Настройки поиска
SEARCH_CONFIG = {
    "max_results_per_query": 10,
    "min_stars": 3,
    "preferred_languages": ["Python", "JavaScript", "C++"],
    "search_delay": 1,  # секунды между запросами
}

# Ключевые слова для поиска
UI_KEYWORDS = [
    "ui", "gui", "interface", "element", "detection", "automation",
    "screenshot", "ocr", "vision", "computer", "machine", "learning",
    "selenium", "playwright", "opencv", "testing", "scraping",
    "annotation", "bounding", "box", "recognition", "analysis"
]

# Поисковые запросы
SEARCH_QUERIES = [
    "UI element detection computer vision language:python stars:>10",
    "GUI automation element detection screenshot stars:>5",
    "web scraping element detection python stars:>20",
    "screenshot OCR element extraction python stars:>15",
    "text detection UI automation stars:>10",
    "UI analysis machine learning python stars:>10",
    "interface detection deep learning stars:>5",
    "selenium element detection python stars:>25",
    "playwright element detection stars:>15",
    "opencv UI detection python stars:>10",
    "UI testing automation detection python stars:>20",
    "GUI testing element finder stars:>10",
    "screenshot annotation tool python stars:>5",
    "UI element annotation machine learning stars:>3"
]
