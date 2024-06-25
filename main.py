import re
from telegram import Update
from telegram.ext import CallbackContext, Defaults, Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from config import TOKEN
from handlers import handle_text, handle_voice_or_video, handle_image
from src.gpt_response import ChatBot

bot = ChatBot()

def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.chat_data['photo_stream'] = None
    update.message.reply_text('Привет!')

def main():
    defaults = Defaults(timeout=240)
    updater = Updater(TOKEN, use_context=True, defaults=defaults)  # use_context is important in version 13
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, lambda update, context: handle_text(update, context, bot)))  # Use Filters.text
    dp.add_handler(MessageHandler(Filters.voice | Filters.video_note, handle_voice_or_video))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
