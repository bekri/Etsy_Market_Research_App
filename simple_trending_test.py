"""
Simple Trending Keywords Test
Quick test to verify trending keyword extraction is working
"""

import asyncio
import cloudscraper
import logging
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleTrendingTest:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        self.scraper.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        })

    def fetch_etsy_page(self, url: str) -> str:
        """Fetch Etsy page content"""
        try:
            logger.info(f"🔍 Fetching: {url}")
            response = self.scraper.get(url, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully fetched {len(response.text)} characters")
                return response.text
            else:
                logger.error(f"❌ HTTP {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error fetching page: {str(e)}")
            return ""

    def extract_trending_keywords(self, html_content: str) -> List[str]:
        """Extract trending keywords from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            trending_keywords = set()
            
            logger.info("🔍 Looking for trending sections...")
            
            # Method 1: Look for trending/popular sections
            trending_sections = soup.find_all(['div', 'section'], 
                class_=lambda x: x and any(term in str(x).lower() for term in ['trending', 'popular', 'hot']))
            
            logger.info(f"Found {len(trending_sections)} trending sections")
            
            for section in trending_sections:
                keywords = section.find_all(['a', 'span', 'div'], 
                    class_=lambda x: x and any(term in str(x).lower() for term in ['keyword', 'tag', 'trend']))
                for keyword in keywords:
                    text = keyword.get_text(strip=True)
                    if text and len(text) > 2 and len(text) < 50:
                        trending_keywords.add(text)
            
            # Method 2: Extract from product titles and popular searches
            logger.info("🔍 Looking for product titles...")
            
            # Look for search suggestions or popular terms
            search_suggestions = soup.find_all(['a', 'span'], 
                class_=lambda x: x and any(term in str(x).lower() for term in ['search', 'suggestion', 'popular']))
            
            for suggestion in search_suggestions:
                text = suggestion.get_text(strip=True)
                if text and len(text) > 2 and len(text) < 50:
                    trending_keywords.add(text)
            
            # Method 3: Look for category links and popular items
            category_links = soup.find_all('a', href=lambda x: x and '/c/' in str(x))
            for link in category_links:
                text = link.get_text(strip=True)
                if text and len(text) > 2 and len(text) < 30:
                    trending_keywords.add(text)
            
            # Method 4: Extract from meta tags and structured data
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and meta_keywords.get('content'):
                keywords = meta_keywords['content'].split(',')
                for keyword in keywords:
                    keyword = keyword.strip()
                    if keyword and len(keyword) > 2:
                        trending_keywords.add(keyword)
            
            # Method 5: Look for trending hashtags or tags
            hashtags = soup.find_all(text=re.compile(r'#\w+'))
            for hashtag in hashtags:
                clean_tag = hashtag.strip().replace('#', '')
                if clean_tag and len(clean_tag) > 2:
                    trending_keywords.add(clean_tag)
            
            # Convert to list and filter
            keywords_list = list(trending_keywords)
            
            # Filter out common non-trending words
            filtered_keywords = []
            common_words = {'home', 'shop', 'etsy', 'search', 'cart', 'account', 'help', 'sign', 'in', 'out', 'up'}
            
            for keyword in keywords_list:
                if keyword.lower() not in common_words and not keyword.isdigit():
                    filtered_keywords.append(keyword)
            
            logger.info(f"✅ Extracted {len(filtered_keywords)} trending keywords")
            return filtered_keywords[:20]  # Return top 20
            
        except Exception as e:
            logger.error(f"❌ Error extracting keywords: {str(e)}")
            return []

    def analyze_keywords(self, keywords: List[str]) -> dict:
        """Analyze the quality and relevance of keywords"""
        analysis = {
            'total_keywords': len(keywords),
            'trend_indicators': [],
            'seasonal_keywords': [],
            'aesthetic_keywords': [],
            'quality_score': 0
        }
        
        # Look for trend indicators
        trend_terms = ['aesthetic', 'core', 'style', 'trend', 'viral', 'popular', 'hot']
        for keyword in keywords:
            for term in trend_terms:
                if term in keyword.lower():
                    analysis['trend_indicators'].append(keyword)
        
        # Look for seasonal keywords
        current_month = datetime.now().month
        seasonal_terms = {
            12: ['christmas', 'holiday', 'winter', 'festive'],
            1: ['new year', 'winter', 'resolution'],
            2: ['valentine', 'love', 'heart', 'romantic'],
            3: ['spring', 'easter', 'fresh'],
            10: ['halloween', 'spooky', 'autumn', 'fall'],
            11: ['thanksgiving', 'gratitude', 'autumn']
        }
        
        current_seasonal = seasonal_terms.get(current_month, [])
        for keyword in keywords:
            for term in current_seasonal:
                if term in keyword.lower():
                    analysis['seasonal_keywords'].append(keyword)
        
        # Look for aesthetic keywords
        aesthetic_terms = ['cottagecore', 'dark academia', 'minimalist', 'boho', 'vintage', 'modern', 'rustic']
        for keyword in keywords:
            for term in aesthetic_terms:
                if term in keyword.lower():
                    analysis['aesthetic_keywords'].append(keyword)
        
        # Calculate quality score
        score = 0
        if analysis['total_keywords'] > 5:
            score += 25
        if analysis['trend_indicators']:
            score += 25
        if analysis['aesthetic_keywords']:
            score += 25
        if len(set(k[0].lower() for k in keywords if k)) > len(keywords) * 0.3:
            score += 25
        
        analysis['quality_score'] = score
        
        return analysis

    def test_trending_extraction(self):
        """Main test function"""
        logger.info("🚀 Starting Simple Trending Keywords Test")
        logger.info("="*50)
        
        # Test URLs
        test_urls = [
            'https://www.etsy.com/trending',
            'https://www.etsy.com/',
            'https://www.etsy.com/search?q=trending'
        ]
        
        all_keywords = set()
        successful_extractions = 0
        
        for url in test_urls:
            logger.info(f"\n📍 Testing URL: {url}")
            
            html_content = self.fetch_etsy_page(url)
            if html_content:
                keywords = self.extract_trending_keywords(html_content)
                if keywords:
                    successful_extractions += 1
                    all_keywords.update(keywords)
                    logger.info(f"✅ Extracted keywords: {keywords[:5]}...")
                else:
                    logger.warning("⚠️ No keywords extracted from this page")
            else:
                logger.error("❌ Failed to fetch page content")
        
        # Analyze results
        final_keywords = list(all_keywords)
        analysis = self.analyze_keywords(final_keywords)
        
        # Print results
        logger.info("\n" + "="*50)
        logger.info("📊 TEST RESULTS")
        logger.info("="*50)
        
        logger.info(f"🎯 Total unique keywords extracted: {analysis['total_keywords']}")
        logger.info(f"📈 Successful extractions: {successful_extractions}/{len(test_urls)}")
        logger.info(f"⭐ Quality score: {analysis['quality_score']}/100")
        
        if final_keywords:
            logger.info(f"\n🔥 Sample keywords: {final_keywords[:10]}")
        
        if analysis['trend_indicators']:
            logger.info(f"📊 Trend indicators found: {analysis['trend_indicators']}")
        
        if analysis['seasonal_keywords']:
            logger.info(f"🗓️ Seasonal keywords: {analysis['seasonal_keywords']}")
        
        if analysis['aesthetic_keywords']:
            logger.info(f"🎨 Aesthetic keywords: {analysis['aesthetic_keywords']}")
        
        # Overall assessment
        if analysis['quality_score'] >= 75:
            logger.info("\n✅ EXCELLENT: Trending keyword extraction is working very well!")
        elif analysis['quality_score'] >= 50:
            logger.info("\n✅ GOOD: Trending keyword extraction is working adequately")
        elif analysis['quality_score'] >= 25:
            logger.info("\n⚠️ FAIR: Trending keyword extraction needs improvement")
        else:
            logger.info("\n❌ POOR: Trending keyword extraction is not working properly")
        
        # Save results to file
        results = {
            'timestamp': datetime.now().isoformat(),
            'keywords': final_keywords,
            'analysis': analysis,
            'test_urls': test_urls,
            'successful_extractions': successful_extractions
        }
        
        with open('trending_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n💾 Results saved to 'trending_test_results.json'")
        logger.info("="*50)
        
        return analysis['quality_score'] >= 50

def main():
    """Run the simple trending test"""
    test = SimpleTrendingTest()
    success = test.test_trending_extraction()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n⚠️ Test completed with issues - check the logs above")

if __name__ == "__main__":
    main()
