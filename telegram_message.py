#!/usr/bin/env python
import os

import telegram
from dotenv import load_dotenv

load_dotenv()


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def send_message(message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        return 'ok'
    except telegram.error.Unauthorized:
        return 'Unauthorized'
    except telegram.error.BadRequest:
        return 'BadRequest'
    except telegram.error.TimedOut:
        return 'TimedOut'
    except telegram.error.NetworkError:
        return 'NetworkError'
    except telegram.error.ChatMigrated:
        return 'ChatMigrated'
    except telegram.error.TelegramError:
        return 'TelegramError'
    except Exception as error:
        return error
