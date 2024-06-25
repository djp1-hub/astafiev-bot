import openai
from config import OPENAI_API_KEY
from telegram import Update
from telegram.ext import CallbackContext
import soundfile as sf
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
        input_audio = io.BytesIO(file_byte_array)
        data, samplerate = sf.read(input_audio, format='ogg')
        output_audio = io.BytesIO()
        sf.write(output_audio, data, samplerate, format='wav')
        output_audio.seek(0)

        # Чтение файла в бинарном режиме
        transcript = openai.Audio.transcribe("whisper-1", output_audio)

        # Отправка текста пользователю
        update.message.reply_text(transcript["text"])
