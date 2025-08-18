# 🚀 Развертывание Life OS Bot

## 🎯 Обзор развертывания

**Life OS Bot** можно развернуть на различных платформах для обеспечения стабильной работы:

- **🖥️ Локальный сервер** - для разработки и тестирования
- **☁️ Облачные платформы** - для продакшена
- **📱 VPS/Хостинг** - для полного контроля
- **🔄 CI/CD** - для автоматического обновления

## 🖥️ Локальное развертывание

### **Требования к системе**

#### **Операционная система:**
- **Windows 10/11** (рекомендуется)
- **macOS 10.15+** (Catalina и новее)
- **Linux** (Ubuntu 18.04+, CentOS 7+)

#### **Программное обеспечение:**
- **Python 3.7+** (рекомендуется 3.9+)
- **pip** (менеджер пакетов Python)
- **Git** (для управления версиями)

### **Пошаговая установка**

#### **Шаг 1: Подготовка системы**

1. **Установите Python:**
   ```bash
   # Windows: Скачайте с python.org
   # macOS: brew install python
   # Linux: sudo apt install python3 python3-pip
   ```

2. **Проверьте установку:**
   ```bash
   python --version  # Должно быть 3.7+
   pip --version
   ```

#### **Шаг 2: Клонирование проекта**

1. **Склонируйте репозиторий:**
   ```bash
   git clone https://github.com/your-username/life-os.git
   cd life-os
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

#### **Шаг 3: Установка зависимостей**

1. **Обновите pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

#### **Шаг 4: Настройка окружения**

1. **Скопируйте шаблон:**
   ```bash
   cp docs/env.example .env
   ```

2. **Отредактируйте .env:**
   ```bash
   # Telegram Bot
   TELEGRAM_BOT_TOKEN=ваш_токен_бота
   
   # Todoist (опционально)
   TODOIST_API_TOKEN=ваш_токен_todoist
   
   # Логирование
   LOG_LEVEL=INFO
   ```

#### **Шаг 5: Запуск бота**

1. **Запустите бота:**
   ```bash
   python run_bot.py
   ```

2. **Проверьте логи:**
   ```
   🤖 Life OS Bot запущен...
   Обработчики настроены
   Команды бота настроены
   ```

## ☁️ Облачное развертывание

### **Heroku**

#### **Преимущества:**
- ✅ Простота развертывания
- ✅ Автоматическое масштабирование
- ✅ Интеграция с Git
- ✅ Бесплатный план

#### **Развертывание:**

1. **Создайте аккаунт на Heroku**

2. **Установите Heroku CLI:**
   ```bash
   # Windows: Скачайте установщик
   # macOS: brew install heroku
   # Linux: sudo snap install heroku --classic
   ```

3. **Войдите в аккаунт:**
   ```bash
   heroku login
   ```

4. **Создайте приложение:**
   ```bash
   heroku create your-life-os-bot
   ```

5. **Настройте переменные окружения:**
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=ваш_токен
   heroku config:set TODOIST_API_TOKEN=ваш_токен
   heroku config:set LOG_LEVEL=INFO
   ```

6. **Разверните приложение:**
   ```bash
   git push heroku main
   ```

7. **Запустите бота:**
   ```bash
   heroku ps:scale worker=1
   ```

#### **Файлы для Heroku:**

1. **Procfile:**
   ```
   worker: python run_bot.py
   ```

2. **runtime.txt:**
   ```
   python-3.9.18
   ```

3. **requirements.txt** (уже есть)

### **Railway**

#### **Преимущества:**
- ✅ Простота использования
- ✅ Автоматическое развертывание
- ✅ Хорошая производительность
- ✅ Разумные цены

#### **Развертывание:**

1. **Подключите GitHub репозиторий**

2. **Настройте переменные окружения:**
   - `TELEGRAM_BOT_TOKEN`
   - `TODOIST_API_TOKEN`
   - `LOG_LEVEL`

3. **Автоматическое развертывание**

### **Render**

#### **Преимущества:**
- ✅ Бесплатный план
- ✅ Простота настройки
- ✅ Автоматическое развертывание
- ✅ Хорошая документация

#### **Развертывание:**

1. **Создайте Web Service**

2. **Подключите GitHub репозиторий**

3. **Настройте переменные окружения**

4. **Укажите команду запуска:**
   ```
   python run_bot.py
   ```

## 📱 VPS/Хостинг развертывание

### **DigitalOcean Droplet**

#### **Создание сервера:**

1. **Создайте Droplet:**
   - **OS**: Ubuntu 20.04 LTS
   - **Size**: Basic (1GB RAM, 1 CPU)
   - **Region**: Ближайший к вам

2. **Подключитесь по SSH:**
   ```bash
   ssh root@your-server-ip
   ```

3. **Обновите систему:**
   ```bash
   apt update && apt upgrade -y
   ```

4. **Установите Python:**
   ```bash
   apt install python3 python3-pip python3-venv -y
   ```

5. **Создайте пользователя:**
   ```bash
   adduser lifeos
   usermod -aG sudo lifeos
   ```

#### **Установка бота:**

1. **Переключитесь на пользователя:**
   ```bash
   su - lifeos
   ```

2. **Клонируйте проект:**
   ```bash
   git clone https://github.com/your-username/life-os.git
   cd life-os
   ```

3. **Создайте виртуальное окружение:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Настройте .env файл:**
   ```bash
   cp docs/env.example .env
   nano .env  # Отредактируйте переменные
   ```

### **Systemd сервис**

#### **Создание сервиса:**

1. **Создайте файл сервиса:**
   ```bash
   sudo nano /etc/systemd/system/lifeos-bot.service
   ```

2. **Добавьте содержимое:**
   ```ini
   [Unit]
   Description=Life OS Bot
   After=network.target
   
   [Service]
   Type=simple
   User=lifeos
   WorkingDirectory=/home/lifeos/life-os
   Environment=PATH=/home/lifeos/life-os/venv/bin
   ExecStart=/home/lifeos/life-os/venv/bin/python run_bot.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Активируйте сервис:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable lifeos-bot
   sudo systemctl start lifeos-bot
   ```

4. **Проверьте статус:**
   ```bash
   sudo systemctl status lifeos-bot
   ```

### **Nginx (опционально)**

#### **Для веб-интерфейса:**

1. **Установите Nginx:**
   ```bash
   sudo apt install nginx -y
   ```

2. **Настройте конфигурацию:**
   ```bash
   sudo nano /etc/nginx/sites-available/lifeos-bot
   ```

3. **Добавьте конфигурацию:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Активируйте сайт:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/lifeos-bot /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## 🔄 CI/CD развертывание

### **GitHub Actions**

#### **Автоматическое развертывание:**

1. **Создайте .github/workflows/deploy.yml:**
   ```yaml
   name: Deploy Life OS Bot
   
   on:
     push:
       branches: [ main ]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       
       steps:
       - uses: actions/checkout@v2
       
       - name: Deploy to Heroku
         uses: akhileshns/heroku-deploy@v3.12.14
         with:
           heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
           heroku_app_name: ${{ secrets.HEROKU_APP_NAME }}
           heroku_email: ${{ secrets.HEROKU_EMAIL }}
   ```

2. **Настройте секреты в GitHub:**
   - `HEROKU_API_KEY`
   - `HEROKU_APP_NAME`
   - `HEROKU_EMAIL`

### **Docker развертывание**

#### **Создание Dockerfile:**

1. **Создайте Dockerfile:**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   CMD ["python", "run_bot.py"]
   ```

2. **Создайте docker-compose.yml:**
   ```yaml
   version: '3.8'
   
   services:
     lifeos-bot:
       build: .
       environment:
         - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
         - TODOIST_API_TOKEN=${TODOIST_API_TOKEN}
         - LOG_LEVEL=${LOG_LEVEL}
       restart: unless-stopped
   ```

3. **Запустите контейнер:**
   ```bash
   docker-compose up -d
   ```

## 📊 Мониторинг и логирование

### **Логирование**

#### **Настройка логов:**

1. **Файловое логирование:**
   ```python
   # В logger.py
   import logging
   from logging.handlers import RotatingFileHandler
   
   handler = RotatingFileHandler('bot.log', maxBytes=1024*1024, backupCount=5)
   ```

2. **Системное логирование:**
   ```bash
   # В systemd сервисе
   StandardOutput=journal
   StandardError=journal
   ```

### **Мониторинг**

#### **Проверка состояния:**

1. **Статус сервиса:**
   ```bash
   sudo systemctl status lifeos-bot
   ```

2. **Логи в реальном времени:**
   ```bash
   sudo journalctl -u lifeos-bot -f
   ```

3. **Использование ресурсов:**
   ```bash
   htop
   df -h
   free -h
   ```

## 🔒 Безопасность

### **Основные меры:**

1. **Firewall:**
   ```bash
   sudo ufw enable
   sudo ufw allow ssh
   sudo ufw allow 80
   sudo ufw allow 443
   ```

2. **SSH безопасность:**
   ```bash
   # Отключите root логин
   # Используйте ключи вместо паролей
   # Измените порт SSH
   ```

3. **Регулярные обновления:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

## 📈 Масштабирование

### **Горизонтальное масштабирование:**

1. **Несколько экземпляров бота**
2. **Балансировщик нагрузки**
3. **Общая база данных**

### **Вертикальное масштабирование:**

1. **Увеличение ресурсов сервера**
2. **Оптимизация кода**
3. **Кэширование данных**

---

**🎯 Выберите подходящий способ развертывания в зависимости от ваших потребностей!**

*От простого локального запуска до профессионального облачного развертывания.* 