# UI Analysis Agent Configuration
# Configuration file for mobile gaming UI taxonomy and settings

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

# Analysis settings
ANALYSIS_SETTINGS = {
    'min_element_area': 100,
    'max_element_area': 50000,
    'button_aspect_ratio_range': (0.3, 5.0),
    'input_field_aspect_ratio_min': 2.0,
    'icon_area_threshold': 10000,
    'default_text_confidence': 0.8
}

# Dataset settings
DATASET_SETTINGS = {
    'output_dir': 'training_dataset',
    'learning_data_dir': 'learning_data',
    'annotation_formats': ['yolo', 'coco', 'json'],
    'backup_original_images': True
}

# UI Keywords for classification
UI_KEYWORDS = {
    'action_buttons': ['start', 'play', 'begin', 'continue', 'resume', 'go', 'launch'],
    'menu_buttons': ['menu', 'options', 'settings', 'config', 'preferences'],
    'close_buttons': ['close', 'exit', 'quit', 'cancel', 'dismiss', 'back'],
    'navigation_buttons': ['next', 'previous', 'forward', 'back', 'return'],
    'shop_buttons': ['buy', 'purchase', 'shop', 'store', 'market'],
    'inventory_buttons': ['inventory', 'items', 'equipment', 'gear'],
    'health_indicators': ['health', 'hp', 'life', 'hearts'],
    'mana_indicators': ['mana', 'mp', 'magic', 'energy'],
    'experience_indicators': ['experience', 'exp', 'xp', 'level']
}
