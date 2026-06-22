# Sentiment Analysis Studio (Flask + TextBlob)

Advanced Flask app for sentiment analysis using TextBlob. The app now includes:
- polarity and subjectivity scoring
- confidence labeling and tone summaries
- positive / negative term highlights
- session history of recent analyses
- polished responsive interface with live sentiment meters

## Setup

1. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Download TextBlob corpora (pattern/text corpora):

```bash
python -m textblob.download_corpora
```

## Run

You can run the app directly:

```bash
python app.py
```

Or using Flask CLI (Windows):

```bash
set FLASK_APP=app.py
flask run
```

Then open http://127.0.0.1:5000 in your browser.

> Do not open `templates/index.html` directly with Live Server or a static file server. The form requires the Flask backend to handle the POST request.

## Files

- [sentiment-analysis/app.py](sentiment-analysis/app.py#L1) - Flask application
- [sentiment-analysis/templates/index.html](sentiment-analysis/templates/index.html#L1) - Form view
- [sentiment-analysis/templates/result.html](sentiment-analysis/templates/result.html#L1) - Result view
- [sentiment-analysis/requirements.txt](sentiment-analysis/requirements.txt#L1) - Python dependencies

