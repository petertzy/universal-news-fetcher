from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 配置 CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许前端来自 localhost:3000 的请求
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 获取福克斯新闻首页的头条新闻
def get_top_headline():
    url = "https://www.foxnews.com/"
    print(f"Fetching URL: {url}")  # 添加日志
    try:
        response = requests.get(url, timeout=10)  # 设置超时，避免请求卡住
        if response.status_code == 200:
            print("Successfully fetched the page.")  # 添加日志
            soup = BeautifulSoup(response.text, 'html.parser')

            # 获取第一条头条新闻
            headline_element = soup.find('h3', class_='title')  # 查找第一个 h3.title
            if not headline_element:
                print("No headline found.")  # 添加日志
                return None

            headline_link = headline_element.find('a')  # 获取链接
            if not headline_link:
                return None

            title = headline_link.get_text(strip=True)  # 获取标题文本并去除多余空格
            link = headline_link['href']
            if not link.startswith('http'):
                link = f"https://www.foxnews.com{link}"  # 构建完整链接

            return {
                'title': title,
                'link': link
            }
        else:
            print(f"Failed to fetch page. Status code: {response.status_code}")  # 添加日志
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")  # 捕获网络请求相关的异常
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")  # 捕获其它可能的异常
        return None

# 路由：获取头条新闻
@app.get("/api/get-top-headline")
async def get_top_headline_api():
    headline = get_top_headline()  # 获取单个头条
    if not headline:
        return JSONResponse(content={"message": "Failed to fetch headline"}, status_code=500)
    
    return {"headline": headline}  # 返回单个头条新闻

# 路由：主页
@app.get("/")
async def read_root():
    return {"message": "Welcome to the News API! Go to /api/get-top-headline to fetch top headline."}
