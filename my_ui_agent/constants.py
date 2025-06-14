"""
Константы и таксономия UI элементов для проекта UI Analysis Agent
"""

# Mobile Gaming UI Element Taxonomy - 82 тега в 5 категориях
MOBILE_GAMING_UI_TAXONOMY = {
    "interactive": [
        "button", "icon_button", "toggle_button", "radio_button", "checkbox",
        "slider", "joystick", "touch_area", "drag_handle", "input_field",
        "search_box", "dropdown", "picker", "stepper", "switch",
        "tap_zone", "gesture_area", "scroll_handle", "resize_handle",
        "action_button", "menu_button", "close_button", "back_button",
        "forward_button", "play_button", "pause_button", "stop_button",
        "record_button", "settings_button", "help_button", "info_button"
    ],
    "navigational": [
        "menu", "navigation_bar", "tab_bar", "breadcrumb", "pagination",
        "sidebar", "drawer", "bottom_sheet", "toolbar", "header",
        "footer", "minimap", "level_selector", "chapter_nav", "world_map"
    ],
    "informational": [
        "text_label", "title", "subtitle", "description", "caption",
        "badge", "notification", "alert", "tooltip", "status_indicator",
        "progress_bar", "loading_spinner", "health_bar", "mana_bar",
        "experience_bar", "score_display", "timer", "counter", "level_indicator"
    ],
    "structural": [
        "panel", "card", "container", "frame", "border", "divider",
        "separator", "modal", "dialog", "popup", "overlay", "mask",
        "background", "layout_grid", "list_container", "scroll_view"
    ],
    "gaming_specific": [
        "hud_element", "inventory_slot", "character_portrait", "skill_icon",
        "weapon_slot", "armor_slot", "spell_icon", "achievement_badge",
        "quest_indicator", "map_marker", "resource_counter", "energy_meter",
        "cooldown_timer", "buff_icon", "debuff_icon", "chat_bubble"
    ]
}

# Конфигурация анализа
ANALYSIS_CONFIG = {
    "supported_formats": ["png", "jpg", "jpeg", "gif", "bmp", "webp"],
    "max_file_size": 16 * 1024 * 1024,  # 16MB
    "confidence_threshold": 0.5,
    "min_element_size": 10,  # минимальный размер элемента интерфейса в пикселях
}

# Цветовые схемы для визуализации
UI_COLORS = {
    "text": "#00FF00",           # Зеленый для текста
    "buttons": "#FF0000",       # Красный для интерактивных элементов
    "containers": "#0000FF",    # Синий для структурных элементов
    "navigation": "#FFFF00",    # Желтый для навигации
    "gaming": "#FF00FF"         # Пурпурный для игровых элементов
}

# Создаем плоский список всех тегов для удобства
ALL_UI_TAGS = []
for category, tags in MOBILE_GAMING_UI_TAXONOMY.items():
    ALL_UI_TAGS.extend(tags)
