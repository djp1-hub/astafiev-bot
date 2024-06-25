from src.gpt_response import ChatBot  # Обновите путь к модулю, если он отличается

import unittest

class TestChatBot(unittest.TestCase):
    def setUp(self):
        self.bot = ChatBot()

    def test_combined_formatting(self):
        text = "Here is some code: ```print('Hello')``` and some math: \\[x = y + z\\]."
        expected_output = "Here is some code: <pre><code>print(&#39;Hello&#39;)</code></pre>and some math: <pre>x = y + z</pre>"
        self.assertEqual(self.bot.format_combined(text), expected_output)

    def test_format_code_blocks(self):
        text = "Here is some code: ```print('Hello')```"
        expected_output = "Here is some code: <pre><code>print(&#39;Hello&#39;)</code></pre>"
        self.assertEqual(self.bot.format_combined(text), expected_output)

    def test_format_math_blocks(self):
        text = "Here is a math expression: \\[x = y + z\\]"
        expected_output = "Here is a math expression: <pre>x = y + z</pre>"
        self.assertEqual(self.bot.format_combined(text), expected_output)

if __name__ == '__main__':
    unittest.main()
