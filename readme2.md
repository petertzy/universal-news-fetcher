### 项目结构

首先，假设你的项目结构如下：

```
my-next-app/
├── backend/
│   ├── app.py           # FastAPI 后端应用
│   └── requirements.txt # 后端依赖包
├── frontend/
│   ├── components/
│   │   └── SendNotificationPage.tsx  # React 前端页面
│   ├── pages/
│   │   └── sendNotification.tsx      # 页面入口
│   └── package.json     # 前端依赖
└── README.md            # 项目说明文件
```

### 步骤 1: 编写后端爬虫代码

#### 1.1 安装依赖

在后端部分，我们使用 FastAPI 来编写 API，并用 `beautifulsoup4` 和 `requests` 库进行网页爬取。

```bash
pip install fastapi uvicorn beautifulsoup4 requests
```

#### 1.2 创建后端文件

在 `backend/` 文件夹中创建一个名为 `app.py` 的文件，这是后端应用的主文件。

**文件路径：`backend/app.py`**

```python
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from fastapi.responses import JSONResponse

app = FastAPI()

# 获取福克斯新闻首页的头条新闻
def get_top_headlines():
    url = "https://www.foxnews.com/"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('a', class_='article-title')
        
        top_headlines = []
        for headline in headlines:
            title = headline.get_text()
            link = headline['href']
            if not link.startswith('http'):
                link = f"https://www.foxnews.com{link}"
            top_headlines.append({
                'title': title,
                'link': link
            })
        return top_headlines
    else:
        return []

@app.get("/api/get-top-headlines")
async def get_top_headlines_api():
    headlines = get_top_headlines()
    if not headlines:
        return JSONResponse(content={"message": "Failed to fetch headlines"}, status_code=500)
    
    return {"headlines": headlines}
```

#### 解释：
- `get_top_headlines()`：爬取福克斯新闻首页，提取头条新闻的标题和链接。
- `/api/get-top-headlines`：FastAPI 提供的端点，返回头条新闻的 JSON 响应。

#### 1.3 启动后端应用

你可以使用 `uvicorn` 启动 FastAPI 后端：

```bash
uvicorn app:app --reload
```

### 步骤 2: 修改前端代码来获取爬取的新闻

前端部分使用 React 和 TypeScript。我们需要编写一个组件来显示按钮，点击后从后端获取新闻并推送通知。

#### 2.1 安装前端依赖

在 `frontend/` 文件夹中，确保安装了 `react` 和 `typescript`，如果没有，使用以下命令安装：

```bash
npm install react react-dom typescript
```

#### 2.2 创建前端组件

在 `frontend/components/` 文件夹中创建一个名为 `SendNotificationPage.tsx` 的文件。

**文件路径：`frontend/components/SendNotificationPage.tsx`**

```typescript
import React, { useState } from 'react';
import styles from './page.module.css';

const SendNotificationPage = () => {
  const [notificationSent, setNotificationSent] = useState<boolean | null>(null);
  const [headlines, setHeadlines] = useState<{ title: string; link: string }[] | null>(null);

  const fetchTopHeadlines = async () => {
    try {
      const response = await fetch('/api/get-top-headlines'); // 从后端获取头条新闻
      const data = await response.json();
      if (data.headlines) {
        setHeadlines(data.headlines); // 更新头条新闻状态
      } else {
        console.error("Failed to retrieve headlines");
      }
    } catch (error) {
      console.error("Error fetching headlines:", error);
    }
  };

  const sendNotification = async () => {
    // Retrieve all device tokens
    let tokens: string[] = [];
    try {
      const tokenResponse = await fetch('https://firebase-push-server.onrender.com/api/get-device-token');
      const tokenData = await tokenResponse.json();
      if (!tokenData.tokens || tokenData.tokens.length === 0) {
        throw new Error("No device tokens found");
      }
      tokens = tokenData.tokens;
    } catch (error) {
      console.error("Failed to retrieve tokens:", error);
      setNotificationSent(false);
      return;
    }

    // Fetch the latest headlines
    if (!headlines || headlines.length === 0) {
      await fetchTopHeadlines();  // 如果新闻为空，则尝试获取最新的头条新闻
    }

    // Proceed with sending notifications only if headlines are available
    const notificationData = {
      tokens: tokens,
      title: headlines && headlines.length > 0 ? headlines[0].title : 'Default Headline',
      body: headlines && headlines.length > 0 ? headlines[0].link : 'No news available',
      image: 'https://a57.foxnews.com/prod-hp.foxnews.com/images/2025/03/662/372/77a1d0e069043a1b7bbc33a01c371365.png?tl=1&ve=1',
      link: headlines && headlines.length > 0 ? headlines[0].link : '#',
      time: new Date().toISOString(),
      author: 'Admin',
    };

    try {
      const response = await fetch('/api/send-notification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(notificationData),
      });

      if (response.ok) {
        const responseData = await response.json();
        setNotificationSent(true);
        console.log(`${responseData.successCount} notifications sent successfully.`);
      } else {
        setNotificationSent(false);
      }
    } catch (error) {
      console.error('Error sending notification:', error);
      setNotificationSent(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>Send Push Notification</h1>
      <button className={styles.button} onClick={sendNotification}>Send Notification</button>
      {notificationSent !== null && (
        <p className={styles.text}>
          {notificationSent ? 'Notification sent successfully!' : 'Failed to send notification'}
        </p>
      )}
    </div>
  );
};

export default SendNotificationPage;
```

#### 解释：
- `fetchTopHeadlines()`：从后端 `/api/get-top-headlines` 获取头条新闻并将其保存在 `headlines` 状态中。
- `sendNotification()`：从后端获取设备 token，抓取新闻并发送推送通知。

#### 2.3 创建页面入口

在 `frontend/pages/` 文件夹中创建一个名为 `sendNotification.tsx` 的文件，这是应用的入口页面。

**文件路径：`frontend/pages/sendNotification.tsx`**

```typescript
import React from 'react';
import SendNotificationPage from '../components/SendNotificationPage';

const SendNotification = () => {
  return <SendNotificationPage />;
};

export default SendNotification;
```

#### 2.4 启动前端应用

确保前端和后端都在本地运行，使用以下命令启动前端：

```bash
npm run dev
```

### 步骤 3: 测试功能

1. 启动后端 API：在 `backend/` 目录下使用 `uvicorn` 启动 FastAPI：

   ```bash
   uvicorn backend.app:app --reload
   ```

2. 启动前端应用：在 `frontend/` 目录下运行前端开发服务器：

   ```bash
   npm run dev
   ```

3. 访问 `http://localhost:3000/sendNotification` 页面，点击 **Send Notification** 按钮，检查是否能够成功发送包含福克斯新闻头条的推送通知。

### 总结

在此教程中，我们成功地通过以下步骤实现了功能：
- **爬取福克斯新闻网站的头条**：使用 BeautifulSoup 和 requests 库编写了爬虫。
- **获取设备 tokens 并推送通知**：通过前端和后端 API 获取新闻和推送通知。
- **前后端集成**：将爬虫和通知逻辑整合到前后端中，确保应用能动态地推送最新的新闻头条。

这样，你就能够从福克斯新闻网站爬取最新头条并通过推送通知发送给用户！