import json
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from typing import List, Union, Dict, Any
import uvicorn
import os

app = FastAPI(title="Async Web Crawler API", description="Extract Markdown from web pages")

# Security
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API key from Authorization header"""
    api_key = os.getenv("API_KEY", "admin")  # Default to "admin" if not set
    if credentials.credentials != api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

class CrawlRequest(BaseModel):
    url: HttpUrl
    max_depth: int = 1

class CrawlResult(BaseModel):
    url: str
    markdown: str

async def crawl_url(url: str, max_depth: int) -> Union[List[CrawlResult], CrawlResult]:
    # Configure the crawl
    config = CrawlerRunConfig(
        magic=True,
        cache_mode=CacheMode.BYPASS,
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=max_depth, 
            include_external=False
        ) if max_depth > 0 else None,
        verbose=True
    )

    try:
        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun(url, config=config)
            return [CrawlResult(url=result.url, markdown=str(result._markdown)) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawling failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Async Web Crawler API", "docs": "/docs", "auth": "Required - use Authorization: Bearer <API_KEY>"}

@app.post("/crawl", response_model=Union[List[CrawlResult], CrawlResult])
async def crawl_endpoint(request: CrawlRequest, api_key: str = Depends(verify_api_key)):
    """
    Crawl a URL and extract Markdown content.
    
    - **url**: The starting URL to crawl
    - **max_depth**: Maximum depth for deep crawling (0 = single page, >0 = deep crawl)
    
    Requires Authorization header with Bearer token (API key).
    """
    return await crawl_url(str(request.url), request.max_depth)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
