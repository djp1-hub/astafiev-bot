import unittest
from unittest.mock import patch, Mock, call
from collections import defaultdict, deque
from main import start, handle_text, previous_messages

class TestMainFunctions(unittest.TestCase):
    @patch('main.Update')
    @patch('main.CallbackContext')
    def test_start(self, mock_context, mock_update):
        mock_update.message.chat_id = 12345
        mock_update.message.reply_text = Mock()
        mock_context.chat_data = {}

        start(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once_with('Привет!')
        self.assertIn('photo_stream', mock_context.chat_data)
        self.assertIsNone(mock_context.chat_data['photo_stream'])

    @patch('main.get_gpt_response')
    @patch('main.weather')
    @patch('main.Update')
    @patch('main.CallbackContext')
    def test_handle_text_weather(self, mock_context, mock_update, mock_weather, mock_get_gpt_response):
        mock_update.message.chat_id = 12345
        mock_update.message.text = "Что там с зябь?"
        mock_update.effective_user.id = 67890
        mock_update.effective_user.full_name = "Test User"
        mock_context.bot_data = {}

        handle_text(mock_update, mock_context)

        mock_weather.assert_called_once_with(mock_update, mock_context)
        mock_get_gpt_response.assert_not_called()

    @patch('main.get_gpt_response')
    @patch('main.weather')
    @patch('main.Update')
    @patch('main.CallbackContext')
    def test_handle_text_explain(self, mock_context, mock_update, mock_weather, mock_get_gpt_response):
        mock_update.message.chat_id = 12345
        mock_update.message.text = "Поясни что такое AI"
        mock_update.effective_user.id = 67890
        mock_update.effective_user.full_name = "Test User"
        mock_context.bot_data = {}

        handle_text(mock_update, mock_context)

        mock_weather.assert_not_called()
        mock_get_gpt_response.assert_called_once_with("что такое ai", 12345, 67890, "Test User", mock_context)

    @patch('main.get_gpt_response')
    @patch('main.weather')
    @patch('main.Update')
    @patch('main.CallbackContext')
    def test_handle_text_normal_message(self, mock_context, mock_update, mock_weather, mock_get_gpt_response):
        mock_update.message.chat_id = 12345
        mock_update.message.text = "Привет, как дела?"
        mock_update.effective_user.id = 67890
        mock_update.effective_user.full_name = "Test User"
        mock_context.bot_data = {}

        handle_text(mock_update, mock_context)

        mock_weather.assert_not_called()
        mock_get_gpt_response.assert_not_called()
        self.assertIn({"role": "user", "content": "Привет, как дела?"}, previous_messages[12345])

if __name__ == '__main__':
    unittest.main()
