from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urljoin
import os
from dotenv import load_dotenv

app = FastAPI()

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all request headers
)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv("GEMINI_API_URL")

# Function to fetch the top headline from Fox News
def get_top_headline():
    url = "https://www.foxnews.com/"
    print(f"Fetching URL: {url}")  # Log fetching attempt

    try:
        response = requests.get(url, timeout=10)  # Set a timeout to avoid hanging requests
        if response.status_code != 200:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Get the first headline
        headline_element = soup.find('h3', class_='title')
        if not headline_element:
            print("No headline found.")
            return None

        headline_link = headline_element.find('a')
        if not headline_link:
            print("No link found in the headline.")
            return None

        # Extract headline text
        headline_text = headline_link.get_text(strip=True)
        print(f"Original headline: {headline_text}")

        link = headline_link['href']
        if not link.startswith('http'):
            link = f"https://www.foxnews.com{link}"

        # Get image URL
        image_element = soup.find('picture')
        image_url = None
        if image_element:
            img_tag = image_element.find('img')
            if img_tag and 'src' in img_tag.attrs:
                image_url = img_tag['src']
                if image_url.startswith('//'):
                    image_url = urljoin('https:', image_url)

        return {
            'title': "FOX: " + headline_text,
            'link': link,
            'image': image_url
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Function to translate the headline using Gemini API
def translate_title_to_german(title):
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
        
        print(f"Gemini API response: {result}")  # Debugging output

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

# API endpoint to get both the original and translated headlines
@app.get("/api/get-top-headline")
async def get_top_headline_api():
    original_headline = get_top_headline()

    if not original_headline:
        return JSONResponse(content={"message": "Failed to fetch headline"}, status_code=500)

    # Get the German translation
    german_translation = translate_title_to_german(original_headline['title'])

    translated_headline = {
        'title': "FOX: " + german_translation,  # Add FOX prefix to translated title
        'link': original_headline['link'],
        'image': original_headline['image']
    }

    return {"headlines": [translated_headline, original_headline]}

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the News API! Go to /api/get-top-headline to fetch top headlines."}
