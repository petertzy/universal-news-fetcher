from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urljoin
import os
from dotenv import load_dotenv
import html

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv("GEMINI_API_URL")

# Function to scrape article body
def get_article_body(link):
    try:
        response = requests.get(link, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch article. Status code: {response.status_code}")
            return ""

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <p> tags and concatenate text
        #paragraphs = soup.find_all('p')
        #body_text = ' '.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        #body_text = soup.select('div.article-body p')
        # Find all <p> tags and concatenate text

        article_container = soup.find('div', class_='article-body')
        if article_container:
            paragraphs = article_container.find_all('p')
            body_text = ' '.join(html.unescape(p.get_text()) for p in paragraphs)

            body_text = body_text.replace('\xa0', ' ')

        return body_text
    except Exception as e:
        print(f"Error fetching article body: {e}")
        return ""

# Function to fetch top headline
def get_top_headline():
    url = "https://www.foxnews.com/"
    print(f"Fetching URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        headline_element = soup.find('h3', class_='title')
        if not headline_element:
            print("No headline found.")
            return None

        headline_link = headline_element.find('a')
        if not headline_link:
            print("No link found in the headline.")
            return None

        headline_text = headline_link.get_text(strip=True)
        print(f"Original headline: {headline_text}")

        link = headline_link['href']
        if not link.startswith('http'):
            link = f"https://www.foxnews.com{link}"

        # Get image
        image_element = soup.find('picture')
        image_url = None
        if image_element:
            img_tag = image_element.find('img')
            if img_tag and 'src' in img_tag.attrs:
                image_url = img_tag['src']
                if image_url.startswith('//'):
                    image_url = urljoin('https:', image_url)

        # Get article body
        body = get_article_body(link)

        return {
            'title': "FOX: " + headline_text,
            'link': link,
            'image': image_url,
            'body': body
        }

    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to translate headline title to Chinese
def translate_title_to_chinese(title):
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        "contents": [{
            "parts": [{"text": f"Translate this into Chinese. Only provide the translated text, nothing else: {title}"}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        print(f"Gemini API response: {result}")

        if 'candidates' not in result or not result['candidates']:
            print("No candidates found in response.")
            return "Translation failed"

        candidate = result['candidates'][0]
        if 'content' not in candidate or 'parts' not in candidate['content'] or not candidate['content']['parts']:
            print("Unexpected response structure.")
            return "Translation failed"

        translated_text = candidate['content']['parts'][0]['text']
        return translated_text.strip()
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return "Translation failed"

# Function to translate article body to Chinese
def translate_text_to_chinese(text):
    if not text or not text.strip():
        return "(No content available for translation)"

    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

    headers = {
        'Content-Type': 'application/json'
    }

    prompt = f"Translate the following English article into Chinese. Just return the translated Chinese text, do not include any explanation or formatting:\n\n{text}"

    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        print("Gemini API response:", result)

        # Safely extract translated content
        candidates = result.get("candidates", [])
        if not candidates:
            return "Translation failed (no candidates returned)"

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts or not parts[0].get("text"):
            return "Translation failed (unexpected response structure)"

        translated_text = parts[0]["text"].strip()
        return translated_text

    except requests.exceptions.RequestException as e:
        print(f"Request to Gemini API failed: {e}")
        return "Translation failed (request error)"
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return "Translation failed (unknown error)"

# API endpoint to fetch and translate top headline
@app.get("/api/get-top-headline")
async def get_top_headline_api():
    original_headline = get_top_headline()

    if not original_headline:
        return JSONResponse(content={"message": "Failed to fetch headline"}, status_code=500)

    # Translate title and body
    translated_title = translate_title_to_chinese(original_headline['title'])
    translated_body = translate_text_to_chinese(original_headline['body'])

    translated_headline = {
        'title': translated_title,
        'link': original_headline['link'],
        'image': original_headline['image'],
        'body': translated_body
    }

    return {
        "headlines": [
            translated_headline,
            original_headline
        ]
    }

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the News API! Use /api/get-top-headline to retrieve top headlines."}
