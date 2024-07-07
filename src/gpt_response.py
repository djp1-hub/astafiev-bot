from collections import defaultdict, deque
import matplotlib
import openai
from config import OPENAI_API_KEY
import re

openai.api_key = OPENAI_API_KEY

matplotlib.use("Agg")

class ChatBot:
    def __init__(self):
        self.previous_messages = defaultdict(lambda: deque(maxlen=12))

    def send_html_message(self, chat_id, text, context):
        context.bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')

    def escape_html(self, text):
        """Escapes HTML special characters in a text string."""
        return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("'", "&#39;")
                .replace('"', "&quot;"))

    def format_combined(self, text):
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
                        parts.append(f"<pre><code>{self.escape_html(buffer.strip())}</code></pre>")
                        buffer = ""
                        in_code_block = False
                    else:
                        if buffer:
                            parts.append(self.escape_html(buffer.strip()) + " ")
                            buffer = ""
                        in_code_block = True
                    i += 2
                elif text[i:i + 2] == "\\[":
                    if in_math_block:
                        parts.append(f"<pre>{self.escape_html(buffer.strip())}</pre>")
                        buffer = ""
                        in_math_block = False
                    else:
                        if buffer:
                            parts.append(self.escape_html(buffer.strip()) + " ")
                            buffer = ""
                        in_math_block = True
                    i += 1
                else:
                    buffer += text[i]
            else:
                if (in_code_block and text[i:i + 3] == "```") or (in_math_block and text[i:i + 2] == "\\]"):
                    if in_code_block:
                        parts.append(f"<pre><code>{self.escape_html(buffer.strip())}</code></pre>")
                        in_code_block = False
                    if in_math_block:
                        parts.append(f"<pre>{self.escape_html(buffer.strip())}</pre>")
                        in_math_block = False
                    buffer = ""
                    i += 2 if in_math_block else 3
                else:
                    buffer += text[i]
            i += 1

        # Flush the remaining buffer
        if buffer:
            parts.append(self.escape_html(buffer.strip()))

        return ''.join(parts)

    def get_gpt_response(self, input_text, chat_id, user_id, name, context):
        # Отправляем запрос на GPT-3 API
        response_patterns = {
            5011231443: f"Ты отвечаешь как максимально аполитичный ученый физик. в конце ответа добавляй С уважением, ваш Бацка, начинай ответ с фразы дорогой {name}",
            5150332012: f"Ты отвечаешь как опытный мужчина который повидал всякое. отвечаешь на украинской мове. в конце ответа добавляй С уважением, ваш Бацка, начинай ответ с фразы дорогой Роман Васильевич!",
            70154056: f"Ты отвечаешь как опытный мужчина татарин с политическими взглядами ультра правого толка. отвечаешь на русском. в конце ответа добавляй С уважением, ваш Бацка. исимбаева клевая? и предлагай очпочмак, начинай ответ с фразы дорогой Дмитрий Сергеевич!",
            132875045: f"Ты отвечаешь как опытный мужчина бурят с политическими взглядами ультра правого толка. отвечаешь на русском. в конце ответа добавляй С уважением, ваш Бацка и предлагай БУХЭЛЕЭР, начинай ответ с фразы дорогой Евгений Карелин!",
        }

        content = response_patterns.get(user_id, f"Отвечать в стиле Виктора Астафьева, известного своими произведениями о жизни русской деревни, природе и человеческой справедливости. Используйте язык, который отражает богатство и точность русского языка, характерные для его стиля. Астафьев часто включал в свои тексты детальные описания природы и сельской жизни, выражая глубокую эмоциональную связь с темами, затрагиваемыми в его работах. В ответах следует поддерживать тон, который сочетает философскую глубину и острое чувство моральной ответственности перед лицом трудностей и неправды. начинай предожение с фразы дорогой {name}")

        messages = [{"role": "system", "content": content}]
        messages.extend(list(self.previous_messages[chat_id]))
        messages.append({"role": "user", "content": input_text})

        try:
            response = openai.ChatCompletion.create(
                messages=messages,
                max_tokens=3000,
                model="gpt-4o",
                temperature=0.1,
                presence_penalty=0.1,
                frequency_penalty=0.6,
            )

            message_content = response.choices[0].message['content']
            formatted_content = self.format_combined(message_content)
            # Добавляем ответ модели в очередь сообщений
            self.previous_messages[chat_id].append({"role": "assistant", "content": message_content})
            self.send_html_message(chat_id, formatted_content, context)
            return formatted_content
        except openai.error.RateLimitError as e:
            return f"Превышен лимит запросов. Подробнее: {e}"
        except openai.error.OpenAIError as e:
            return f"Произошла ошибка OpenAI: {e}"


# Пример использования класса
if __name__ == "__main__":
    bot = ChatBot()
    # Пример вызова метода для получения ответа
    # bot.get_gpt_response("Ваш вопрос", chat_id, user_id, "Имя", context)
