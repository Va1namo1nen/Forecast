import os
import socket
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
API_KEY = os.getenv("API_KEY")
history = []

def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def fetch_data(url, params=None):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"\nОшибка: {e}")
        return None

def ip_location():
    data = fetch_data("http://ipinfo.io/json")
    return data.get("city") if data else None

def get_location():
    return input("Введите название города: ")

def get_weather(location):
    params = {
        'q': location,
        'appid': API_KEY,
        'lang': 'ru',
        'units': 'metric'
    }
    data = fetch_data(BASE_URL, params)
    if data and data.get('cod') == 200:
        return data
    print(f"\nОшибка: {data.get('message', 'Неизвестная ошибка')}" if data else "\nОшибка запроса")
    return None

def format_time(shift):
    return datetime.now(tz=timezone(timedelta(seconds=shift))).strftime("%Y-%m-%d %H:%M:%S")

def display_weather(data):
    info = {
        'time': format_time(data['timezone']),
        'city': data['name'],
        'weather': data['weather'][0]['description'],
        'temp': data['main']['temp'],
        'feels_like': data['main']['feels_like'],
        'wind_speed': data['wind']['speed']
    }
    print(
        f"""
Текущее время: {info['time']}
Название города: {info['city']}
Погодные условия: {info['weather']}
Текущая температура: {info['temp']} градусов по цельсию
Ощущается как {info['feels_like']} градусов по цельсию
Скорость ветра: {info['wind_speed']} м/c
"""
    )
    history.append({
        'request_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **info
    })
    if len(history) > 4:
        history.pop(0)

def show_history():
    if not history:
        print("История пуста.")
    else:
        print("\n=== Последние 5 запросов ===")
        for i, entry in enumerate(history[-5:], 1):
            print(
                f"""
            {i}. Время запроса: {entry['request_time']}
Текущее время: {entry['time']}
Название города: {entry['city']}
Погодные условия: {entry['weather']}
Текущая температура: {entry['temp']} градусов по цельсию
Ощущается как {entry['feels_like']} градусов по цельсию
Скорость ветра: {entry['wind_speed']} м/c
            """
            )

def main():
    while True:
        print("\n=== Меню ===")
        print("1. Погода")
        print("2. История запросов")
        print("0. Выйти")
        choice = input("Выберите опцию: ")

        if choice == '1':
            while True:
                print("\n=== Погода ===")
                print("1. Текущее местоположение")
                print("2. Указать город")
                print("0. Назад")
                choice_1 = input("Выберите опцию: ")

                if choice_1 == '1':
                    location = ip_location()
                    data = get_weather(location)
                    if data:
                        display_weather(data)
                    else:
                        print("Не удалось получить данные о текущем местоположении.")
                    input("Нажмите Enter, чтобы вернуться назад.")
                    continue

                elif choice_1 == '2':
                    while True:
                        print("\n0. Назад")
                        location = get_location()
                        if location == "0":
                            break
                        data = get_weather(location)
                        if data:
                            display_weather(data)
                            break
                        else:
                            print("\nГород не найден. Попробуйте снова.")

                elif choice_1 == '0':
                    break

                else:
                    print("Некорректный ввод. Попробуйте снова.")

        elif choice == '2':
            print("\n=== История запросов ===")
            show_history()
            input("Нажмите Enter, чтобы вернуться назад.")
            continue

        elif choice == '0':
            print("Выход из программы.")
            break

        else:
            print("Некорректный ввод. Попробуйте снова.")


if __name__ == '__main__':
    while True:
        if check_internet():
            main()
            break
        else:
            if input('Проверьте соединение с интернетом. Нажмите Enter, чтобы попробовать снова. Нажмите 0, чтобы выйти.') == '0':
                break