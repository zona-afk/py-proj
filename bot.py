"""
Pulse Bot — Daily Summary
--------------------------

"""

import requests
from datetime import datetime

CITY = "Thiruvananthapuram"  # <-- change to your city


def get_weather(city):
    """wttr.in needs no API key. Returns something like 'Clear +29°C'"""
    url = f"https://wttr.in/{city}?format=%C+%t"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        return f"Weather unavailable ({e})"


def get_quote():
    """ZenQuotes is free and needs no API key."""
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()[0]
        return f'"{data["q"]}" — {data["a"]}'
    except requests.RequestException as e:
        return f"Quote unavailable ({e})"


def build_entry():
    today = datetime.now().strftime("%A, %d %B %Y")
    weather = get_weather(CITY)
    quote = get_quote()
    return (
        f"## {today}\n\n"
        f"- **Weather in {CITY}:** {weather}\n"
        f"- **Quote of the day:** {quote}\n\n"
        f"---\n\n"
    )


def main():
    entry = build_entry()
    header = "# Pulse Log\n\n"

    try:
        with open("pulse-log.md", "r", encoding="utf-8") as f:
            content = f.read()
        body = content[len(header):] if content.startswith(header) else content
    except FileNotFoundError:
        body = ""

    with open("pulse-log.md", "w", encoding="utf-8") as f:
        f.write(header + entry + body)

    print("New Pulse entry added:\n")
    print(entry)


if __name__ == "__main__":
    main()
