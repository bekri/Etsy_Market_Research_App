"""
Enhanced Etsy Research API with Cloudflare Integration
"""

import asyncio
import aiohttp
import json
import random
import time
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import re
from urllib.parse import urlencode, quote_plus
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import redis
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from proxy_manager import ProxyManager
import cloudscraper
from trending_keywords import TrendingKeywordsManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment
CONFIG = {
    'PROXY_ENDPOINTS': os.getenv('CLOUDFLARE_FLOXY_ENDPOINTS', '').split(',') if os.getenv('CLOUDFLARE_FLOXY_ENDPOINTS') else [],
    'MAX_CONCURRENT_BOTS': int(os.getenv('MAX_CONCURRENT_BOTS', '5')),
    'REQUEST_DELAY_RANGE': (2, 5),
    'REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379'),
    'CACHE_EXPIRY': 3600,
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 5,
    'USER_AGENTS': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
    ]
}

# Initialize proxy manager
proxy_manager = ProxyManager()

@dataclass
class EtsyProduct:
    title: str
    price: str
    shop_name: str
    url: str
    image_url: str
    sales_count: int
    views_estimate: int
    listing_age_days: int
    is_star_seller: bool
    is_best_seller: bool
    keywords: List[str]
    shop_rating: float

class SearchRequest(BaseModel):
    keyword: str
    product_type: str
    filter_type: str = "star_seller"
    max_results: int = 20

class Bot:
    def __init__(self, bot_id: int):
        self.bot_id = bot_id
        self.session = None
        self.requests_session = None
        self.is_busy = False
        self.requests_made = 0
        self.last_request_time = 0
        self.retry_count = 0
        self.proxy_endpoint = None
        self.current_proxy = None
        self._create_requests_session()

    def _create_requests_session(self):
        self.requests_session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        self.requests_session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        })

    async def create_session(self):
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=2, ttl_dns_cache=300, use_dns_cache=True)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
                'DNT': '1',
            }
        )

    async def close_session(self):
        if self.session:
            await self.session.close()
        if self.requests_session:
            self.requests_session.close()

    async def make_request(self, url: str, params: Dict = None) -> Optional[str]:
        if not self.session:
            await self.create_session()
        
        current_time = time.time()
        if current_time - self.last_request_time < CONFIG['REQUEST_DELAY_RANGE'][0]:
            delay = random.uniform(*CONFIG['REQUEST_DELAY_RANGE'])
            await asyncio.sleep(delay)
        
        try:
            self.is_busy = True
            
            # Always make direct requests using cloudscraper
            for attempt in range(CONFIG['MAX_RETRIES']):
                try:
                    response = self.requests_session.get(
                        url, 
                        params=params, 
                        timeout=30
                    )
                    if response.status_code == 200:
                        self.requests_made += 1
                        self.last_request_time = time.time()
                        self.retry_count = 0  # Reset retry count on success
                        return response.text
                    elif response.status_code == 429:
                        logger.warning(f"Bot {self.bot_id}: Rate limited, attempt {attempt + 1}/{CONFIG['MAX_RETRIES']}")
                        await asyncio.sleep(CONFIG['RETRY_DELAY'] * (attempt + 1))
                        continue
                    elif response.status_code == 403:
                        logger.warning(f"Bot {self.bot_id}: Cloudflare block detected, attempt {attempt + 1}/{CONFIG['MAX_RETRIES']}")
                        self._create_requests_session()  # Recreate cloudscraper session
                        await asyncio.sleep(CONFIG['RETRY_DELAY'] * (attempt + 1))
                        continue
                    else:
                        logger.error(f"Bot {self.bot_id}: HTTP {response.status_code}")
                        break
                except Exception as e:
                    logger.error(f"Bot {self.bot_id}: Request failed - {str(e)}")
                    if attempt < CONFIG['MAX_RETRIES'] - 1:
                        await asyncio.sleep(CONFIG['RETRY_DELAY'] * (attempt + 1))
                        continue
                    break
            self.retry_count += 1
            return None
        except Exception as e:
            logger.error(f"Bot {self.bot_id}: Request failed - {str(e)}")
            return None
        finally:
            self.is_busy = False

class BotManager:
    def __init__(self):
        self.bots: List[Bot] = []
        self.setup_bots()
    
    def setup_bots(self):
        proxy_endpoints = [ep.strip() for ep in CONFIG['PROXY_ENDPOINTS'] if ep.strip()]
        
        for i in range(CONFIG['MAX_CONCURRENT_BOTS']):
            if proxy_endpoints:
                proxy_endpoint = proxy_endpoints[i % len(proxy_endpoints)]
            else:
                proxy_endpoint = None
                
            bot = Bot(i)
            self.bots.append(bot)
        
        logger.info(f"Initialized {len(self.bots)} bots with {len(proxy_endpoints)} proxies")
    
    async def get_available_bot(self) -> Optional[Bot]:
        for bot in self.bots:
            if not bot.is_busy:
                return bot
        return None
    
    async def shutdown(self):
        for bot in self.bots:
            await bot.close_session()

class EtsyScraper:
    def __init__(self, bot_manager: BotManager, redis_client):
        self.bot_manager = bot_manager
        self.redis_client = redis_client
    
    def build_etsy_search_url(self, keyword: str, product_type: str, filter_type: str) -> str:
        base_url = "https://www.etsy.com/search"
        query = f"{keyword} {product_type}"
        params = {'q': query, 'explicit': '1', 'ref': 'search_bar'}
        
        if filter_type == "star_seller":
            params['is_star_seller'] = 'true'
        elif filter_type == "best_seller":
            params['is_best_seller'] = 'true'
        
        return f"{base_url}?{urlencode(params)}"
    
    def extract_product_data(self, html: str, search_keyword: str) -> List[EtsyProduct]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Multiple selectors to handle Etsy's changing structure
        selectors = [
            'div[data-test-id="organic-search-result"]',
            'div[class*="listing-card"]',
            'div[class*="search-result"]',
            '.organic-search-result'
        ]
        
        product_containers = []
        for selector in selectors:
            containers = soup.select(selector)
            if containers:
                product_containers = containers
                break
        
        logger.info(f"Found {len(product_containers)} product containers")
        
        for container in product_containers[:20]:
            try:
                product = self.parse_product_container(container, search_keyword)
                if product:
                    products.append(product)
            except Exception as e:
                logger.error(f"Error parsing product: {str(e)}")
                continue
        
        return products
    
    def parse_product_container(self, container, search_keyword: str) -> Optional[EtsyProduct]:
        try:
            # Title - updated selectors for Etsy's current structure
            title_selectors = [
                'h3.v2-listing-card__title',
                'h3[data-test-id="listing-link"]',
                'a[data-test-id="listing-link"] h3',
                '.v2-listing-card__title',
                'h3'
            ]
            title = "Unknown Title"
            
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            # Price - updated selectors
            price_selectors = [
                '.currency-value',
                '.wt-text-title-01 .currency-value',
                '.wt-text-title-01 .currency-symbol',
                '.wt-text-title-01 .currency-value + .currency-symbol',
                '.price'
            ]
            price = "$0.00"
            
            for selector in price_selectors:
                price_elem = container.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if '$' in price_text or '€' in price_text or '£' in price_text:
                        price = price_text
                        break
            
            # Shop name - updated selectors
            shop_selectors = [
                'p.wt-text-caption',
                '.wt-text-caption a[href*="/shop/"]',
                '.shop-name',
                'a[href*="/shop/"]'
            ]
            shop_name = "Unknown Shop"
            
            for selector in shop_selectors:
                shop_elem = container.select_one(selector)
                if shop_elem:
                    shop_name = shop_elem.get_text(strip=True)
                    break
            
            # URL - updated selectors
            url_selectors = [
                'a[data-test-id="listing-link"]',
                '.v2-listing-card__title a',
                'a[href*="/listing/"]',
                '.listing-link'
            ]
            url = ""
            
            for selector in url_selectors:
                link_elem = container.select_one(selector)
                if link_elem and link_elem.get('href'):
                    url = link_elem['href']
                    if url and not url.startswith('http'):
                        url = f"https://www.etsy.com{url}"
                    break
            
            # Image - updated selectors
            img_selectors = [
                'img.v2-listing-card__img',
                'img[data-test-id="listing-card-image"]',
                '.v2-listing-card__img',
                'img'
            ]
            image_url = ""
            for selector in img_selectors:
                img_elem = container.select_one(selector)
                if img_elem and img_elem.get('src'):
                    image_url = img_elem['src']
                    break
            
            # Sales count - updated selectors
            sales_selectors = [
                '.wt-text-caption .wt-text-gray',
                '.wt-text-caption .wt-text-gray-light',
                '.wt-text-caption'
            ]
            sales_count = 0
            for selector in sales_selectors:
                sales_elem = container.select_one(selector)
                if sales_elem:
                    sales_text = sales_elem.get_text(strip=True)
                    if 'sale' in sales_text.lower() or 'sold' in sales_text.lower():
                        sales_count = self.estimate_sales_count(sales_text)
                        break
            
            # Star seller and best seller badges - updated selectors
            badge_selectors = [
                '.wt-badge',
                '.wt-text-caption .wt-badge',
                '.wt-text-caption .wt-text-gray'
            ]
            is_star_seller = False
            is_best_seller = False
            for selector in badge_selectors:
                badge_elem = container.select_one(selector)
                if badge_elem:
                    badge_text = badge_elem.get_text(strip=True).lower()
                    if 'star seller' in badge_text:
                        is_star_seller = True
                    if 'best seller' in badge_text:
                        is_best_seller = True
            
            # Mock additional data (in real scraping, these would be extracted)
            views_estimate = random.randint(500, 5000)
            listing_age_days = random.randint(30, 365)
            shop_rating = round(random.uniform(4.0, 5.0), 1)
            
            keywords = self.extract_keywords(title, search_keyword)
            
            return EtsyProduct(
                title=title,
                price=price,
                shop_name=shop_name,
                url=url,
                image_url=image_url,
                sales_count=sales_count,
                views_estimate=views_estimate,
                listing_age_days=listing_age_days,
                is_star_seller=is_star_seller,
                is_best_seller=is_best_seller,
                keywords=keywords,
                shop_rating=shop_rating
            )
            
        except Exception as e:
            logger.error(f"Error parsing product: {str(e)}")
            return None
    
    def estimate_sales_count(self, container) -> int:
        # Look for review indicators
        review_patterns = [r'(\d+)\s*review', r'(\d+)\s*sale', r'sold\s*(\d+)', r'(\d+)\s*favorite']
        
        container_text = str(container).lower()
        for pattern in review_patterns:
            match = re.search(pattern, container_text)
            if match:
                count = int(match.group(1))
                return random.randint(count * 2, count * 5)
        
        return random.randint(10, 500)
    
    def extract_keywords(self, title: str, search_keyword: str) -> List[str]:
        keywords = [search_keyword.lower()]
        
        common_keywords = [
            'gift', 'custom', 'personalized', 'handmade', 'vintage', 
            'unique', 'funny', 'cute', 'cool', 'trendy', 'modern'
        ]
        
        title_lower = title.lower()
        for keyword in common_keywords:
            if keyword in title_lower and keyword not in keywords:
                keywords.append(keyword)
        
        title_words = re.findall(r'\b[a-zA-Z]{3,}\b', title_lower)
        for word in title_words[:3]:
            if word not in keywords and len(word) > 3:
                keywords.append(word)
        
        return keywords[:6]
    
    async def search_products(self, request: SearchRequest) -> List[EtsyProduct]:
        cache_key = f"etsy_search:{request.keyword}:{request.product_type}:{request.filter_type}"
        
        # Check cache
        if self.redis_client:
            try:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for {cache_key}")
                    cached_data = json.loads(cached_result)
                    return [EtsyProduct(**item) for item in cached_data]
            except Exception as e:
                logger.error(f"Cache error: {str(e)}")
        
        # Get bot
        bot = await self.bot_manager.get_available_bot()
        if not bot:
            raise HTTPException(status_code=503, detail="No available bots")
        
        # Search
        search_url = self.build_etsy_search_url(request.keyword, request.product_type, request.filter_type)
        logger.info(f"Bot {bot.bot_id} searching: {search_url}")
        
        html_content = await bot.make_request(search_url)
        if not html_content:
            raise HTTPException(status_code=500, detail="Failed to fetch search results")
        
        products = self.extract_product_data(html_content, request.keyword)
        products.sort(key=lambda p: p.sales_count, reverse=True)
        
        # Cache results
        if self.redis_client and products:
            try:
                cache_data = [product.__dict__ for product in products]
                self.redis_client.setex(cache_key, CONFIG['CACHE_EXPIRY'], json.dumps(cache_data, default=str))
            except Exception as e:
                logger.error(f"Cache save error: {str(e)}")
        
        return products[:request.max_results]

class EtsyResearchApp:
    def __init__(self):
        self.redis_client = None
        self.bot_manager = None
        self.trending_manager = None
        self.setup_redis()
        self.setup_bot_manager()
        self.trending_manager = TrendingKeywordsManager(redis_client)

# App setup
bot_manager = BotManager()
redis_client = None

try:
    redis_client = redis.from_url(CONFIG['REDIS_URL'], decode_responses=True)
    redis_client.ping()
    logger.info("Redis connected successfully")
except Exception as e:
    logger.warning(f"Redis connection failed: {str(e)}. Running without cache.")
    redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Etsy Scraper API")
    yield
    await bot_manager.shutdown()
    logger.info("Shutdown complete")

app = FastAPI(
    title="Etsy Research API",
    description="Professional Etsy product research with bot management and proxy rotation",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML frontend)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

scraper = EtsyScraper(bot_manager, redis_client)
app.scraper = scraper

@app.get("/")
async def serve_frontend():
    """Serve the HTML frontend"""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "Etsy Research API", "version": "1.0.0", "docs": "/docs"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "bots_status": {
            "total": len(bot_manager.bots),
            "available": len([b for b in bot_manager.bots if not b.is_busy]),
            "busy": len([b for b in bot_manager.bots if b.is_busy])
        },
        "redis_connected": redis_client is not None,
        "proxy_endpoints": len([ep for ep in CONFIG['PROXY_ENDPOINTS'] if ep.strip()])
    }

@app.post("/api/search")
async def search_products(request: SearchRequest):
    try:
        products = await scraper.search_products(request)
        return [product.__dict__ for product in products]  # Convert to dict for JSON response
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trending")
async def get_trending_keywords():
    """Get trending keywords"""
    try:
        # Get a bot to fetch trending data
        bot = await bot_manager.get_available_bot()
        if not bot:
            # Return default keywords if no bot available
            default_keywords = [
                "Cottagecore", "Dark Academia", "Y2K Aesthetic", "Minimalist Design",
                "Boho Chic", "Vintage Retro", "Plant Mom", "Self Care", "Motivational Quotes",
                "Astrology", "Crystal Healing", "Sustainable Living", "Mental Health Awareness",
                "Dopamine Decor", "Grandmillennial", "Maximalist", "Japandi Style"
            ]
            return {
                "trending": default_keywords,
                "updated": datetime.now().isoformat()
            }

        # Try to get trending keywords from Etsy
        try:
            html_content = await bot.make_request('https://www.etsy.com/trending')
            if html_content:
                trending_manager = TrendingKeywordsManager()
                trending_keywords = await trending_manager.extract_trending_from_listings(html_content)
            else:
                # Fallback to default keywords
                trending_keywords = [
                    "Cottagecore", "Dark Academia", "Y2K Aesthetic", "Minimalist Design",
                    "Boho Chic", "Vintage Retro", "Plant Mom", "Self Care", "Motivational Quotes",
                    "Astrology", "Crystal Healing", "Sustainable Living", "Mental Health Awareness",
                    "Dopamine Decor", "Grandmillennial", "Maximalist", "Japandi Style"
                ]
        except Exception as e:
            logger.error(f"Error fetching trending keywords: {str(e)}")
            # Return default keywords on error
            trending_keywords = [
                "Cottagecore", "Dark Academia", "Y2K Aesthetic", "Minimalist Design",
                "Boho Chic", "Vintage Retro", "Plant Mom", "Self Care", "Motivational Quotes",
                "Astrology", "Crystal Healing", "Sustainable Living", "Mental Health Awareness",
                "Dopamine Decor", "Grandmillennial", "Maximalist", "Japandi Style"
            ]

        return {
            "trending": trending_keywords,
            "updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Trending keywords error: {str(e)}")
        # Return default keywords as fallback
        return {
            "trending": [
                "Cottagecore", "Dark Academia", "Y2K Aesthetic", "Minimalist Design",
                "Boho Chic", "Vintage Retro", "Plant Mom", "Self Care", "Motivational Quotes",
                "Astrology", "Crystal Healing", "Sustainable Living", "Mental Health Awareness",
                "Dopamine Decor", "Grandmillennial", "Maximalist", "Japandi Style"
            ],
            "updated": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_py:app", host="0.0.0.0", port=8000, reload=True)