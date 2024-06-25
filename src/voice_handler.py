import openai
from config import OPENAI_API_KEY
from telegram import Update
from telegram.ext import CallbackContext
from pydub import AudioSegment
import io

openai.api_key = OPENAI_API_KEY

class VoiceHandler:
    def __init__(self):
        self.api_key = OPENAI_API_KEY

    def transcribe_voice_or_video(self, update: Update, context: CallbackContext):
        # Определение типа сообщения
        if update.message.voice:
            file = update.message.voice.get_file()
        elif update.message.video_note:
            file = update.message.video_note.get_file()
        else:
            update.message.reply_text("Не удалось обработать сообщение.")
            return

        file_byte_array = file.download_as_bytearray()

        # Преобразование ogg в wav в памяти
        ogg_audio = AudioSegment.from_ogg(io.BytesIO(file_byte_array))
        wav_io = io.BytesIO()
        ogg_audio.export(wav_io, format="wav")
        wav_io.seek(0)

        # Установка имени файла для BytesIO
        wav_io.name = "voice_message.wav"

        # Чтение файла в бинарном режиме
        transcript = openai.Audio.transcribe("whisper-1", wav_io)

        # Отправка текста пользователю
        update.message.reply_text(transcript["text"])
