# Scripts

This directory contains configuration files and credentials for external services.

## Files

- `credentials.json` - Google API credentials (download from Google Cloud Console)
- `token.json` - Gmail API access token (created automatically)
- `telegram-bot-config.ts` - Telegram bot configuration template

## Setup

### Gmail API Setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth2 credentials
4. Download `credentials.json` to this directory

### Usage

All functionality has been migrated to Python services in `bot/services/`:

- Gmail integration: `python -m bot.services.gmail_service`
- Todoist integration: `python -m bot.services.todoist_service`
- System monitoring: `python -m bot.services.watch_service`

## Migration Notice

TypeScript scripts have been migrated to Python for better integration and maintainability. See `MIGRATION-TO-PYTHON.md` for details.

## NPM Commands

```bash
# Bot commands
npm run bot              # Start bot
npm run bot:dev          # Start bot in development mode

# Service commands
npm run gmail            # Read emails
npm run todoist          # View Todoist tasks
npm run todoist:import   # Import tasks from Todoist
npm run todoist:export   # Export tasks to Todoist
npm run watch            # Monitor system
```

## Environment Variables

Required in `.env` file:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
BOT_ADMIN_USER_ID=your_telegram_user_id_here

# Todoist (optional)
TODOIST_API_TOKEN=your_todoist_api_token_here

# Gmail (optional)
GMAIL_CLIENT_ID=your_gmail_client_id_here
GMAIL_CLIENT_SECRET=your_gmail_client_secret_here
```
