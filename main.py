import requests
import datetime
import os
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient


def average(values: list):
    average_val = 0
    for num in values:
        average_val += num
    average_val /= len(values)
    return average_val


MY_NUM = os.environ['MY_NUM']
SID = os.environ['SID']
TOKEN = os.environ['TOKEN']

HOUR_RANGE = 18

params = {
    # LATERZA
    # "lat": 40.624943,
    # "lon": 16.798088,
    
    # PORDENONE
    #"lat": 45.962650,
    #"lon": 12.655040,

    # CHARLESTOWN
    "lat": 53.963520,
    "lon": -8.791950,
    "units": "metric",
    "lang": "it",
    "exclude": "current,minutely,daily,alerts",
    "appid": "a4ee5d5d6fceb775c3be031c9c7581b9",
}

response = requests.get(url='https://api.openweathermap.org/data/2.5/onecall', params=params)
response.raise_for_status()

data = response.json()["hourly"][:HOUR_RANGE]

bring_umbrella = False
rain_hours = []
temperatures = []
feels_like = []

for item in data:
    temperatures.append(item["temp"])
    feels_like.append(item["feels_like"])
    code = item["weather"][0]["id"]
    if int(code) < 700:
        bring_umbrella = True
        rain_time_data = item["dt"]
        rain_time_hour = datetime.datetime.fromtimestamp(rain_time_data).strftime("%H:00")
        rain_hours.append(rain_time_hour)

if bring_umbrella:
    average_temp = int(average(temperatures))
    average_feels_like = int(average(feels_like))
    rain_hours_text = ", ".join(rain_hours)

    body = f"ALERT:\n\n" \
           f"Expected rain in the next {HOUR_RANGE} hours.\n" \
           f"Average temperature: {average_temp} °C\n" \
           f'Feels like (average): {average_feels_like} °C\n' \
           f"Expected rain at {rain_hours_text} (UTC Time)."

    proxy_client = TwilioHttpClient()
    proxy_client.session.proxies = {'https': os.environ['https_proxy']}

    client = Client(SID, TOKEN, http_client=proxy_client)

    message = client.messages.create(
        body=body,
        from_='+19382014501',
        to=MY_NUM
    )

    with open("log.txt", mode="a") as log_file:
        log_file.write(f"{datetime.date.today()} - {str(message.status)}\n")
else:
    with open("log.txt", mode="a") as log_file:
        log_file.write(f"{datetime.date.today()} - No message was sent.\n")
