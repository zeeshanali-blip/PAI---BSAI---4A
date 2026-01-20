from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re
import csv
import os

app = Flask(__name__)

CSV_FILE = "emails.csv"

def scrape_emails(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()

        emails = set(
            re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        )
        return emails
    except:
        return set()

def save_to_csv(url, emails):
    if not emails:
        return

    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["URL", "Email"])

        for email in emails:
            writer.writerow([url, email])

@app.route("/", methods=["GET", "POST"])
def index():
    emails = []

    if request.method == "POST":
        url = request.form.get("url")
        emails = scrape_emails(url)
        save_to_csv(url, emails)

    return render_template("index.html", emails=emails)

if __name__ == "__main__":
    app.run(debug=True)
