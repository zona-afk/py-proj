"""
News Digest Bot 
------------------------------------
Scrapes top headlines from 3 news sites, builds a formatted
HTML email (with links + generation time), and sends it to you
every morning at 7 AM via GitHub Actions.

Needs these secrets set in your GitHub repo:
  EMAIL_ADDRESS
  EMAIL_APP_PASSWORD
  TO_EMAIL (optional, defaults to EMAIL_ADDRESS)

NOTE: News sites change their HTML structure from time to time.
If a source returns "no headlines found", open the site, right-click
a headline -> Inspect, and update the CSS selector below to match.
"""

import os
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]
TO_EMAIL = os.environ.get("TO_EMAIL", EMAIL_ADDRESS)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PulseNewsBot/1.0)"}


def scrape_hackernews():
    items = []
    r = requests.get("https://news.ycombinator.com/", headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    for row in soup.select("tr.athing")[:5]:
        link = row.select_one("span.titleline a")
        if link:
            items.append({"title": link.get_text(strip=True), "link": link["href"]})
    return {"source": "Hacker News", "items": items}


def scrape_bbc():
    items = []
    r = requests.get("https://www.bbc.com/news", headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    for link in soup.select("a[data-testid='internal-link']")[:5]:
        title = link.get_text(strip=True)
        href = link.get("href", "")
        if title and href:
            if href.startswith("/"):
                href = "https://www.bbc.com" + href
            items.append({"title": title, "link": href})
    return {"source": "BBC News", "items": items}


def scrape_toi():
    items = []
    r = requests.get("https://timesofindia.indiatimes.com/", headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    for link in soup.select("figcaption a")[:5]:
        title = link.get_text(strip=True)
        href = link.get("href", "")
        if title and href:
            if href.startswith("/"):
                href = "https://timesofindia.indiatimes.com" + href
            items.append({"title": title, "link": href})
    return {"source": "Times of India", "items": items}


def build_html(sources, generated_at):
    html = f"<h2>Your Morning News Digest — {generated_at}</h2>"
    for source in sources:
        html += f"<h3>{source['source']}</h3><ul>"
        if source["items"]:
            for item in source["items"]:
                html += f"<li><a href='{item['link']}'>{item['title']}</a></li>"
        else:
            html += "<li>(no headlines found — site layout may have changed)</li>"
        html += "</ul>"
    html += f"<p><small>Generated at {generated_at}</small></p>"
    return html


def send_email(html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Morning News Digest"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)


def main():
    generated_at = datetime.now().strftime("%A, %d %B %Y %H:%M")
    sources = []
    for scraper in (scrape_hackernews, scrape_bbc, scrape_toi):
        try:
            sources.append(scraper())
        except Exception as e:
            sources.append({"source": scraper.__name__, "items": []})
            print(f"{scraper.__name__} failed: {e}")

    html = build_html(sources, generated_at)
    send_email(html)
    print("News digest sent.")


if __name__ == "__main__":
    main()
