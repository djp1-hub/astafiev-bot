import unittest
from unittest.mock import MagicMock, patch
from collections import defaultdict, deque
from src.gpt_response import ChatBot  # Замените 'your_module' на имя вашего модуля
import openai


class TestChatBot(unittest.TestCase):
    def setUp(self):
        self.bot = ChatBot()
        self.context = MagicMock()
        self.chat_id = 123456789
        self.user_id = 5011231443
        self.name = "John Doe"

    def test_escape_html(self):
        text = "Special characters: & < > ' \""
        expected_result = "Special characters: &amp; &lt; &gt; &#39; &quot;"
        result = self.bot.escape_html(text)
        self.assertEqual(result, expected_result)

    def test_filter_html(self):
        html = "<b>bold</b>"
        expected_result = "<b>bold</b>"
        result = self.bot.filter_html(html)
        self.assertEqual(result, expected_result)

    @patch('openai.ChatCompletion.create')
    def test_get_gpt_response(self, mock_create):
        mock_create.return_value = MagicMock(choices=[MagicMock(message={'content': 'response text'})])
        input_text = "This is a test question."

        result = self.bot.get_gpt_response(input_text, self.chat_id, self.user_id, self.name, self.context)

        self.assertIn("response text", result)
        self.context.bot.send_message.assert_called_once()

    def test_format_combined(self):
        markdown_text = "This is **bold** and this is `code`."
        expected_html = "This is <strong>bold</strong> and this is <code>code</code>."
        result = self.bot.format_combined(markdown_text)
        self.assertIn(expected_html, result)

    def test_previous_messages(self):
        # Проверка, что очередь сообщений ограничена 12
        self.bot.previous_messages[self.chat_id] = deque(maxlen=12)
        for i in range(15):
            self.bot.previous_messages[self.chat_id].append(f"message {i}")

        self.assertEqual(len(self.bot.previous_messages[self.chat_id]), 12)
        self.assertEqual(self.bot.previous_messages[self.chat_id][0], "message 3")


if __name__ == '__main__':
    unittest.main()
