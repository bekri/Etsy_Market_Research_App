from datetime import datetime
from typing import List, Dict
import json
import logging
from collections import Counter
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class TrendingKeywordsManager:
    def __init__(self, scraper=None):
        self.scraper = scraper
        self.default_keywords = [
            "Cottagecore", "Dark Academia", "Y2K Aesthetic", "Minimalist Design",
            "Boho Chic", "Vintage Retro", "Plant Mom", "Self Care", "Motivational Quotes",
            "Astrology", "Crystal Healing", "Sustainable Living", "Mental Health Awareness",
            "Dopamine Decor", "Grandmillennial", "Maximalist", "Japandi Style"
        ]

    async def extract_trending_from_listings(self, html_content: str) -> List[str]:
        """Extract trending keywords from Etsy listings"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            trending_keywords = set()

            logger.info("🔍 Starting trending keyword extraction...")

            # Method 1: Extract from product titles (most reliable)
            title_selectors = [
                'h3[data-test-id="listing-link"]',
                'h3.v2-listing-card__title',
                'a[data-test-id="listing-link"] h3',
                '.v2-listing-card__title',
                'h3',
                '.listing-link h3'
            ]

            titles_found = 0
            for selector in title_selectors:
                title_elements = soup.select(selector)
                if title_elements:
                    logger.info(f"Found {len(title_elements)} titles with selector: {selector}")
                    titles_found += len(title_elements)

                    for title_elem in title_elements[:50]:  # Limit to first 50 titles
                        title = title_elem.get_text(strip=True)
                        if title and len(title) > 5:
                            # Extract meaningful keywords from titles
                            keywords = self._extract_keywords_from_title(title)
                            trending_keywords.update(keywords)
                    break  # Use first working selector

            logger.info(f"Extracted keywords from {titles_found} product titles")

            # Method 2: Look for search suggestions and popular searches
            search_selectors = [
                'a[href*="/search?q="]',
                'a[href*="search"]',
                '.search-suggestion',
                '.popular-search',
                '[data-test-id*="search"]'
            ]

            for selector in search_selectors:
                search_elements = soup.select(selector)
                for elem in search_elements[:20]:  # Limit to 20 search suggestions
                    text = elem.get_text(strip=True)
                    href = elem.get('href', '')

                    # Extract from link text
                    if text and 3 < len(text) < 30 and not any(skip in text.lower() for skip in ['sign', 'cart', 'account', 'help']):
                        trending_keywords.add(text.title())

                    # Extract from search URLs
                    if 'q=' in href:
                        try:
                            import urllib.parse
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                            if 'q' in parsed:
                                search_term = parsed['q'][0].replace('+', ' ').replace('%20', ' ')
                                if 3 < len(search_term) < 30:
                                    trending_keywords.add(search_term.title())
                        except:
                            pass

            # Method 3: Extract from category and navigation links
            category_selectors = [
                'a[href*="/c/"]',
                '.category-link',
                '.nav-link',
                '[data-test-id*="category"]'
            ]

            for selector in category_selectors:
                category_elements = soup.select(selector)
                for elem in category_elements[:15]:  # Limit to 15 categories
                    text = elem.get_text(strip=True)
                    if text and 3 < len(text) < 25 and not any(skip in text.lower() for skip in ['home', 'shop', 'sell', 'help']):
                        trending_keywords.add(text.title())

            # Method 4: Look for trending tags and badges
            tag_selectors = [
                '.trending-tag',
                '.popular-tag',
                '.badge',
                '[class*="trend"]',
                '[class*="popular"]'
            ]

            for selector in tag_selectors:
                tag_elements = soup.select(selector)
                for elem in tag_elements:
                    text = elem.get_text(strip=True)
                    if text and 3 < len(text) < 20:
                        trending_keywords.add(text.title())

            # Method 5: Extract from meta tags and structured data
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and meta_keywords.get('content'):
                keywords = meta_keywords['content'].split(',')
                for keyword in keywords[:10]:  # Limit to 10 meta keywords
                    keyword = keyword.strip()
                    if keyword and 3 < len(keyword) < 25:
                        trending_keywords.add(keyword.title())

            # Filter and clean keywords
            filtered_keywords = self._filter_and_clean_keywords(list(trending_keywords))

            logger.info(f"✅ Extracted {len(filtered_keywords)} trending keywords from Etsy")

            if len(filtered_keywords) >= 5:
                return filtered_keywords[:16]
            else:
                logger.warning("⚠️ Not enough real keywords found, mixing with defaults")
                # Mix real keywords with some defaults
                mixed_keywords = filtered_keywords + self.default_keywords
                return list(dict.fromkeys(mixed_keywords))[:16]  # Remove duplicates, keep order

        except Exception as e:
            logger.error(f"Error extracting trending keywords: {str(e)}")
            return self.default_keywords

    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """Extract meaningful keywords from a product title"""
        keywords = []

        # Clean the title
        title = title.lower()

        # Remove common words and extract meaningful terms
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'this', 'that', 'these', 'those',
            'gift', 'gifts', 'item', 'items', 'product', 'products', 'sale', 'new',
            'best', 'top', 'great', 'perfect', 'amazing', 'beautiful', 'cute', 'cool'
        }

        # Extract words that might be trending
        words = re.findall(r'\b[a-zA-Z]{3,}\b', title)

        for word in words:
            if word not in stop_words and len(word) > 3:
                # Capitalize first letter
                keyword = word.capitalize()
                if keyword not in keywords:
                    keywords.append(keyword)

        # Look for compound terms (aesthetic styles, etc.)
        compound_patterns = [
            r'\b(\w+core)\b',  # cottagecore, darkcore, etc.
            r'\b(\w+\s+aesthetic)\b',  # dark aesthetic, etc.
            r'\b(\w+\s+style)\b',  # boho style, etc.
            r'\b(\w+\s+decor)\b',  # home decor, etc.
            r'\b(\w+\s+design)\b',  # minimalist design, etc.
        ]

        for pattern in compound_patterns:
            matches = re.findall(pattern, title, re.IGNORECASE)
            for match in matches:
                keyword = match.title()
                if keyword not in keywords and len(keyword) > 5:
                    keywords.append(keyword)

        return keywords[:5]  # Return top 5 keywords per title

    def _filter_and_clean_keywords(self, keywords: List[str]) -> List[str]:
        """Filter and clean the extracted keywords"""
        filtered = []

        # Words to exclude
        exclude_words = {
            'etsy', 'shop', 'store', 'buy', 'sell', 'cart', 'account', 'sign', 'help',
            'home', 'page', 'search', 'filter', 'sort', 'view', 'more', 'less',
            'shipping', 'delivery', 'return', 'policy', 'terms', 'privacy',
            'contact', 'about', 'blog', 'news', 'press', 'careers', 'investors'
        }

        for keyword in keywords:
            if not keyword:
                continue

            keyword = keyword.strip()

            # Skip if too short or too long
            if len(keyword) < 3 or len(keyword) > 30:
                continue

            # Skip if in exclude list
            if keyword.lower() in exclude_words:
                continue

            # Skip if it's just numbers
            if keyword.isdigit():
                continue

            # Skip if it contains special characters
            if not re.match(r'^[a-zA-Z\s]+$', keyword):
                continue

            # Clean up the keyword
            keyword = ' '.join(keyword.split())  # Remove extra spaces
            keyword = keyword.title()  # Proper case

            if keyword not in filtered:
                filtered.append(keyword)

        # Sort by length (shorter, more specific terms first)
        filtered.sort(key=len)

        return filtered

    async def get_trending_keywords(self, limit: int = 16) -> List[str]:
        """Get trending keywords from Etsy"""
        if not self.scraper:
            return self.default_keywords

        try:
            # Scrape Etsy's homepage or trending page
            html_content = await self.scraper.make_request('https://www.etsy.com/trending')
            if not html_content:
                return self.default_keywords

            trending_keywords = await self.extract_trending_from_listings(html_content)
            return trending_keywords[:limit]

        except Exception as e:
            logger.error(f"Error getting trending keywords: {str(e)}")
            return self.default_keywords 