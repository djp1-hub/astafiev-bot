import openai
from telegram import Update
from telegram.ext import CallbackContext
import requests
from io import BytesIO
import base64



from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

class ImageDescriptionHandler:
    def __init__(self):
        self.api_key = OPENAI_API_KEY

    def get_image_description(self, image: BytesIO) -> str:
        # Преобразование изображения в base64
        image_base64 = base64.b64encode(image.getvalue()).decode('utf-8')

        # Формирование запроса к GPT-4 с использованием base64-изображения
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Опиши происходящее стиле натуралиста дикой природы Николая Дроздова. не больше 20 слов. больше юмора!"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }

        # Отправка запроса к API
        response = openai.ChatCompletion.create(**payload)

        # Извлечение и возврат описания
        description = response['choices'][0]['message']['content']
        return description

    def handle_image_message(self, update: Update, context: CallbackContext):
        # Получение файла изображения
        photo_file = update.message.photo[-1].get_file()
        file_byte_array = requests.get(photo_file.file_path).content
        image = BytesIO(file_byte_array)

        try:
            # Получение описания изображения
            description = self.get_image_description(image)
            update.message.reply_text(description)
        except Exception as e:
            update.message.reply_text(f"Error describing image: {str(e)}")
