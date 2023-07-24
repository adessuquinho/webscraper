from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import requests
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Force decode the response content as UTF-8
            text = response.content.decode('utf-8', errors='replace')

            soup = BeautifulSoup(text, 'html.parser')

            # Load ignore data from JSON file
            with open('ignore_data.json', 'r') as f:
                ignore_data = json.load(f)
            ignore_texts = ignore_data.get('ignore_texts', [])
            ignore_classes = ignore_data.get('ignore_classes', [])

            # Remove paragraphs with ignored classes
            for element in soup.find_all(class_=ignore_classes):
                element.decompose()

            # Remove paragraphs with ignored texts
            for element in soup.find_all('p'):
                if any(ignore_text in element.get_text() for ignore_text in ignore_texts):
                    element.decompose()

            # Extract the HTML of remaining paragraphs
            paragraphs = [str(p) for p in soup.find_all('p')]

            if not paragraphs:
                return render_template('error.html', message='No text found on the page.')
            
            page_title = soup.title.get_text() if soup.title else "Scrape Results"

            return render_template('result.html', page_title=page_title, paragraphs=paragraphs)

            return render_template('result.html', paragraphs=paragraphs)

        except (requests.RequestException, ValueError):
            return render_template('error.html', message='Invalid URL or the request timed out.')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)