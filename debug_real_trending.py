"""
Debug Real Trending Keywords Extraction
This script tests the improved trending keyword extraction to get REAL data from Etsy
"""

import asyncio
import cloudscraper
import logging
from bs4 import BeautifulSoup
from datetime import datetime
import json
from trending_keywords import TrendingKeywordsManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTrendingDebugger:
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
        self.trending_manager = TrendingKeywordsManager()

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

    def analyze_page_structure(self, html_content: str, url: str):
        """Analyze the structure of the fetched page"""
        logger.info(f"\n🔍 ANALYZING PAGE STRUCTURE FOR: {url}")
        logger.info("="*60)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check page title
        title = soup.find('title')
        if title:
            logger.info(f"📄 Page Title: {title.get_text(strip=True)}")
        
        # Look for product titles
        title_selectors = [
            'h3[data-test-id="listing-link"]',
            'h3.v2-listing-card__title',
            'a[data-test-id="listing-link"] h3',
            '.v2-listing-card__title',
            'h3',
            '.listing-link h3'
        ]
        
        for selector in title_selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"🎯 Found {len(elements)} elements with selector: {selector}")
                # Show first few examples
                for i, elem in enumerate(elements[:3]):
                    text = elem.get_text(strip=True)
                    logger.info(f"   Example {i+1}: {text}")
                break
        
        # Look for search links
        search_links = soup.select('a[href*="/search?q="]')
        if search_links:
            logger.info(f"🔍 Found {len(search_links)} search links")
            for i, link in enumerate(search_links[:3]):
                text = link.get_text(strip=True)
                href = link.get('href', '')
                logger.info(f"   Search {i+1}: {text} -> {href}")
        
        # Look for category links
        category_links = soup.select('a[href*="/c/"]')
        if category_links:
            logger.info(f"📂 Found {len(category_links)} category links")
            for i, link in enumerate(category_links[:3]):
                text = link.get_text(strip=True)
                href = link.get('href', '')
                logger.info(f"   Category {i+1}: {text} -> {href}")

    async def test_real_extraction(self):
        """Test real trending keyword extraction"""
        logger.info("🚀 TESTING REAL TRENDING KEYWORD EXTRACTION")
        logger.info("="*60)
        
        # Test different Etsy pages
        test_urls = [
            'https://www.etsy.com/',
            'https://www.etsy.com/trending',
            'https://www.etsy.com/search?q=trending',
            'https://www.etsy.com/search?q=popular',
            'https://www.etsy.com/featured/trending-now'
        ]
        
        all_extracted_keywords = {}
        
        for url in test_urls:
            logger.info(f"\n📍 TESTING URL: {url}")
            logger.info("-" * 40)
            
            # Fetch the page
            html_content = self.fetch_etsy_page(url)
            
            if not html_content:
                logger.error(f"❌ Failed to fetch content from {url}")
                continue
            
            # Analyze page structure
            self.analyze_page_structure(html_content, url)
            
            # Extract keywords using our improved method
            try:
                keywords = await self.trending_manager.extract_trending_from_listings(html_content)
                all_extracted_keywords[url] = keywords
                
                logger.info(f"\n✅ EXTRACTED KEYWORDS FROM {url}:")
                logger.info(f"📊 Total keywords: {len(keywords)}")
                
                if keywords:
                    # Check if these are real or default keywords
                    default_keywords = self.trending_manager.default_keywords
                    real_keywords = [k for k in keywords if k not in default_keywords]
                    
                    if real_keywords:
                        logger.info(f"🎯 REAL KEYWORDS ({len(real_keywords)}): {real_keywords}")
                    else:
                        logger.warning("⚠️ Only default keywords returned - extraction may have failed")
                    
                    logger.info(f"📝 All keywords: {keywords}")
                else:
                    logger.error("❌ No keywords extracted")
                    
            except Exception as e:
                logger.error(f"❌ Error extracting keywords: {str(e)}")
                all_extracted_keywords[url] = []
            
            # Small delay between requests
            await asyncio.sleep(2)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("📊 EXTRACTION SUMMARY")
        logger.info("="*60)
        
        total_unique_keywords = set()
        successful_extractions = 0
        
        for url, keywords in all_extracted_keywords.items():
            if keywords:
                successful_extractions += 1
                total_unique_keywords.update(keywords)
                logger.info(f"✅ {url}: {len(keywords)} keywords")
            else:
                logger.info(f"❌ {url}: No keywords")
        
        logger.info(f"\n🎯 FINAL RESULTS:")
        logger.info(f"   Successful extractions: {successful_extractions}/{len(test_urls)}")
        logger.info(f"   Total unique keywords: {len(total_unique_keywords)}")
        
        if total_unique_keywords:
            # Check how many are real vs default
            default_keywords = set(self.trending_manager.default_keywords)
            real_keywords = total_unique_keywords - default_keywords
            
            logger.info(f"   Real keywords found: {len(real_keywords)}")
            logger.info(f"   Default keywords: {len(total_unique_keywords & default_keywords)}")
            
            if real_keywords:
                logger.info(f"\n🔥 REAL TRENDING KEYWORDS DISCOVERED:")
                for keyword in sorted(real_keywords):
                    logger.info(f"   • {keyword}")
            
            # Save results
            results = {
                'timestamp': datetime.now().isoformat(),
                'test_urls': test_urls,
                'successful_extractions': successful_extractions,
                'total_unique_keywords': len(total_unique_keywords),
                'real_keywords_found': len(real_keywords),
                'all_keywords': list(total_unique_keywords),
                'real_keywords': list(real_keywords),
                'extraction_details': all_extracted_keywords
            }
            
            with open('real_trending_debug_results.json', 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"\n💾 Results saved to 'real_trending_debug_results.json'")
            
            # Assessment
            if len(real_keywords) >= 10:
                logger.info("\n🎉 EXCELLENT: Successfully extracting real trending keywords!")
            elif len(real_keywords) >= 5:
                logger.info("\n✅ GOOD: Extracting some real keywords, but could be improved")
            elif len(real_keywords) >= 1:
                logger.info("\n⚠️ FAIR: Found some real keywords, but extraction needs work")
            else:
                logger.info("\n❌ POOR: Not finding real keywords - extraction method needs improvement")
        
        return len(total_unique_keywords - default_keywords) > 0

    def save_sample_html(self, url: str):
        """Save a sample of HTML for manual inspection"""
        logger.info(f"\n💾 Saving sample HTML from {url}")
        
        html_content = self.fetch_etsy_page(url)
        if html_content:
            # Save first 50KB for inspection
            sample_html = html_content[:50000]
            
            filename = f"etsy_sample_{url.split('/')[-1] or 'homepage'}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(sample_html)
            
            logger.info(f"✅ Sample HTML saved to {filename}")
            
            # Also extract and save just the titles for inspection
            soup = BeautifulSoup(html_content, 'html.parser')
            titles = []
            
            title_selectors = [
                'h3[data-test-id="listing-link"]',
                'h3.v2-listing-card__title',
                'a[data-test-id="listing-link"] h3',
                '.v2-listing-card__title',
                'h3'
            ]
            
            for selector in title_selectors:
                elements = soup.select(selector)
                if elements:
                    for elem in elements[:20]:  # First 20 titles
                        title = elem.get_text(strip=True)
                        if title:
                            titles.append(title)
                    break
            
            if titles:
                titles_filename = f"etsy_titles_{url.split('/')[-1] or 'homepage'}.txt"
                with open(titles_filename, 'w', encoding='utf-8') as f:
                    for title in titles:
                        f.write(f"{title}\n")
                
                logger.info(f"✅ Product titles saved to {titles_filename}")

async def main():
    """Main debug function"""
    debugger = RealTrendingDebugger()
    
    logger.info("🎯 REAL TRENDING KEYWORDS DEBUGGER")
    logger.info("This will test if we can extract REAL trending data from Etsy")
    logger.info("="*60)
    
    # Test the extraction
    success = await debugger.test_real_extraction()
    
    # Save sample HTML for manual inspection
    debugger.save_sample_html('https://www.etsy.com/')
    
    if success:
        print("\n🎉 SUCCESS: Found real trending keywords!")
    else:
        print("\n⚠️ ISSUE: Only finding default keywords - check the debug output above")

if __name__ == "__main__":
    asyncio.run(main())
