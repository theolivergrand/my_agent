# Решение проблем с Pylance в VS Code

## Проблема
VS Code/Pylance показывает ошибки импорта Flask, хотя пакеты установлены.

## Решения

### 1. Выбор правильного интерпретатора Python
1. Откройте VS Code
2. Нажмите `Ctrl+Shift+P`
3. Введите "Python: Select Interpreter"
4. Выберите интерпретатор где установлен Flask

### 2. Проверка установки пакетов
```powershell
python -c "import flask; print('Flask установлен успешно')"
python -c "import werkzeug; print('Werkzeug установлен успешно')"
```

### 3. Перезагрузка VS Code
Иногда помогает просто перезагрузить VS Code после установки пакетов.

### 4. Настройка .vscode/settings.json
Создайте файл `.vscode/settings.json` в корне проекта:
```json
{
    "python.defaultInterpreterPath": "python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true
}
```

### 5. Создание виртуального окружения (рекомендуется)
```powershell
# Создание виртуального окружения
python -m venv .venv

# Активация (PowerShell)
.\.venv\Scripts\Activate.ps1

# Установка зависимостей
pip install -r requirements.txt
```

## Проверка работоспособности
Запустите тест:
```powershell
python test_setup.py
```

Если тест проходит успешно, значит все пакеты установлены корректно.
