import locale
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import requests
from config import API_KEY
import io


class WeatherBot:
    FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
    CURRENT_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

    def __init__(self):
        self.user_cities = defaultdict(list)

    def weather(self, update, context):
        chat_id = update.message.chat_id
        cities = self.user_cities[chat_id] if chat_id in self.user_cities else ["Krasnoyarsk, RU", "Kaliningrad, RU", "Belgrade, RS"]

        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

        city_weather = {
            city: {
                'dates': [],
                'temps': [],
                'current_temp': None,
                'humidity': None,
                'pressure': None,
                'wind_speed': None
            } for city in cities
        }

        for city in cities:
            # Запрос прогноза погоды
            forecast_response = requests.get(f"{self.FORECAST_URL}?q={city}&appid={API_KEY}")
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                for item in forecast_data['list']:
                    timestamp = item['dt']
                    datetime_utc = datetime.utcfromtimestamp(timestamp)
                    temp = item['main']['temp'] - 273.15  # Конвертация в Цельсии

                    # Сохранение времени и температуры
                    city_weather[city]['dates'].append(datetime_utc)
                    city_weather[city]['temps'].append(temp)

            # Запрос текущей погоды
            current_response = requests.get(f"{self.CURRENT_WEATHER_URL}?q={city}&appid={API_KEY}")
            if current_response.status_code == 200:
                current_data = current_response.json()
                city_weather[city]['current_temp'] = current_data['main']['temp'] - 273.15
                city_weather[city]['humidity'] = current_data['main']['humidity']
                city_weather[city]['pressure'] = current_data['main']['pressure']
                city_weather[city]['wind_speed'] = current_data['wind']['speed']

        # Создание линейного графика
        fig, ax = plt.subplots()
        ax.set_ylabel('Температура (°C)')
        ax.grid(True, which='major', axis='y', linestyle='--')

        for city in cities:
            dates = city_weather[city]['dates']
            temps = city_weather[city]['temps']

            line, = ax.plot(dates, temps, label=city)

            # Добавление подписей для макс. и мин. значений с выносками
            if temps:  # Проверка на пустой список
                max_temp = max(temps)
                min_temp = min(temps)
                max_date = dates[temps.index(max_temp)]
                min_date = dates[temps.index(min_temp)]
                if not self.check_annotation_overlap(ax, max_date, max_temp):
                    ax.annotate(f'максимум {round(max_temp)}°C в {max_date}', xy=(max_date, max_temp),
                                xytext=(max_date, max_temp + 5),
                                arrowprops=dict(facecolor=line.get_color(), shrink=0.05),
                                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.75))

                if not self.check_annotation_overlap(ax, min_date, min_temp):
                    ax.annotate(f'минимум {round(min_temp)}°C в {min_date}', xy=(min_date, min_temp),
                                xytext=(min_date, min_temp - 5),
                                arrowprops=dict(facecolor=line.get_color(), shrink=0.05),
                                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.75))

        # Форматирование оси X
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Создание и размещение таблицы с текущими данными
        cell_text = []
        col_labels = ['Темп.', 'Вл.(%)', 'Давл.(hPa)', 'Ск.вет.(м/с)']
        for city in cities:
            city_data = city_weather[city]
            cell_text.append([
                f"{city_data['current_temp']:.2f}°C" if city_data['current_temp'] is not None else 'N/A',
                f"{city_data['humidity']}%" if city_data['humidity'] is not None else 'N/A',
                f"{city_data['pressure']} hPa" if city_data['pressure'] is not None else 'N/A',
                f"{city_data['wind_speed']} м/с" if city_data['wind_speed'] is not None else 'N/A'
            ])

        table = plt.table(cellText=cell_text, rowLabels=cities, colLabels=col_labels, loc='bottom', bbox=[0, -1.1, 1, 0.6])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        plt.subplots_adjust(bottom=0.4, right=0.75)

        # Настройка легенды
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -1.15), ncol=len(cities), frameon=False)

        # Сохранение и отправка графика
        chart_stream = io.BytesIO()
        plt.savefig(chart_stream, format='png', bbox_inches='tight')
        chart_stream.seek(0)
        update.message.reply_photo(photo=chart_stream)
        plt.close()

    def check_annotation_overlap(self, ax, x, y, threshold=0.1):
        annotations = ax.texts
        for annotation in annotations:
            ax_x, ax_y = annotation.get_position()
            # Преобразование datetime.datetime в datetime.timedelta
            ax_x_timedelta = x - ax_x
            if abs(ax_x_timedelta.total_seconds()) < threshold and abs(y - ax_y) < threshold:
                return True
        return False
