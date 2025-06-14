"""
Константы и таксономия UI элементов для проекта UI Analysis Agent
"""

# Mobile Gaming UI Element Taxonomy
MOBILE_GAMING_UI_TAXONOMY = {
    'interactive': [
        'button', 'action_button', 'menu_button', 'close_button', 'back_button',
        'joystick', 'virtual_joystick', 'directional_pad', 'touch_zone',
        'slider', 'toggle', 'checkbox', 'radio_button', 'dropdown', 
        'input_field', 'search_box', 'skill_button', 'attack_button'
    ],
    
    'navigational': [
        'menu', 'main_menu', 'pause_menu', 'settings_menu', 'inventory_menu',
        'tab', 'menu_tab', 'navigation_bar', 'breadcrumb', 'pagination', 
        'scroll_bar', 'home_button', 'minimap', 'compass'
    ],
    
    'informational': [
        'text_label', 'title_text', 'description_text', 'instruction_text',
        'icon', 'weapon_icon', 'item_icon', 'skill_icon', 'currency_icon',
        'image', 'logo', 'avatar', 'progress_indicator', 'health_bar', 
        'mana_bar', 'experience_bar', 'status_bar', 'notification', 
        'score_counter', 'coin_counter', 'level_indicator'
    ],
    
    'structural': [
        'panel', 'background_panel', 'card', 'list_item', 'grid_item', 
        'modal', 'popup', 'overlay', 'container', 'divider', 'frame',
        'border_frame', 'inventory_slot', 'chat_window'
    ],
    
    'gaming_specific': [
        'hud_element', 'minimap', 'health_bar', 'mana_bar', 'stamina_bar',
        'inventory_slot', 'skill_button', 'achievement_badge', 
        'leaderboard_entry', 'chat_bubble', 'quest_marker', 
        'upgrade_button', 'shop_item', 'daily_deal', 'special_offer'
    ]
}

# Создаем плоский список всех тегов для удобства
ALL_UI_TAGS = []
for category, tags in MOBILE_GAMING_UI_TAXONOMY.items():
    ALL_UI_TAGS.extend(tags)
