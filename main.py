import re
from src.gpt_response import get_gpt_response
from telegram import Update
from telegram.ext import CallbackContext, Defaults, Updater
from telegram.ext import CommandHandler, MessageHandler, Filters
from collections import defaultdict
from config import  TOKEN
from src.weather import weather
from collections import deque

previous_messages = defaultdict(lambda: deque(maxlen=12))
def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.chat_data['photo_stream'] = None
    update.message.reply_text(
        'Привет!',
    )


def handle_text(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    message = update.message.text
    user = update.effective_user  # Получаем объект пользователя
    user_id = user.id
    name = user.full_name  # Имя пользователя
    if "зябь" in message.lower():
        weather(update, context)
    else:
        previous_messages[chat_id].append({"role": "user", "content": message})
        if "поясни" in message.lower():
            message = re.sub(r"\bпоясни \b", "", message.lower())
            get_gpt_response(message, chat_id, user_id, name, context)


def main():
    defaults = Defaults(timeout=240)
    updater = Updater(TOKEN, use_context=True, defaults=defaults)  # use_context is important in version 13
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))  # Use Filters.text

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
