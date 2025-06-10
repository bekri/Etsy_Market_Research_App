🚀 Etsy App Setup Guide
Quick Start
Run the batch file: Double-click etsy_app_manager.bat
Choose option 8 (Utilities) to check your setup
Install missing packages if needed
Start the server with option 1
Issues You Might See
❌ Redis Connection Failed
WARNING: Redis connection failed: Error 10061 connecting to localhost:6379
Solution: Redis is optional! Your app works without it, but caching improves performance.

To install Redis (optional):

Windows: Download from https://github.com/microsoftarchive/redis/releases
Docker: docker run -d -p 6379:6379 redis
Or: Use the batch file option 6 → 5 (Redis Management)
⚠️ Import String Warning
WARNING: You must pass the application as an import string to enable 'reload' or 'workers'.
Solution: This is fixed! The batch file now uses the correct uvicorn command.

❌ Python/Package Not Found
❌ Python not found! Please install Python first.
Solution:

Install Python from https://python.org
Run the batch file again
Use option 8 → 4 to install packages
📦 Required Packages
The app needs these Python packages:

pip install fastapi uvicorn aiohttp cloudscraper redis beautifulsoup4 python-dotenv requests
Or use the batch file option 8 → 4 to install automatically.

🎯 Testing Your Setup
Method 1: Use the Batch File
Run etsy_app_manager.bat
Choose option 2 (Run All Tests)
Check the results
Method 2: Manual Testing
# Start server
python main_py.py

# In another terminal, test API
python test_api_trending.py
🌐 Server URLs
Main App: http://localhost:8000
API Docs: http://localhost:8000/docs
Health Check: http://localhost:8000/api/health
Trending Keywords: http://localhost:8000/api/trending
🔧 Troubleshooting
Server Won't Start
Check Python installation: python --version
Install missing packages: Use batch file option 8 → 4
Check port 8000 is free: netstat -an | findstr :8000
No Trending Keywords
Check internet connection
Try the quick test: Batch file option 3
Check bot status: http://localhost:8000/api/health
Tests Failing
Make sure server is running first
Check firewall/antivirus blocking connections
Try running tests individually
📊 Performance Tips
With Redis (Recommended)
Install Redis for caching
Faster response times
Better performance under load
Without Redis
App works fine without Redis
Slightly slower (no caching)
Good for development/testing
🎉 Success Indicators
You'll know everything is working when:

✅ Server starts without errors ✅ Health check shows bots available ✅ Trending endpoint returns keywords ✅ Tests pass with good scores

📞 Need Help?
contact me at bzpw@gmailcom
If you're still having issues:

Check the logs in the batch file output
Run diagnostics with batch file option 8
Try the simple test with option 3 (doesn't need server)
Check test results with option 7
🚀 Ready to Go!
Once setup is complete:

Use etsy_app_manager.bat for daily development
Start server with option 1
Test with option 4
View results with option 7
