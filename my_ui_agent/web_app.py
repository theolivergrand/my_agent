import os
import json
import datetime
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import uuid
from agent import UIAnalysisAgent
from constants import MOBILE_GAMING_UI_TAXONOMY

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Создаем папки если они не существуют
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('training_dataset', exist_ok=True)

# Инициализация UI агента
ui_agent = UIAnalysisAgent()

def allowed_file(filename):
    """Проверяет, разрешен ли тип файла"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_ui_taxonomy():
    """Возвращает структурированную таксономию UI элементов"""
    return MOBILE_GAMING_UI_TAXONOMY

@app.route('/')
def index():
    """Главная страница с формой загрузки"""
    return render_template('index.html', taxonomy=get_ui_taxonomy())

@app.route('/upload', methods=['POST'])
def upload_file():
    """Обработка загруженного файла"""
    if 'file' not in request.files:
        flash('Не выбран файл')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Не выбран файл')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Генерируем уникальное имя файла
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Анализируем изображение
        try:
            analysis_result = ui_agent.analyze_image(filepath)
            
            # Сохраняем результат в сессию для дальнейшего использования
            session_data = {
                'filename': unique_filename,
                'original_filename': original_filename,
                'analysis_result': analysis_result,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            # Сохраняем во временный файл
            session_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_filename}.json")
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            return redirect(url_for('annotate', filename=unique_filename))
            
        except Exception as e:
            flash(f'Ошибка при анализе изображения: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Недопустимый тип файла')
    return redirect(url_for('index'))

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
    dataset_entries = []
    training_path = Path('training_dataset')
    
    if training_path.exists():
        for entry_dir in training_path.iterdir():
            if entry_dir.is_dir():
                json_file = entry_dir / 'data.json'
                if json_file.exists():
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            dataset_entries.append({
                                'entry_name': entry_dir.name,
                                'image_filename': data.get('image_filename'),
                                'timestamp': data.get('annotation_timestamp'),
                                'annotations_count': len(data.get('user_annotations', [])),
                                'feedback': data.get('user_feedback', '')
                            })
                    except Exception as e:
                        print(f"Ошибка чтения {json_file}: {e}")
    
    return render_template('dataset.html', entries=dataset_entries)

@app.route('/api/taxonomy')
def api_taxonomy():
    """API endpoint для получения таксономии"""
    return jsonify(get_ui_taxonomy())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
