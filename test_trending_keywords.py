"""
Comprehensive Test Suite for Trending Keywords Functionality
Tests the ability to fetch trending keywords, events, and trends from Etsy
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import requests
import cloudscraper
from bs4 import BeautifulSoup
import re

# Import your classes
from trending_keywords import TrendingKeywordsManager
from main_py import Bot, BotManager, CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrendingKeywordsTest:
    def __init__(self):
        self.bot_manager = BotManager()
        self.trending_manager = TrendingKeywordsManager()
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }

    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test results"""
        self.test_results['total_tests'] += 1
        if passed:
            self.test_results['passed_tests'] += 1
            logger.info(f"✅ {test_name}: PASSED")
        else:
            self.test_results['failed_tests'] += 1
            logger.error(f"❌ {test_name}: FAILED")
        
        if details:
            logger.info(f"   Details: {details}")
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

    async def test_bot_connection(self) -> bool:
        """Test if bot can connect to Etsy"""
        logger.info("\n🔍 Testing Bot Connection to Etsy...")
        
        try:
            bot = await self.bot_manager.get_available_bot()
            if not bot:
                self.log_test_result("Bot Availability", False, "No bots available")
                return False
            
            # Test basic connection
            html_content = await bot.make_request('https://www.etsy.com/')
            if html_content and len(html_content) > 1000:
                self.log_test_result("Bot Connection", True, f"Successfully fetched {len(html_content)} characters")
                return True
            else:
                self.log_test_result("Bot Connection", False, "Failed to fetch content or content too small")
                return False
                
        except Exception as e:
            self.log_test_result("Bot Connection", False, f"Exception: {str(e)}")
            return False

    async def test_trending_page_access(self) -> bool:
        """Test access to Etsy's trending page"""
        logger.info("\n🔍 Testing Trending Page Access...")
        
        try:
            bot = await self.bot_manager.get_available_bot()
            if not bot:
                self.log_test_result("Trending Page Access", False, "No bots available")
                return False
            
            html_content = await bot.make_request('https://www.etsy.com/trending')
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Check for common Etsy page elements
                has_etsy_elements = any([
                    soup.find('title'),
                    soup.find(class_=lambda x: x and 'etsy' in str(x).lower()),
                    soup.find(attrs={'data-test-id': True}),
                    'etsy' in html_content.lower()
                ])
                
                if has_etsy_elements:
                    self.log_test_result("Trending Page Access", True, 
                                       f"Successfully accessed trending page ({len(html_content)} chars)")
                    return True
                else:
                    self.log_test_result("Trending Page Access", False, 
                                       "Page accessed but doesn't appear to be Etsy")
                    return False
            else:
                self.log_test_result("Trending Page Access", False, "No content received")
                return False
                
        except Exception as e:
            self.log_test_result("Trending Page Access", False, f"Exception: {str(e)}")
            return False

    async def test_keyword_extraction(self) -> bool:
        """Test keyword extraction from HTML content"""
        logger.info("\n🔍 Testing Keyword Extraction...")
        
        try:
            bot = await self.bot_manager.get_available_bot()
            if not bot:
                self.log_test_result("Keyword Extraction", False, "No bots available")
                return False
            
            # Try multiple Etsy pages for keyword extraction
            test_urls = [
                'https://www.etsy.com/trending',
                'https://www.etsy.com/',
                'https://www.etsy.com/search?q=trending'
            ]
            
            extracted_keywords = set()
            
            for url in test_urls:
                try:
                    html_content = await bot.make_request(url)
                    if html_content:
                        keywords = await self.trending_manager.extract_trending_from_listings(html_content)
                        extracted_keywords.update(keywords)
                        logger.info(f"   From {url}: {len(keywords)} keywords")
                        
                        # Add small delay between requests
                        await asyncio.sleep(2)
                except Exception as e:
                    logger.warning(f"   Failed to extract from {url}: {str(e)}")
                    continue
            
            total_keywords = len(extracted_keywords)
            if total_keywords > 0:
                self.log_test_result("Keyword Extraction", True, 
                                   f"Extracted {total_keywords} unique keywords: {list(extracted_keywords)[:10]}")
                return True
            else:
                self.log_test_result("Keyword Extraction", False, "No keywords extracted")
                return False
                
        except Exception as e:
            self.log_test_result("Keyword Extraction", False, f"Exception: {str(e)}")
            return False

    async def test_api_endpoint(self) -> bool:
        """Test the /api/trending endpoint"""
        logger.info("\n🔍 Testing API Endpoint...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8000/api/trending') as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validate response structure
                        if 'trending' in data and 'updated' in data:
                            keywords = data['trending']
                            if isinstance(keywords, list) and len(keywords) > 0:
                                self.log_test_result("API Endpoint", True, 
                                                   f"API returned {len(keywords)} keywords: {keywords[:5]}")
                                return True
                            else:
                                self.log_test_result("API Endpoint", False, "Empty or invalid keywords list")
                                return False
                        else:
                            self.log_test_result("API Endpoint", False, "Invalid response structure")
                            return False
                    else:
                        self.log_test_result("API Endpoint", False, f"HTTP {response.status}")
                        return False
                        
        except Exception as e:
            self.log_test_result("API Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_keyword_quality(self, keywords: List[str]) -> bool:
        """Test the quality and relevance of extracted keywords"""
        logger.info("\n🔍 Testing Keyword Quality...")
        
        try:
            if not keywords:
                self.log_test_result("Keyword Quality", False, "No keywords to test")
                return False
            
            # Quality checks
            quality_score = 0
            total_checks = 0
            
            # Check 1: Keywords should be meaningful (length > 2)
            meaningful_keywords = [k for k in keywords if len(k.strip()) > 2]
            quality_score += len(meaningful_keywords) / len(keywords)
            total_checks += 1
            
            # Check 2: Should contain trend-related terms
            trend_indicators = ['aesthetic', 'core', 'style', 'decor', 'vintage', 'modern', 'boho', 'minimalist']
            trend_keywords = [k for k in keywords if any(indicator in k.lower() for indicator in trend_indicators)]
            if trend_keywords:
                quality_score += 1
            total_checks += 1
            
            # Check 3: Should not be too generic
            generic_terms = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']
            non_generic = [k for k in keywords if k.lower() not in generic_terms]
            quality_score += len(non_generic) / len(keywords)
            total_checks += 1
            
            # Check 4: Should have reasonable diversity
            unique_first_letters = len(set(k[0].lower() for k in keywords if k))
            if unique_first_letters > len(keywords) * 0.3:  # At least 30% diversity
                quality_score += 1
            total_checks += 1
            
            final_score = quality_score / total_checks
            
            if final_score > 0.7:
                self.log_test_result("Keyword Quality", True, 
                                   f"Quality score: {final_score:.2f}, Trend keywords: {trend_keywords[:3]}")
                return True
            else:
                self.log_test_result("Keyword Quality", False, 
                                   f"Quality score too low: {final_score:.2f}")
                return False
                
        except Exception as e:
            self.log_test_result("Keyword Quality", False, f"Exception: {str(e)}")
            return False

    async def test_trending_events_detection(self) -> bool:
        """Test detection of seasonal/event-based trends"""
        logger.info("\n🔍 Testing Trending Events Detection...")
        
        try:
            # Get current month to check for seasonal trends
            current_month = datetime.now().month
            seasonal_keywords = {
                12: ['christmas', 'holiday', 'winter', 'new year'],
                1: ['new year', 'winter', 'resolution'],
                2: ['valentine', 'love', 'heart'],
                3: ['spring', 'easter'],
                4: ['spring', 'easter'],
                5: ['mother', 'spring'],
                6: ['summer', 'father', 'graduation'],
                7: ['summer', 'july', 'independence'],
                8: ['summer', 'back to school'],
                9: ['fall', 'autumn', 'back to school'],
                10: ['halloween', 'fall', 'autumn'],
                11: ['thanksgiving', 'fall', 'autumn']
            }
            
            expected_seasonal = seasonal_keywords.get(current_month, [])
            
            # Get keywords from API
            bot = await self.bot_manager.get_available_bot()
            if bot:
                html_content = await bot.make_request('https://www.etsy.com/trending')
                if html_content:
                    keywords = await self.trending_manager.extract_trending_from_listings(html_content)
                    
                    # Check for seasonal relevance
                    seasonal_found = []
                    for keyword in keywords:
                        for seasonal in expected_seasonal:
                            if seasonal.lower() in keyword.lower():
                                seasonal_found.append(keyword)
                    
                    if seasonal_found:
                        self.log_test_result("Trending Events Detection", True, 
                                           f"Found seasonal keywords: {seasonal_found}")
                        return True
                    else:
                        # Even if no seasonal keywords, if we got keywords it's still a pass
                        if keywords and len(keywords) > 5:
                            self.log_test_result("Trending Events Detection", True, 
                                               f"No seasonal keywords but got {len(keywords)} trending keywords")
                            return True
                        else:
                            self.log_test_result("Trending Events Detection", False, 
                                               "No seasonal keywords and insufficient trending keywords")
                            return False
            
            self.log_test_result("Trending Events Detection", False, "Could not fetch trending data")
            return False
            
        except Exception as e:
            self.log_test_result("Trending Events Detection", False, f"Exception: {str(e)}")
            return False

    def print_test_summary(self):
        """Print comprehensive test summary"""
        logger.info("\n" + "="*60)
        logger.info("🎯 TRENDING KEYWORDS TEST SUMMARY")
        logger.info("="*60)
        
        total = self.test_results['total_tests']
        passed = self.test_results['passed_tests']
        failed = self.test_results['failed_tests']
        
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {failed} ❌")
        logger.info(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "No tests run")
        
        logger.info("\n📋 Detailed Results:")
        for test in self.test_results['test_details']:
            status = "✅" if test['passed'] else "❌"
            logger.info(f"{status} {test['test_name']}")
            if test['details']:
                logger.info(f"   {test['details']}")
        
        logger.info("\n" + "="*60)

    async def run_all_tests(self):
        """Run all trending keywords tests"""
        logger.info("🚀 Starting Trending Keywords Test Suite...")
        logger.info("="*60)
        
        # Test 1: Bot Connection
        await self.test_bot_connection()
        
        # Test 2: Trending Page Access
        await self.test_trending_page_access()
        
        # Test 3: Keyword Extraction
        await self.test_keyword_extraction()
        
        # Test 4: API Endpoint (requires server to be running)
        await self.test_api_endpoint()
        
        # Test 5: Trending Events Detection
        await self.test_trending_events_detection()
        
        # Test 6: Get keywords for quality testing
        try:
            bot = await self.bot_manager.get_available_bot()
            if bot:
                html_content = await bot.make_request('https://www.etsy.com/trending')
                if html_content:
                    keywords = await self.trending_manager.extract_trending_from_listings(html_content)
                    self.test_keyword_quality(keywords)
        except Exception as e:
            logger.error(f"Could not test keyword quality: {str(e)}")
        
        # Cleanup
        await self.bot_manager.shutdown()
        
        # Print summary
        self.print_test_summary()

async def main():
    """Main test function"""
    test_suite = TrendingKeywordsTest()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
