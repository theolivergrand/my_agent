@echo off
echo ====================================================
echo UI Dataset Web Application - Startup Script
echo ====================================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден в PATH
    echo    Установите Python и добавьте его в PATH
    pause
    exit /b 1
)

echo ✅ Python найден
echo.

REM Проверяем наличие файлов
if not exist "web_app.py" (
    echo ❌ Файл web_app.py не найден
    echo    Убедитесь, что вы находитесь в правильной директории
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ Файл requirements.txt не найден
    pause
    exit /b 1
)

echo ✅ Файлы приложения найдены
echo.

REM Создаем необходимые директории
if not exist "uploads" mkdir uploads
if not exist "training_dataset" mkdir training_dataset
if not exist "static" mkdir static

echo ✅ Директории созданы
echo.

REM Предлагаем установить зависимости
echo 📦 Проверяем зависимости...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Flask не установлен. Установить зависимости? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        echo 🔄 Устанавливаем зависимости...
        pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo ❌ Ошибка установки зависимостей
            pause
            exit /b 1
        )
        echo ✅ Зависимости установлены
    ) else (
        echo ⚠️  Зависимости не установлены. Приложение может не работать.
    )
)

echo.
echo 🚀 Запускаем веб-приложение...
echo.
echo 🌐 Откройте браузер и перейдите по адресу:
echo    http://localhost:5000
echo.
echo 🛑 Для остановки нажмите Ctrl+C
echo.
echo ====================================================

REM Запускаем приложение
python web_app.py

echo.
echo 👋 Приложение остановлено
pause
