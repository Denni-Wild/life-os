# 🚀 Быстрый старт Life OS

## 1. Настройка Telegram бота

### 1.1 Создание бота
1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте `/newbot`
3. Введите имя и username для бота
4. Сохраните полученный токен

### 1.2 Получение User ID
1. Найдите [@userinfobot](https://t.me/userinfobot) в Telegram
2. Отправьте любое сообщение
3. Скопируйте ваш User ID

### 1.3 Настройка Todoist (опционально)
1. Войдите в [Todoist](https://todoist.com)
2. Перейдите в Settings → Integrations → Developer
3. Скопируйте API Token

## 2. Создание конфигурационного файла

Создайте файл `.env` в корне проекта:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Todoist Configuration (опционально)
TODOIST_API_TOKEN=your_todoist_api_token_here

# Bot Settings
BOT_ADMIN_USER_ID=your_telegram_user_id_here
BOT_DEBUG_MODE=false
```

## 3. Установка зависимостей

```bash
# Python зависимости
pip install -r requirements.txt

# Node.js зависимости (для дополнительных скриптов)
npm install
```

## 4. Запуск бота

```bash
# Запуск бота
python run_bot.py

# Или через npm
npm run bot
```

## 5. Тестирование

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Попробуйте команды:
   - `/help` - справка
   - `/capture Тестовая задача` - захват задачи
   - `/tasks` - просмотр задач

## 6. Структура системы

```
life-os/
├── bot/                    # Python Telegram бот
├── scripts/                # TypeScript скрипты
├── memory/                 # GTD система
│   ├── gtd/               # Задачи и проекты
│   ├── assessments/       # Оценки жизни
│   ├── objectives/        # Цели и OKR
│   └── reference/         # Справочные материалы
├── templates/             # Шаблоны
└── .env                   # Конфигурация
```

## 7. Основные команды

### Telegram бот
- `/start` - запуск бота
- `/capture` - быстрый захват
- `/tasks` - задачи на сегодня
- `/status` - статус жизненных областей
- `/review` - ежедневный обзор
- `/assess` - оценка жизни

### NPM скрипты
- `npm run bot` - запуск бота
- `npm run bot:dev` - запуск бота в режиме разработки
- `npm run todoist` - просмотр задач Todoist
- `npm run todoist:import` - импорт задач из Todoist
- `npm run todoist:export` - экспорт задач в Todoist
- `npm run gmail` - чтение email
- `npm run watch` - мониторинг изменений

## 8. Следующие шаги

1. **Настройте регулярные обзоры**:
   - Ежедневно: обработка inbox
   - Еженедельно: обзор проектов
   - Ежемесячно: оценка прогресса

2. **Интегрируйте с внешними сервисами**:
   - Google Calendar
   - Notion
   - Obsidian

3. **Настройте автоматизацию**:
   - Автоматические напоминания
   - Синхронизация данных
   - Экспорт отчетов

## 🆘 Поддержка

Если возникли проблемы:
1. Проверьте правильность токенов в `.env`
2. Убедитесь, что все зависимости установлены
3. Проверьте логи в консоли
4. Обратитесь к документации в папке `docs/`

Удачного использования! 🚀 