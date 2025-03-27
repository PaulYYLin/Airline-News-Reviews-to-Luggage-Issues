from fastapi import FastAPI
from main import trigger_reddit_spider
from fastapi import Request
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Test"}


@app.post("/get_reddit_posts")
async def get_reddit_posts(request: Request):
    request_data = await request.json()
    response = trigger_reddit_spider(**request_data)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    request_data = {
        "time_filter": "month",
        "limit": 1,
        "subreddit_name": "all",
        "sort": "new"
    }
    get_reddit_posts(request_data)

