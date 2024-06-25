import re
from src.gpt_response import ChatBot  # Импортируем новый класс ChatBot
from telegram import Update
from telegram.ext import CallbackContext, Defaults, Updater, CommandHandler, MessageHandler, Filters
from config import TOKEN
from src.weather import WeatherBot
from src.voice_handler import VoiceHandler

# Создаем экземпляр класса ChatBot
bot = ChatBot()
weather_bot = WeatherBot()
voice_handler = VoiceHandler()


def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.chat_data['photo_stream'] = None
    update.message.reply_text('Привет!')

def handle_text(update: Update, context: CallbackContext, bot_instance):
    chat_id = update.message.chat_id
    message = update.message.text
    user = update.effective_user  # Получаем объект пользователя
    user_id = user.id
    name = user.full_name  # Имя пользователя
    if "зябь" in message.lower():
        weather_bot.weather(update, context)
    else:
        bot_instance.previous_messages[chat_id].append({"role": "user", "content": message})
        if "поясни" in message.lower():
            message = re.sub(r"\bпоясни \b", "", message.lower())
            bot_instance.get_gpt_response(message, chat_id, user_id, name, context)


def handle_voice_or_video(update: Update, context: CallbackContext):
    voice_handler.transcribe_voice_or_video(update, context)

def main():
    defaults = Defaults(timeout=240)
    updater = Updater(TOKEN, use_context=True, defaults=defaults)  # use_context is important in version 13
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, lambda update, context: handle_text(update, context, bot)))  # Use Filters.text
    dp.add_handler(MessageHandler(Filters.voice | Filters.video_note, handle_voice_or_video))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
