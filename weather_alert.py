"""
Checks OpenWeatherMap for your city.
If temperature > 35°C OR rain/thunderstorm/drizzle is in the forecast,
sends YOU an email alert. Scheduled daily via GitHub Actions.

"""

import os
import smtplib
import requests
from email.mime.text import MIMEText

CITY = "Thiruvananthapuram,IN"  # <-- change to "YourCity,CountryCode"

API_KEY = os.environ["OPENWEATHER_API_KEY"]
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
TO_EMAIL = os.environ.get("TO_EMAIL", EMAIL_ADDRESS)


def get_weather():
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": CITY, "appid": API_KEY, "units": "metric"}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)


def main():
    data = get_weather()
    temp = data["main"]["temp"]
    conditions = [w["main"].lower() for w in data["weather"]]
    description = data["weather"][0]["description"]

    print(f"Current temp: {temp}°C, conditions: {description}")

    alerts = []
    if temp > 35:
        alerts.append(f"🔥 High temperature alert: {temp}°C in {CITY}.")
    if any(c in conditions for c in ("rain", "thunderstorm", "drizzle")):
        alerts.append(f"🌧️ Rain is predicted in {CITY}: {description}.")

    if alerts:
        body = "\n".join(alerts) + f"\n\nFull conditions: {description}, {temp}°C"
        send_email(f"Weather Alert for {CITY}", body)
        print("Alert email sent.")
    else:
        print("No alert conditions met — no email sent.")


if __name__ == "__main__":
    main()
