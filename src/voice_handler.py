import openai
from config import OPENAI_API_KEY
from telegram import Update
from telegram.ext import CallbackContext
import io
from pydub import AudioSegment

openai.api_key = OPENAI_API_KEY

class VoiceHandler:
    def __init__(self):
        self.api_key = OPENAI_API_KEY

    def transcribe_voice_or_video(self, update: Update, context: CallbackContext):
        file_byte_array = None
        file_format = None

        if update.message.voice:
            voice_file = update.message.voice.get_file()
            file_byte_array = voice_file.download_as_bytearray()
            file_format = "ogg"
        elif update.message.video_note:
            video_file = update.message.video_note.get_file()
            file_byte_array = video_file.download_as_bytearray()
            file_format = "mp4"

        if file_byte_array:
            input_audio = io.BytesIO(file_byte_array)
            input_audio.name = f"input.{file_format}"  # Whisper требует имени файла

            # Transcribe audio or video
            transcript = openai.Audio.transcribe("whisper-1", input_audio)

            # Send transcript to user
            update.message.reply_text(transcript["text"])


