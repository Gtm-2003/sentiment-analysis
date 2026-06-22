import os
from collections import Counter
from datetime import datetime
import re

from flask import Flask, render_template, request, session
from textblob import TextBlob

app = Flask(__name__)
# Use environment variable for secret in production; keep fallback for local dev
app.secret_key = os.environ.get('FLASK_SECRET') or 'replace-this-with-a-secure-random-key'
# Safer cookie defaults
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)


def normalize_token(token):
    return re.sub(r"[^A-Za-z']+", '', token).lower().strip()


def sentiment_label(polarity):
    if polarity >= 0.6:
        return 'Strongly Positive'
    if polarity >= 0.15:
        return 'Positive'
    if polarity > -0.15:
        return 'Neutral'
    if polarity > -0.6:
        return 'Negative'
    return 'Strongly Negative'


def polarity_summary(polarity):
    if polarity >= 0.8:
        return 'The text is highly positive and enthusiastic.'
    if polarity >= 0.4:
        return 'The tone is positive and upbeat.'
    if polarity >= 0.15:
        return 'The sentiment is mildly positive.'
    if polarity > -0.15:
        return 'The text is neutral or mixed.'
    if polarity > -0.4:
        return 'The tone is mildly negative.'
    if polarity > -0.8:
        return 'The sentiment is negative and critical.'
    return 'The text is very negative.'


def subjectivity_summary(subjectivity):
    if subjectivity >= 0.75:
        return 'The text is very subjective and personal.'
    if subjectivity >= 0.45:
        return 'The message is balanced with personal opinion.'
    return 'The writing is objective and factual.'


def extract_term_insights(text):
    blob = TextBlob(text)
    words = [normalize_token(word) for word in blob.words if len(normalize_token(word)) > 2]
    counts = Counter(words)
    scored = []

    for word in counts:
        score = TextBlob(word).sentiment.polarity
        if abs(score) > 0.1:
            scored.append((word, score, counts[word]))

    positive_terms = sorted([item for item in scored if item[1] > 0], key=lambda x: (-x[1], -x[2]))[:5]
    negative_terms = sorted([item for item in scored if item[1] < 0], key=lambda x: (x[1], -x[2]))[:5]
    top_terms = [word for word, _ in counts.most_common(8)]

    return positive_terms, negative_terms, top_terms


def add_to_history(entry):
    history = session.get('history', [])
    history.insert(0, entry)
    session['history'] = history[:6]
    session.modified = True


@app.route('/', methods=['GET', 'POST'])
def index():
    history = session.get('history', [])

    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        if not text:
            error = 'Please enter some text.'
            return render_template('index.html', error=error, text=text, history=history)

        blob = TextBlob(text)
        polarity = round(blob.sentiment.polarity, 4)
        subjectivity = round(blob.sentiment.subjectivity, 4)
        label = sentiment_label(polarity)
        polarity_desc = polarity_summary(polarity)
        subjectivity_desc = subjectivity_summary(subjectivity)
        word_count = len(blob.words)
        sentence_count = len(blob.sentences)
        avg_word_length = round(
            sum(len(normalize_token(w)) for w in blob.words if normalize_token(w)) / max(1, word_count),
            2,
        )
        positive_terms, negative_terms, top_terms = extract_term_insights(text)
        confidence = 'High' if abs(polarity) >= 0.4 else 'Moderate' if abs(polarity) >= 0.15 else 'Low'
        trend = None

        if history:
            last_polarity = history[0].get('polarity', 0)
            if polarity > last_polarity:
                trend = 'This result is more positive than your previous analysis.'
            elif polarity < last_polarity:
                trend = 'This result is more negative than your previous analysis.'
            else:
                trend = 'Sentiment remains consistent with the last analysis.'

        entry = {
            'text': text,
            'label': label,
            'polarity': polarity,
            'subjectivity': subjectivity,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'short_text': text if len(text) <= 60 else text[:57] + '...',
        }
        add_to_history(entry)

        return render_template(
            'result.html',
            text=text,
            label=label,
            polarity=polarity,
            subjectivity=subjectivity,
            polarity_desc=polarity_desc,
            subjectivity_desc=subjectivity_desc,
            word_count=word_count,
            sentence_count=sentence_count,
            avg_word_length=avg_word_length,
            positive_terms=positive_terms,
            negative_terms=negative_terms,
            top_terms=top_terms,
            confidence=confidence,
            trend=trend,
            history=session.get('history', []),
        )

    return render_template('index.html', history=history)


if __name__ == '__main__':
    app.run(debug=True)
