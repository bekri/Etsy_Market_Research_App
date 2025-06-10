"""
Test script for Etsy Research API
"""

import asyncio
import aiohttp
import json
from datetime import datetime
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_health_check():
    """Test the health check endpoint"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://localhost:8000/api/health') as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ Health check passed")
                    logger.info(f"Status: {data}")
                    return True
                else:
                    logger.error(f"❌ Health check failed with status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Health check error: {str(e)}")
            return False

async def test_search_products():
    """Test the search products endpoint"""
    test_cases = [
        {
            "keyword": "vintage necklace",
            "product_type": "jewelry",
            "filter_type": "star_seller",
            "max_results": 5
        },
        {
            "keyword": "handmade soap",
            "product_type": "bath",
            "filter_type": "best_seller",
            "max_results": 3
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test_case in test_cases:
            try:
                logger.info(f"\nTesting search with: {test_case}")
                async with session.post(
                    'http://localhost:8000/api/search',
                    json=test_case
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Search successful for {test_case['keyword']}")
                        logger.info(f"Found {len(data)} products")
                        
                        # Validate product data
                        for product in data:
                            required_fields = [
                                'title', 'price', 'shop_name', 'url', 
                                'image_url', 'sales_count', 'views_estimate',
                                'listing_age_days', 'is_star_seller', 
                                'is_best_seller', 'keywords', 'shop_rating'
                            ]
                            
                            missing_fields = [field for field in required_fields if field not in product]
                            if missing_fields:
                                logger.error(f"❌ Missing fields in product: {missing_fields}")
                            else:
                                logger.info(f"✅ Product data complete: {product['title']}")
                    else:
                        logger.error(f"❌ Search failed with status {response.status}")
                        error_text = await response.text()
                        logger.error(f"Error details: {error_text}")
            except Exception as e:
                logger.error(f"❌ Search error: {str(e)}")

async def test_trending_keywords():
    """Test the trending keywords endpoint"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://localhost:8000/api/trending') as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ Trending keywords retrieved")
                    logger.info(f"Found {len(data)} trending keywords")
                    return True
                else:
                    logger.error(f"❌ Trending keywords failed with status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Trending keywords error: {str(e)}")
            return False

async def run_tests():
    """Run all tests"""
    logger.info("Starting API tests...")
    
    # Test health check
    health_check_passed = await test_health_check()
    if not health_check_passed:
        logger.error("❌ Health check failed, stopping tests")
        return
    
    # Test search products
    await test_search_products()
    
    # Test trending keywords
    await test_trending_keywords()
    
    logger.info("\nTest summary:")
    logger.info("✅ Health check test completed")
    logger.info("✅ Search products test completed")
    logger.info("✅ Trending keywords test completed")

if __name__ == "__main__":
    asyncio.run(run_tests()) 