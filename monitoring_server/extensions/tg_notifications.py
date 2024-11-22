# This is a real example of an extension that sends notifications in Telegram with every update

from time import time
from json import load
from traceback import print_exc

from telebot import TeleBot

from .utils import extension

bot = TeleBot(token='TG BOT TOKEN')
config = {
    'group': '@supergroup',
    'topic': 1
}

status_messages = {
    'Critical': '%s не отвечает',
    'Warning': '%s',
    'Operational': '%s восстановлен',
    'Maintenance': 'На %s начаты технические работы',
}

@extension # Marks a function as an extension
def telegram_updates_notifications(event: dict) -> None: 
    if event['event'] != '/update':
        return
    bot.send_message(config['group'], status_messages[event['body'].status] % event['body'].service_name, message_thread_id=config['topic'])
