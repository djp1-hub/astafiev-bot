from collections import defaultdict
from collections import deque
import matplotlib
import openai
from config import OPENAI_API_KEY
import re
openai.api_key = OPENAI_API_KEY


def send_html_message(chat_id, text, context):
    context.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')


matplotlib.use("Agg")

# Создаем очереди для хранения предыдущих сообщений
previous_messages = defaultdict(lambda: deque(maxlen=12))



def format_combined(text):
    """
    Format text for Telegram HTML, handling code blocks and LaTeX-like math expressions.
    - Code blocks enclosed in triple backticks are formatted within <pre> and <code> tags.
    - Math expressions enclosed in \[ and \] are formatted within <pre> tags.
    This version escapes HTML special characters to ensure the output is safe for HTML rendering.
    """
    parts = []
    in_code_block = False
    in_math_block = False
    buffer = ""
    i = 0

    while i < len(text):
        if not in_code_block and not in_math_block:
            if text[i:i + 3] == "```":
                if in_code_block:
                    parts.append(f"<pre><code>{escape_html(buffer.strip())}</code></pre>")
                    buffer = ""
                    in_code_block = False
                else:
                    if buffer:
                        parts.append(escape_html(buffer.strip()) + " ")
                        buffer = ""
                    in_code_block = True
                i += 2
            elif text[i:i + 2] == "\\[":
                if in_math_block:
                    parts.append(f"<pre>{escape_html(buffer.strip())}</pre>")
                    buffer = ""
                    in_math_block = False
                else:
                    if buffer:
                        parts.append(escape_html(buffer.strip()) + " ")
                        buffer = ""
                    in_math_block = True
                i += 1
            else:
                buffer += text[i]
        else:
            if (in_code_block and text[i:i + 3] == "```") or (in_math_block and text[i:i + 2] == "\\]"):
                if in_code_block:
                    parts.append(f"<pre><code>{escape_html(buffer.strip())}</code></pre>")
                    in_code_block = False
                if in_math_block:
                    parts.append(f"<pre>{escape_html(buffer.strip())}</pre>")
                    in_math_block = False
                buffer = ""
                i += 2 if in_math_block else 3
            else:
                buffer += text[i]
        i += 1

    # Flush the remaining buffer
    if buffer:
        parts.append(escape_html(buffer.strip()))

    return ''.join(parts)

def escape_html(text):
    """Escapes HTML special characters in a text string."""
    return (text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("'", "&#39;")
            .replace('"', "&quot;"))


def get_gpt_response(input_text, chat_id, user_id, name, context):
    # Отправляем запрос на GPT-3 API
    dict = {
        5011231443: f"Ты отвечаешь как максимально аполитичный ученый физик. в конце ответа добавляй С уважением, ваш Бацка, начинай ответ с фразы дорогой {name}",
        5150332012: f"Ты отвечаешь как опытный мужчина который повидал всякое. отвечаешь на украинской мове. в конце ответа добавляй С уважением, ваш Бацка, начинай ответ с фразы дорогой Роман Васильевич!",
        70154056: f"Ты отвечаешь как опытный мужчина татарин с политическими взглядами ульра правого толка. отвечаешь на русском. в конце ответа добавляй С уважением, ваш Бацка. исимбаева клевая? и предлагай очпочмак, начинай ответ с фразы дорогой Дмитрий Сергеевич!",
        132875045: f"Ты отвечаешь как опытный мужчина бурят с политическими взглядами ульра правого толка. отвечаешь на русском. в конце ответа добавляй С уважением, ваш Бацка и предлагай БУХЭЛЕЭР, начинай ответ с фразы дорогой Евгений Карелин!",

    }
    try:
        content = dict[user_id]
    except:
        content = f"Ты отвечаешь как опытный мужчина белорус который повидал всякое. отвечаешь на русском или белорусском. в конце ответа добавляй С уважением, ваш Бацка, начинай ответ с фразы дорогой {name}"

    messages = [{"role": "system",
                 "content": content}]
    for msg in list(previous_messages[chat_id]):
        messages.append(msg)
    messages.append({"role": "user", "content": input_text})
    try:
        response = openai.ChatCompletion.create(
            messages=messages,
            max_tokens=3000,
            model="gpt-4o",  # "gpt-3.5-turbo",
            temperature=0.1,
            presence_penalty=0.1,
            frequency_penalty=0.6,
        )
        # Получаем ответ от GPT-3 API

        message_content = response.choices[0].message['content']
        formatted_content = format_combined(message_content)
        # Добавляем ответ модели в очередь сообщений
        send_html_message(chat_id, formatted_content, context)
        return formatted_content
    except openai.error.RateLimitError as e:
        # Вывод информации о превышении лимитов
        return f"Превышен лимит запросов. Подробнее: {e}"
    except openai.error.OpenAIError as e:
        # Обработка других ошибок OpenAI
        return f"Произошла ошибка OpenAI: {e}"

    previous_messages[chat_id].append({"role": "assistant", "context": message_content})
    return formatted_content
