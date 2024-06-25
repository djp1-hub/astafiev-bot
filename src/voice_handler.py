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

    def transcribe_voice(self, update: Update, context: CallbackContext):
        # Получение файла голосового сообщения
        voice_file = update.message.voice.get_file()
        file_byte_array = voice_file.download_as_bytearray()

        # Преобразование ogg в wav в памяти
        ogg_audio = AudioSegment.from_ogg(io.BytesIO(file_byte_array))
        wav_io = io.BytesIO()
        ogg_audio.export(wav_io, format="wav")
        wav_io.seek(0)
        wav_io.name = "voice_message.wav"

        # Чтение файла в бинарном режиме
        transcript = openai.Audio.transcribe("whisper-1", wav_io)

        # Отправка текста пользователю
        update.message.reply_text(transcript["text"])
