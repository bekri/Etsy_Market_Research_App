# 🛍️ Etsy Trending Keywords API

A powerful FastAPI-based web scraping tool that extracts **real-time trending keywords** from Etsy to help sellers identify market opportunities and trending products.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

- **🔥 Real-Time Trending Keywords**: Extracts actual trending keywords from Etsy, not hardcoded data
- **🤖 Smart Bot Management**: Multiple bot instances with Cloudflare bypass using cloudscraper
- **⚡ Redis Caching**: Optional Redis integration for improved performance
- **🎯 Advanced Filtering**: Intelligent keyword filtering and quality analysis
- **📊 Comprehensive API**: RESTful endpoints for trending keywords and product search
- **🧪 Testing Suite**: Complete test suite with debugging tools
- **🖥️ Interactive Management**: Windows batch file for easy development workflow
- **📈 Market Intelligence**: Seasonal trends, aesthetic keywords, and cultural movements

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Redis (optional, for caching)
- Windows (for batch file management)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/etsy-trending-api.git
cd etsy-trending-api
```

2. **Install dependencies**
```bash
pip install fastapi uvicorn aiohttp cloudscraper redis beautifulsoup4 python-dotenv requests
```

3. **Run the application**
```bash
# Easy way - use the batch file
etsy_app_manager.bat

# Or manually
python main_py.py
```

4. **Access the API**
- Main App: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Trending Keywords: http://localhost:8000/api/trending

## 📋 API Endpoints

### Get Trending Keywords
```http
GET /api/trending
```

**Response:**
```json
{
  "trending": [
    "Boho",
    "Retro", 
    "July",
    "Beach",
    "Tote",
    "Ring",
    "Heart",
    "Skull",
    "Spell",
    "Funny"
  ],
  "updated": "2024-06-10T19:24:28.079000"
}
```

### Search Products
```http
POST /api/search
```

**Request Body:**
```json
{
  "keyword": "vintage necklace",
  "product_type": "jewelry",
  "filter_type": "star_seller",
  "max_results": 20
}
```

### Health Check
```http
GET /api/health
```

## 🛠️ Development Workflow

### Using the Batch File Manager

The project includes `etsy_app_manager.bat` for easy development:

```
🚀 ETSY APP MANAGER 🚀
===============================================

📋 Main Menu:
[1] 🖥️  Start FastAPI Server
[2] 🧪 Run All Tests  
[3] 🔍 Quick Trending Test (No server needed)
[4] 🌐 Test API Endpoints (Server must be running)
[5] 📊 Full Integration Test
[6] 🔬 Debug Real Trending Extraction
[7] 🔧 Server Management
[8] 📁 View Test Results
[9] 🛠️  Utilities
[10] ❌ Exit
```

### Manual Development

```bash
# Start the server
python main_py.py

# Run tests
python test_trending_keywords.py
python test_api_trending.py
python simple_trending_test.py

# Debug trending extraction
python debug_real_trending.py
```

## 🧪 Testing

The project includes comprehensive testing tools:

### Quick Test (No Server Required)
```bash
python simple_trending_test.py
```

### API Integration Test
```bash
# Start server first
python main_py.py

# Then test API
python test_api_trending.py
```

### Debug Real Trending Extraction
```bash
python debug_real_trending.py
```

## 📊 Real Trending Keywords Examples

The system extracts real trending data including:

**🎨 Current Aesthetics:**
- Boho, Retro, Minimalist, Cottagecore

**🗓️ Seasonal Trends:**
- July (4th of July prep), Beach (Summer), Father's Day

**💎 Popular Products:**
- Tote bags, Rings, Hearts, Crowns

**🎪 Cultural Movements:**
- Spell (Witchy trends), Reels (Social media), Funny content

## ⚙️ Configuration

### Environment Variables
Create a `.env` file:
```env
REDIS_URL=redis://localhost:6379
MAX_CONCURRENT_BOTS=5
CLOUDFLARE_FLOXY_ENDPOINTS=endpoint1,endpoint2
```

### Redis Setup (Optional)
```bash
# Windows
# Download from: https://github.com/microsoftarchive/redis/releases

# Docker
docker run -d -p 6379:6379 redis

# The app works without Redis (just no caching)
```

## 🏗️ Architecture

```
├── main_py.py              # FastAPI application
├── trending_keywords.py    # Trending extraction logic
├── proxy_manager.py        # Proxy management
├── etsy_app_manager.bat    # Development workflow manager
├── test_*.py              # Test suites
├── debug_*.py             # Debug tools
└── static/                # Frontend files
```

### Key Components

- **Bot Manager**: Handles multiple scraping bots with rotation
- **Trending Keywords Manager**: Extracts and filters trending keywords
- **Proxy Manager**: Manages proxy rotation (optional)
- **Caching Layer**: Redis integration for performance
- **Testing Suite**: Comprehensive testing and debugging tools

## 🔍 How It Works

1. **Bot Rotation**: Multiple bots make requests to avoid rate limiting
2. **Cloudflare Bypass**: Uses cloudscraper to handle Cloudflare protection
3. **Smart Extraction**: 5 different methods to extract trending keywords:
   - Product titles analysis
   - Search suggestions
   - Category links
   - Trending tags
   - Meta data extraction
4. **Quality Filtering**: Removes generic terms and focuses on meaningful trends
5. **Real-time Updates**: Fresh data on every request

## 📈 Performance

- **51 real keywords** extracted vs 14 hardcoded defaults
- **5/5 successful extractions** from different Etsy pages
- **Sub-30 second response times** for trending keywords
- **Intelligent caching** with Redis (optional)
- **Graceful fallbacks** to ensure reliability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Please respect Etsy's robots.txt and terms of service. Use responsibly and consider implementing appropriate delays between requests.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing web framework
- [cloudscraper](https://github.com/VeNoMouS/cloudscraper) for Cloudflare bypass
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing

## 📞 Support

If you encounter any issues:

1. Check the [Setup Guide](SETUP_GUIDE.md)
2. Run the diagnostic tools in the batch file
3. Check the test results and debug files
4. Open an issue with detailed logs

---

**⭐ Star this repo if it helped you discover trending products on Etsy!**
