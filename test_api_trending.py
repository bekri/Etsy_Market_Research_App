"""
API Trending Keywords Test
Tests the /api/trending endpoint of your FastAPI application
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from typing import Dict, List
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APITrendingTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []

    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        logger.info(f"{status} {test_name}")
        if details:
            logger.info(f"   {details}")

    async def test_health_endpoint(self) -> bool:
        """Test if the API server is running"""
        logger.info("🔍 Testing API Health...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        bots_info = data.get('bots_status', {})
                        self.log_result("API Health Check", True, 
                                      f"Server running, {bots_info.get('total', 0)} bots available")
                        return True
                    else:
                        self.log_result("API Health Check", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            self.log_result("API Health Check", False, f"Connection failed: {str(e)}")
            return False

    async def test_trending_endpoint_structure(self) -> bool:
        """Test the structure of the trending endpoint response"""
        logger.info("🔍 Testing Trending Endpoint Structure...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/trending", timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check required fields
                        if 'trending' in data and 'updated' in data:
                            keywords = data['trending']
                            if isinstance(keywords, list):
                                self.log_result("Trending Endpoint Structure", True, 
                                              f"Valid structure with {len(keywords)} keywords")
                                return True
                            else:
                                self.log_result("Trending Endpoint Structure", False, 
                                              "Keywords field is not a list")
                                return False
                        else:
                            self.log_result("Trending Endpoint Structure", False, 
                                          "Missing required fields (trending, updated)")
                            return False
                    else:
                        self.log_result("Trending Endpoint Structure", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            self.log_result("Trending Endpoint Structure", False, f"Request failed: {str(e)}")
            return False

    async def test_trending_keywords_quality(self) -> bool:
        """Test the quality of returned trending keywords"""
        logger.info("🔍 Testing Trending Keywords Quality...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/trending", timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        keywords = data.get('trending', [])
                        
                        if not keywords:
                            self.log_result("Trending Keywords Quality", False, "No keywords returned")
                            return False
                        
                        # Quality checks
                        quality_score = 0
                        total_checks = 0
                        
                        # Check 1: Reasonable number of keywords
                        if 5 <= len(keywords) <= 50:
                            quality_score += 1
                        total_checks += 1
                        
                        # Check 2: Keywords are not empty or too short
                        valid_keywords = [k for k in keywords if isinstance(k, str) and len(k.strip()) > 2]
                        if len(valid_keywords) >= len(keywords) * 0.8:  # At least 80% valid
                            quality_score += 1
                        total_checks += 1
                        
                        # Check 3: Check for trend-related terms
                        trend_terms = ['aesthetic', 'core', 'style', 'vintage', 'modern', 'boho', 'minimalist']
                        trend_keywords = [k for k in keywords if any(term in k.lower() for term in trend_terms)]
                        if trend_keywords:
                            quality_score += 1
                        total_checks += 1
                        
                        # Check 4: Diversity check
                        unique_first_chars = len(set(k[0].lower() for k in keywords if k))
                        if unique_first_chars >= len(keywords) * 0.3:
                            quality_score += 1
                        total_checks += 1
                        
                        final_score = (quality_score / total_checks) * 100
                        
                        details = f"Score: {final_score:.0f}%, Keywords: {keywords[:5]}..."
                        if trend_keywords:
                            details += f", Trend keywords: {trend_keywords[:3]}"
                        
                        success = final_score >= 75
                        self.log_result("Trending Keywords Quality", success, details)
                        return success
                        
                    else:
                        self.log_result("Trending Keywords Quality", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            self.log_result("Trending Keywords Quality", False, f"Request failed: {str(e)}")
            return False

    async def test_trending_endpoint_performance(self) -> bool:
        """Test the performance of the trending endpoint"""
        logger.info("🔍 Testing Trending Endpoint Performance...")
        
        response_times = []
        successful_requests = 0
        total_requests = 3
        
        try:
            for i in range(total_requests):
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}/api/trending", timeout=60) as response:
                        end_time = time.time()
                        response_time = end_time - start_time
                        response_times.append(response_time)
                        
                        if response.status == 200:
                            successful_requests += 1
                        
                        logger.info(f"   Request {i+1}: {response_time:.2f}s (HTTP {response.status})")
                        
                        # Small delay between requests
                        if i < total_requests - 1:
                            await asyncio.sleep(2)
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                
                # Performance criteria
                performance_good = avg_time < 30 and max_time < 60 and successful_requests >= total_requests * 0.8
                
                details = f"Avg: {avg_time:.2f}s, Max: {max_time:.2f}s, Success: {successful_requests}/{total_requests}"
                self.log_result("Trending Endpoint Performance", performance_good, details)
                return performance_good
            else:
                self.log_result("Trending Endpoint Performance", False, "No response times recorded")
                return False
                
        except Exception as e:
            self.log_result("Trending Endpoint Performance", False, f"Performance test failed: {str(e)}")
            return False

    async def test_trending_consistency(self) -> bool:
        """Test if trending endpoint returns consistent results"""
        logger.info("🔍 Testing Trending Endpoint Consistency...")
        
        try:
            responses = []
            
            # Make multiple requests
            for i in range(2):
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}/api/trending", timeout=30) as response:
                        if response.status == 200:
                            data = await response.json()
                            responses.append(data.get('trending', []))
                        else:
                            self.log_result("Trending Consistency", False, f"HTTP {response.status} on request {i+1}")
                            return False
                
                # Wait between requests
                if i < 1:
                    await asyncio.sleep(3)
            
            if len(responses) >= 2:
                # Check if responses are reasonably consistent
                keywords1 = set(responses[0])
                keywords2 = set(responses[1])
                
                # Calculate overlap
                overlap = len(keywords1.intersection(keywords2))
                total_unique = len(keywords1.union(keywords2))
                
                if total_unique > 0:
                    consistency_ratio = overlap / len(keywords1) if keywords1 else 0
                    
                    # Allow for some variation but expect reasonable consistency
                    is_consistent = consistency_ratio >= 0.5 or overlap >= 5
                    
                    details = f"Overlap: {overlap} keywords, Consistency: {consistency_ratio:.2f}"
                    self.log_result("Trending Consistency", is_consistent, details)
                    return is_consistent
                else:
                    self.log_result("Trending Consistency", False, "No keywords to compare")
                    return False
            else:
                self.log_result("Trending Consistency", False, "Insufficient responses for comparison")
                return False
                
        except Exception as e:
            self.log_result("Trending Consistency", False, f"Consistency test failed: {str(e)}")
            return False

    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 API TRENDING KEYWORDS TEST SUMMARY")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
        logger.info("\n📋 Test Details:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            logger.info(f"{status} {result['test_name']}")
            if result['details']:
                logger.info(f"   {result['details']}")
        
        # Save results
        with open('api_trending_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"\n💾 Results saved to 'api_trending_test_results.json'")
        logger.info("="*60)

    async def run_all_tests(self):
        """Run all API trending tests"""
        logger.info("🚀 Starting API Trending Keywords Test Suite...")
        logger.info("="*60)
        
        # Test 1: Health check
        health_ok = await self.test_health_endpoint()
        if not health_ok:
            logger.error("❌ API server not available - stopping tests")
            self.print_summary()
            return False
        
        # Test 2: Endpoint structure
        await self.test_trending_endpoint_structure()
        
        # Test 3: Keywords quality
        await self.test_trending_keywords_quality()
        
        # Test 4: Performance
        await self.test_trending_endpoint_performance()
        
        # Test 5: Consistency
        await self.test_trending_consistency()
        
        # Print summary
        self.print_summary()
        
        # Return overall success
        passed_tests = sum(1 for result in self.test_results if result['success'])
        return passed_tests >= len(self.test_results) * 0.8  # 80% success rate

async def main():
    """Main test function"""
    print("🎯 API Trending Keywords Test")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("You can start it with: python main_py.py")
    print()
    
    test_suite = APITrendingTest()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n🎉 API trending functionality is working well!")
    else:
        print("\n⚠️ API trending functionality needs attention - check the logs above")

if __name__ == "__main__":
    asyncio.run(main())
