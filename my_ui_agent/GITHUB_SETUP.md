# GitHub Repository Setup Instructions

## Шаги для создания удалённого репозитория:

### 1. Создание репозитория на GitHub
1. Перейдите на https://github.com
2. Нажмите "New repository" или "+"
3. Заполните данные:
   - Repository name: `my-ui-agent` или `ui-element-analyzer`
   - Description: `Advanced UI element analyzer using hybrid methods (Vision API, classical algorithms, deep learning, AI-driven approaches)`
   - Visibility: Public или Private (на ваш выбор)
   - НЕ инициализируйте с README (у нас уже есть)
   - НЕ добавляйте .gitignore (у нас уже есть)

### 2. Подключение локального репозитория
После создания репозитория GitHub покажет инструкции. Выполните команды:

```bash
cd "c:\Users\theol\PetProj\agent-building-tool\my_ui_agent"
git remote add origin https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git
git branch -M main
git push -u origin main
```

### 3. Альтернативный способ через SSH
Если настроен SSH:
```bash
git remote add origin git@github.com:YOUR_USERNAME/REPOSITORY_NAME.git
git push -u origin main
```

## Проверка подключения
После выполнения команд проверьте:
```bash
git remote -v
git log --oneline
```

Репозиторий должен быть успешно создан и синхронизирован с GitHub!
