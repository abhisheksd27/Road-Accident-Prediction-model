import requests

def get_current_weather(latitude, longitude, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to fetch weather data:", response.status_code)
        return None

# Set your latitude, longitude, and OpenWeatherMap API key
latitude = 78.063089
longitude = 9.966063
api_key = "f7e1284567bab40bc03747f246171ce6"

weather_data = get_current_weather(latitude, longitude, api_key)
if weather_data:
    print("Current Weather Data:")
    print("Description:", weather_data['weather'][0]['description'])
    print("Temperature:", weather_data['main']['temp'], "°C")
    print("Humidity:", weather_data['main']['humidity'], "%")
    print("Wind Speed:", weather_data['wind']['speed'], "m/s")
else:
    print("No weather data available.")
