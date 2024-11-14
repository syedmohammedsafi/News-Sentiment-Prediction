import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from twilio.rest import Client
import schedule
import time

account_sid = 'AC85c774794f67fc574ce2541afba03328'
auth_token = '51a2b5fe9d11d00f28ce30240d5ef6ae'
from_num = '+13345184077',
to_num = '+917305607997'

client = Client(account_sid, auth_token)

def get_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def classify_sentiment(sentiment_score):
    if sentiment_score > 0:
        return 'Positive'
    elif sentiment_score < 0:
        return 'Negative'
    else:
        return 'Neutral'

def scrape_news(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        texts = []

        headings = soup.find_all('h2')
        for heading in headings:
            if heading.text.strip():
                texts.append(heading.text.strip())

        divheadings = soup.find_all('div')
        for heading in divheadings:
            if heading.text.strip():
                texts.append(heading.text.strip())

        paragraphs = soup.find_all('p')
        for paragraph in paragraphs:
            if paragraph.text.strip():
                texts.append(paragraph.text.strip())

        sentiment_counts = {
            'Positive': 0,
            'Negative': 0,
            'Neutral': 0
        }

        for text in texts:
            sentiment_score = get_sentiment(text)
            sentiment = classify_sentiment(sentiment_score)
            sentiment_counts[sentiment] += 1

        overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)

        message = f"URL: {url}\nSentiment Counts:\n"
        for sentiment, count in sentiment_counts.items():
            message += f"{sentiment}: {count}\n"
        message += f"Overall Sentiment: {overall_sentiment}"

        client.messages.create(
            to = to_num,
            from_ = from_num,
            body=message
        )

        print(f"Sentiment analysis sent via SMS for {url}")
        print("-" * 100)
    else:
        print(f"Failed to retrieve content from {url}")

urls = [
    "https://timesofindia.indiatimes.com/",
    "https://www.indiatoday.in/",
    "https://www.thehindu.com/",
    "https://indianexpress.com/",
    "https://www.news18.com/",
    "https://www.newsnation.in/",
    "https://www.firstpost.com/",
    "https://www.deccanchronicle.com/"
]

for url in urls:
    schedule.every().day.at("15:07").do(scrape_news, url=url)

while True:
    schedule.run_pending()
    time.sleep(1)
