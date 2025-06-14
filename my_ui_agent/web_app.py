"""
Flask Web Application for UI Analysis
"""
import os
import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

from agent import UIAnalysisAgent
from config import Config
from constants import MOBILE_GAMING_UI_TAXONOMY

app = Flask(__name__)
app.config.from_object(Config)

# Убедимся, что папки существуют
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATASET_FOLDER'], exist_ok=True)

# Разрешенные расширения файлов - ВОССТАНОВЛЕНО
ALLOWED_EXTENSIONS = app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'})

# Инициализация UI агента
ui_agent = UIAnalysisAgent() # Удаляем глобальную инициализацию

def get_ui_taxonomy():
    """Возвращает таксономию UI элементов"""
    return MOBILE_GAMING_UI_TAXONOMY

@app.route('/')
def index():
    """Главная страница с формой загрузки"""
    return render_template('index.html', taxonomy=get_ui_taxonomy())

@app.route('/upload', methods=['POST'])
def upload_file():
    """Обработка загруженного файла"""
    if 'file' not in request.files:
        return jsonify({'error': 'Не выбран файл'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Не выбран файл'}), 400
    
    if file and allowed_file(file.filename):
        # Генерируем уникальное имя файла
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        return redirect(url_for('annotate', filename=unique_filename))
    
    return jsonify({'error': 'Недопустимый тип файла'}), 400

@app.route('/annotate/<filename>')
def annotate(filename):
    """Страница аннотации с результатами анализа"""
    session_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.json")
    
    if not os.path.exists(session_file):
        flash('Данные сессии не найдены')
        return redirect(url_for('index'))
    
    with open(session_file, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    return render_template('annotate.html', 
                         session_data=session_data, 
                         taxonomy=get_ui_taxonomy())

@app.route('/save_annotations', methods=['POST'])
def save_annotations():
    """Сохранение аннотаций пользователя"""
    data = request.get_json()
    filename = data.get('filename')
    annotations = data.get('annotations', [])
    feedback = data.get('feedback', '')
    
    if not filename:
        return jsonify({'error': 'Не указан файл'}), 400
    
    session_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.json")
    
    if not os.path.exists(session_file):
        return jsonify({'error': 'Данные сессии не найдены'}), 404
    
    # Загружаем существующие данные
    with open(session_file, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    # Обновляем аннотации
    session_data['user_annotations'] = annotations
    session_data['user_feedback'] = feedback
    session_data['annotation_timestamp'] = datetime.datetime.now().isoformat()
    
    # Сохраняем обновленные данные
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    # Сохраняем в финальный датасет
    try:
        save_to_dataset(session_data)
        
        # Очищаем временные файлы
        cleanup_session_files(filename)
        
        return jsonify({'success': True, 'message': 'Аннотации сохранены в датасет'})
    except Exception as e:
        return jsonify({'error': f'Ошибка при сохранении: {str(e)}'}), 500

def save_to_dataset(session_data):
    """Сохраняет данные в финальный датасет"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    entry_folder = os.path.join('training_dataset', f'entry_{timestamp}')
    os.makedirs(entry_folder, exist_ok=True)
      # Копируем изображение
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], session_data['filename'])
    final_image_path = os.path.join(entry_folder, session_data['original_filename'])
    
    shutil.copy2(original_path, final_image_path)
    
    # Создаем финальный JSON с данными
    final_data = {
        'image_filename': session_data['original_filename'],
        'analysis_timestamp': session_data['timestamp'],
        'annotation_timestamp': session_data['annotation_timestamp'],
        'vision_api_results': session_data['analysis_result'],
        'user_annotations': session_data['user_annotations'],
        'user_feedback': session_data['user_feedback'],
        'taxonomy_version': 'mobile_gaming_v1',
        'web_interface_version': '1.0'
    }
    
    # Сохраняем JSON
    json_path = os.path.join(entry_folder, 'data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

def cleanup_session_files(filename):
    """Очищает временные файлы сессии"""
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.json"))
    except OSError:
        pass  # Файлы могут уже быть удалены

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Отдача загруженных файлов"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/dataset')
def dataset_overview():
    """Обзор созданного датасета"""
    entries = []
    
    for entry_dir in app.config['TRAINING_DATASET_FOLDER'].iterdir():
        if entry_dir.is_dir() and entry_dir.name.startswith('entry_'):
            annotation_file = entry_dir / "annotations.json"
            if annotation_file.exists():
                try:
                    with open(annotation_file, 'r', encoding='utf-8') as f:
                        annotations = json.load(f)
                    entries.append({
                        'id': entry_dir.name,
                        'timestamp': annotations.get('timestamp', ''),
                        'elements_count': len(annotations.get('annotations', [])),
                        'has_image': (entry_dir / "image.png").exists()
                    })
                except:
                    pass  # Пропускаем поврежденные записи
    
    # Сортируем по времени (новые сначала)
    entries.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return render_template('dataset.html', entries=entries)

@app.route('/api/taxonomy')
def api_taxonomy():
    """API endpoint для получения таксономии"""
    return jsonify(get_ui_taxonomy())

def allowed_file(filename):
    """Проверяет, разрешен ли тип файла"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
