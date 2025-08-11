import { config } from 'dotenv';
import * as process from 'process';

// Load environment variables
config();

export interface BotConfig {
  telegram: {
    token: string;
    adminUserId?: string;
    debugMode: boolean;
  };
  todoist: {
    apiToken?: string;
  };
  gmail: {
    clientId?: string;
    clientSecret?: string;
    redirectUri?: string;
  };
  paths: {
    memory: string;
    tasks: string;
    templates: string;
  };
}

export function getBotConfig(): BotConfig {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  if (!token) {
    throw new Error('TELEGRAM_BOT_TOKEN is required in .env file');
  }

  return {
    telegram: {
      token,
      adminUserId: process.env.BOT_ADMIN_USER_ID,
      debugMode: process.env.BOT_DEBUG_MODE === 'true'
    },
    todoist: {
      apiToken: process.env.TODOIST_API_TOKEN
    },
    gmail: {
      clientId: process.env.GMAIL_CLIENT_ID,
      clientSecret: process.env.GMAIL_CLIENT_SECRET,
      redirectUri: process.env.GMAIL_REDIRECT_URI
    },
    paths: {
      memory: 'memory',
      tasks: 'memory/gtd',
      templates: 'templates'
    }
  };
}

export function validateConfig(config: BotConfig): void {
  const errors: string[] = [];

  if (!config.telegram.token) {
    errors.push('TELEGRAM_BOT_TOKEN is required');
  }

  if (errors.length > 0) {
    throw new Error(`Configuration errors:\n${errors.join('\n')}`);
  }
} 