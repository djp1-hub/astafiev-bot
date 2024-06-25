import requests
import base64
import io
import re

import requests
from PIL import Image
from telegram import Update
from telegram.ext import CallbackContext

from config import STABLE_DIFFUSION_API_URL


class ImageHandler:
    def __init__(self):
        self.api_url = STABLE_DIFFUSION_API_URL

    def generate_image(self, prompt: str) -> bytes:
        payload = {
            "prompt": prompt,
            "negative_prompt": "((((ugly)))), (((duplicate))), ((morbid)), ((mutilated)), out of frame, extra fingers, "
                               "mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), "
                               "(((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), "
                               "((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, "
                               "(bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)),"
                               " (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers),"
                               "(((long neck)))",

            "steps": 25,
            "sampler_name": "DPM++ 2M SDE",
            "width": 768,
            "height": 1024,
            "override_settings": {
                "sd_model_checkpoint": "icbinpICantBelieveIts_newYear",

            }
        }

        response = requests.post(url=f'http://{self.api_url}:7860/sdapi/v1/txt2img', json=payload)
        r = response.json()

        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            return img_byte_arr

    def handle_image_request(self, update: Update, context: CallbackContext):
        prompt = update.message.text
        prompt = re.sub(r"\bdraw \b", "", prompt.lower())

        try:
            image_data = self.generate_image(prompt)
            update.message.reply_photo(photo=image_data)
        except Exception as e:
            update.message.reply_text(f"Error generating image: {str(e)}")
