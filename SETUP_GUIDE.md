# 🚀 Etsy App Setup Guide

## Quick Start

1. **Run the batch file**: Double-click `etsy_app_manager.bat`
2. **Choose option 8** (Utilities) to check your setup
3. **Install missing packages** if needed
4. **Start the server** with option 1

## Issues You Might See

### ❌ Redis Connection Failed
```
WARNING: Redis connection failed: Error 10061 connecting to localhost:6379
```

**Solution**: Redis is optional! Your app works without it, but caching improves performance.

**To install Redis (optional):**
- **Windows**: Download from https://github.com/microsoftarchive/redis/releases
- **Docker**: `docker run -d -p 6379:6379 redis`
- **Or**: Use the batch file option 6 → 5 (Redis Management)

### ⚠️ Import String Warning
```
WARNING: You must pass the application as an import string to enable 'reload' or 'workers'.
```

**Solution**: This is fixed! The batch file now uses the correct uvicorn command.

### ❌ Python/Package Not Found
```
❌ Python not found! Please install Python first.
```

**Solution**: 
1. Install Python from https://python.org
2. Run the batch file again
3. Use option 8 → 4 to install packages

## 📦 Required Packages

The app needs these Python packages:
```bash
pip install fastapi uvicorn aiohttp cloudscraper redis beautifulsoup4 python-dotenv requests
```

Or use the batch file option 8 → 4 to install automatically.

## 🎯 Testing Your Setup

### Method 1: Use the Batch File
1. Run `etsy_app_manager.bat`
2. Choose option 2 (Run All Tests)
3. Check the results

### Method 2: Manual Testing
```bash
# Start server
python main_py.py

# In another terminal, test API
python test_api_trending.py
```

## 🌐 Server URLs

- **Main App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **Trending Keywords**: http://localhost:8000/api/trending

## 🔧 Troubleshooting

### Server Won't Start
1. Check Python installation: `python --version`
2. Install missing packages: Use batch file option 8 → 4
3. Check port 8000 is free: `netstat -an | findstr :8000`

### No Trending Keywords
1. Check internet connection
2. Try the quick test: Batch file option 3
3. Check bot status: http://localhost:8000/api/health

### Tests Failing
1. Make sure server is running first
2. Check firewall/antivirus blocking connections
3. Try running tests individually

## 📊 Performance Tips

### With Redis (Recommended)
- Install Redis for caching
- Faster response times
- Better performance under load

### Without Redis
- App works fine without Redis
- Slightly slower (no caching)
- Good for development/testing

## 🎉 Success Indicators

You'll know everything is working when:

✅ **Server starts without errors**
✅ **Health check shows bots available**
✅ **Trending endpoint returns keywords**
✅ **Tests pass with good scores**

## 📞 Need Help?

If you're still having issues:

1. **Check the logs** in the batch file output
2. **Run diagnostics** with batch file option 8
3. **Try the simple test** with option 3 (doesn't need server)
4. **Check test results** with option 7

## 🚀 Ready to Go!

Once setup is complete:
1. Use `etsy_app_manager.bat` for daily development
2. Start server with option 1
3. Test with option 4
4. View results with option 7

Happy coding! 🎯
