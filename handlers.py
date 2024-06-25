from src.voice_handler import VoiceHandler
from src.image_handler import ImageHandler
from src.describe_handler import ImageDescriptionHandler
from src.weather import WeatherBot
from src.gpt_response import ChatBot
from telegram import Update
from telegram.ext import CallbackContext, Defaults, Updater, CommandHandler, MessageHandler, Filters
import re



# Создаем экземпляр класса ChatBot
bot = ChatBot()
weather_bot = WeatherBot()
voice_handler = VoiceHandler()
image_handler = ImageHandler()
image_description_handler = ImageDescriptionHandler()


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
        elif "draw" in message.lower():
            image_handler.handle_image_request(update, context)


def handle_voice_or_video(update: Update, context: CallbackContext):
    voice_handler.transcribe_voice_or_video(update, context)

def handle_image(update: Update, context: CallbackContext):
    image_description_handler.handle_image_message(update, context)

