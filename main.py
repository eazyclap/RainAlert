import requests
import datetime
import os
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient


# Simple function to calc average value of a list
def average(values: list):
    average_val = 0
    for num in values:
        average_val += num
    average_val /= len(values)
    return average_val


# Took from environment variables 
MY_NUM = os.environ['MY_NUM']
FROM_NUM = os.environ['FROM_NUM']
SID = os.environ['SID']
TOKEN = os.environ['TOKEN']

# Set coordinates of a city/place
LAT = 40.624943
LON = 16.798088

# Set the hour range, max is 48
HOUR_RANGE = 18

# Parameters of OpenWeatherMap API
params = {
    "lat": LAT,
    "lon": LON,
    "units": "metric",
    "lang": "it",
    "exclude": "current,minutely,daily,alerts",
    "appid": "a4ee5d5d6fceb775c3be031c9c7581b9",
}

# Request to OpenWeatherMap
response = requests.get(url='https://api.openweathermap.org/data/2.5/onecall', params=params)
response.raise_for_status()

# Getting the data from the API response
data = response.json()["hourly"][:HOUR_RANGE]

# bring_umbrella stores the result rain/not-rain
bring_umbrella = False

# Lists initialization
rain_hours = []
temperatures = []
feels_like = []

# Organizing data
for item in data:
    temperatures.append(item["temp"])
    feels_like.append(item["feels_like"])
    code = item["weather"][0]["id"]
    if int(code) < 700:
        bring_umbrella = True
        rain_time_data = item["dt"]
        rain_time_hour = datetime.datetime.fromtimestamp(rain_time_data).strftime("%H:00")
        rain_hours.append(rain_time_hour)

# If it's going to rain
if bring_umbrella:
    # Set up message
    average_temp = int(average(temperatures))
    average_feels_like = int(average(feels_like))
    rain_hours_text = ", ".join(rain_hours)
    
    body = f"ALERT:\n\n" \
           f"Expected rain in the next {HOUR_RANGE} hours.\n" \
           f"Average temperature: {average_temp} °C\n" \
           f'Feels like (average): {average_feels_like} °C\n' \
           f"Expected rain at {rain_hours_text} (UTC Time)."
    
    # Initialize twilio API
    proxy_client = TwilioHttpClient()
    proxy_client.session.proxies = {'https': os.environ['https_proxy']}

    client = Client(SID, TOKEN, http_client=proxy_client)
    
    # Send message
    message = client.messages.create(
        body=body,
        from_=FROM_NUM,
        to=MY_NUM
    )
    
    # Log the outcome
    with open("log.txt", mode="a") as log_file:
        log_file.write(f"{datetime.date.today()} - {str(message.status)}")
else:
    # If it isn't raining, log that message has not been sent
    with open("log.txt", mode="a") as log_file:
        log_file.write(f"{datetime.date.today()} - No message was sent.\n")
