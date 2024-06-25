from src.weather import check_annotation_overlap, weather
import unittest
from unittest.mock import patch, Mock, MagicMock, mock_open
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt

class TestCheckAnnotationOverlap(unittest.TestCase):
    def test_no_overlap(self):
        fig, ax = plt.subplots()
        ax.text(datetime(2023, 1, 1), 10, 'Annotation 1')
        result = check_annotation_overlap(ax, datetime(2023, 1, 2), 20)
        self.assertFalse(result)

    def test_overlap(self):
        fig, ax = plt.subplots()
        ax.text(datetime(2023, 1, 1), 10, 'Annotation 1')
        result = check_annotation_overlap(ax, datetime(2023, 1, 1), 10)
        self.assertTrue(result)

class TestWeatherFunction(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.weather.plt')
    @patch('src.weather.datetime')
    @patch('src.weather.requests.get')
    def test_weather(self, mock_requests, mock_datetime, mock_plt, mock_open):
        # Настройка фиктивных данных для API
        forecast_data = {
            'list': [
                {
                    'dt': 1672531200,
                    'main': {
                        'temp': 273.15 + 5  # 5°C
                    }
                }
            ]
        }
        current_data = {
            'main': {
                'temp': 273.15 + 10,  # 10°C
                'humidity': 80,
                'pressure': 1012
            },
            'wind': {
                'speed': 5
            }
        }

        mock_forecast_response = Mock()
        mock_forecast_response.status_code = 200
        mock_forecast_response.json.return_value = forecast_data

        mock_current_response = Mock()
        mock_current_response.status_code = 200
        mock_current_response.json.return_value = current_data

        mock_requests.side_effect = [mock_forecast_response, mock_current_response] * 3

        mock_datetime.utcfromtimestamp.side_effect = lambda ts: datetime.utcfromtimestamp(ts)

        # Настройка mock для plt.subplots
        mock_fig = MagicMock()
        mock_ax = MagicMock()

        # Настройка mock для ax.plot
        mock_line = MagicMock()
        mock_ax.plot.return_value = [mock_line]

        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        # Параметры для функции
        mock_update = Mock()
        mock_context = Mock()
        mock_update.message.chat_id = 12345

        # Вызов функции
        weather(mock_update, mock_context)

        # Проверка вызовов requests.get
        self.assertEqual(mock_requests.call_count, 6)

        # Проверка вызовов plt функции
        mock_plt.subplots.assert_called_once()
        mock_plt.savefig.assert_called_once_with('weather_chart.png', bbox_inches='tight')
        mock_open.assert_called_once_with('weather_chart.png', 'rb')
        mock_update.message.reply_photo.assert_called_once()

if __name__ == '__main__':
    unittest.main()
