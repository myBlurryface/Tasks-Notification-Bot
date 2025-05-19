# Настройка Tasks-Notification-Bot

**Tasks-Notification-Bot** — Telegram-бот для уведомлений от **Task-Manager**. Является частью проекта **Task-Manager-Project**, который включает Django-приложение **Task-Manager**.

## Требования

- Docker и Docker Compose.
- Токен Telegram-бота от [@BotFather](https://t.me/BotFather).
- Свободный порт 8443.

## Сетап

1. **Скачайте репозиторий**:
   ```bash
   git clone <your-repo-url>
   cd task-manager-project
   ```

2. **Заполните `.env`**:
   Скопируйте `env_template` в `.env` и настройте.

3**Запустите Docker Compose в Task-Manager**:
   ```bash
   docker-compose up --build -d
   ```

## Проверка

- Напишите боту `/start` в Telegram.
- Ожидаемый ответ: "Привет! Я бот, который будет напоминать тебе об активных задачах в течении 10 минут до дедлайна!".
- Логи: `docker-compose logs bot`.

## Дополнительно

- Представлена вторая версия бота, которая построена полностью на WebHook, но для такого бота нужно public HTTP, которую требует телеграм. Это неудобно для тестерования.
- Основной рабочей версией бота сейчас является polling_bot.
- Если вы хотите протестировать бота hook_bot:
   - Создайте public HTTP, например с помощью Ngrok.
   - Пропишите public HTTP в env конфигурации.
   - Измените автоматический запуск polling_bot в файле docker-compose.yaml из Task-Manager.