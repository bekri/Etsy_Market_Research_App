@echo off
setlocal enabledelayedexpansion
title Etsy App Manager
color 0A

:MAIN_MENU
cls
echo.
echo ===============================================
echo           🚀 ETSY APP MANAGER 🚀
echo ===============================================
echo.
echo 📋 Main Menu:
echo.
echo [1] 🖥️  Start FastAPI Server
echo [2] 🧪 Run All Tests
echo [3] 🔍 Quick Trending Test (No server needed)
echo [4] 🌐 Test API Endpoints (Server must be running)
echo [5] 📊 Full Integration Test
echo [6] 🔬 Debug Real Trending Extraction
echo [7] 🔧 Server Management
echo [8] 📁 View Test Results
echo [9] 🛠️  Utilities
echo [10] ❌ Exit
echo.
set /p choice="Enter your choice (1-10): "

if "%choice%"=="1" goto START_SERVER
if "%choice%"=="2" goto RUN_ALL_TESTS
if "%choice%"=="3" goto QUICK_TEST
if "%choice%"=="4" goto API_TEST
if "%choice%"=="5" goto INTEGRATION_TEST
if "%choice%"=="6" goto DEBUG_REAL_TRENDING
if "%choice%"=="7" goto SERVER_MANAGEMENT
if "%choice%"=="8" goto VIEW_RESULTS
if "%choice%"=="9" goto UTILITIES
if "%choice%"=="10" goto EXIT
goto INVALID_CHOICE

:START_SERVER
cls
echo.
echo ===============================================
echo           🖥️ STARTING FASTAPI SERVER
echo ===============================================
echo.
echo 🔍 Pre-flight checks...
echo.
echo ✅ Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    goto MAIN_MENU
)

echo ✅ Checking required packages...
python -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ FastAPI/Uvicorn not installed!
    echo.
    set /p install_choice="Install missing packages? (y/n): "
    if /i "!install_choice!"=="y" (
        echo Installing packages...
        pip install fastapi uvicorn aiohttp cloudscraper redis beautifulsoup4 python-dotenv requests
    ) else (
        goto MAIN_MENU
    )
)

echo ✅ Checking Redis (optional)...
python -c "import redis; r=redis.Redis(); r.ping()" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Redis not running - server will work without caching
    echo   To install Redis: https://redis.io/download
) else (
    echo ✅ Redis is running
)

echo.
echo 🚀 Starting server on http://localhost:8000
echo 🌐 Server will open in browser automatically
echo 🛑 Press Ctrl+C to stop the server
echo.
echo 📝 Server logs:
echo ===============================================

REM Start server with proper uvicorn command
uvicorn main_py:app --host 0.0.0.0 --port 8000 --reload 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Uvicorn command failed, trying alternative method...
    python main_py.py
)

echo.
echo 🛑 Server stopped. Press any key to return to menu...
pause >nul
goto MAIN_MENU

:RUN_ALL_TESTS
cls
echo.
echo ===============================================
echo           🧪 RUNNING ALL TESTS
echo ===============================================
echo.
echo This will run all available tests in sequence...
echo.
echo 1️⃣ Running Quick Trending Test...
echo ===============================================
python simple_trending_test.py
echo.
echo ✅ Quick test completed!
echo.
echo 2️⃣ Running Integration Test...
echo ===============================================
python test_trending_keywords.py
echo.
echo ✅ Integration test completed!
echo.
echo 3️⃣ Checking if server is running for API test...
echo ===============================================
python -c "import requests; requests.get('http://localhost:8000/api/health', timeout=5)" 2>nul
if %errorlevel%==0 (
    echo ✅ Server is running! Running API tests...
    python test_api_trending.py
) else (
    echo ⚠️ Server not running. Skipping API tests.
    echo   Start server first with option 1, then run option 4.
)
echo.
echo 🎉 All tests completed! Check the results above.
echo.
pause
goto MAIN_MENU

:QUICK_TEST
cls
echo.
echo ===============================================
echo        🔍 QUICK TRENDING TEST
echo ===============================================
echo.
echo Running standalone trending keyword test...
echo This doesn't require the server to be running.
echo.
python simple_trending_test.py
echo.
echo ✅ Quick test completed!
echo Results saved to: trending_test_results.json
echo.
pause
goto MAIN_MENU

:API_TEST
cls
echo.
echo ===============================================
echo        🌐 API ENDPOINT TESTS
echo ===============================================
echo.
echo Testing API endpoints (server must be running)...
echo.
echo 🔍 Checking if server is running...
python -c "import requests; requests.get('http://localhost:8000/api/health', timeout=5)" 2>nul
if %errorlevel%==0 (
    echo ✅ Server is running! Starting API tests...
    echo.
    python test_api_trending.py
    echo.
    echo ✅ API tests completed!
    echo Results saved to: api_trending_test_results.json
) else (
    echo ❌ Server is not running!
    echo.
    echo Please start the server first:
    echo 1. Go back to main menu
    echo 2. Choose option 1 to start server
    echo 3. Then run this test again
)
echo.
pause
goto MAIN_MENU

:INTEGRATION_TEST
cls
echo.
echo ===============================================
echo        📊 FULL INTEGRATION TEST
echo ===============================================
echo.
echo Running comprehensive integration tests...
echo This tests all components together.
echo.
python test_trending_keywords.py
echo.
echo ✅ Integration test completed!
echo.
pause
goto MAIN_MENU

:DEBUG_REAL_TRENDING
cls
echo.
echo ===============================================
echo        🔬 DEBUG REAL TRENDING EXTRACTION
echo ===============================================
echo.
echo This will test if we can extract REAL trending keywords from Etsy
echo (not just the hardcoded defaults)
echo.
echo The debug will:
echo - Test multiple Etsy pages
echo - Analyze page structure
echo - Extract real trending keywords
echo - Save debug files for inspection
echo.
python debug_real_trending.py
echo.
echo ✅ Debug completed!
echo.
echo 📁 Check these files for results:
echo - real_trending_debug_results.json
echo - etsy_sample_*.html
echo - etsy_titles_*.txt
echo.
pause
goto MAIN_MENU

:SERVER_MANAGEMENT
cls
echo.
echo ===============================================
echo           🔧 SERVER MANAGEMENT
echo ===============================================
echo.
echo [1] 🖥️  Start Server
echo [2] 🔍 Check Server Status
echo [3] 🌐 Open Server in Browser
echo [4] 📊 Check Server Health
echo [5] 🗄️  Redis Management
echo [6] 🔙 Back to Main Menu
echo.
set /p server_choice="Enter your choice (1-5): "

if "%server_choice%"=="1" goto START_SERVER
if "%server_choice%"=="2" goto CHECK_STATUS
if "%server_choice%"=="3" goto OPEN_BROWSER
if "%server_choice%"=="4" goto CHECK_HEALTH
if "%server_choice%"=="5" goto REDIS_MANAGEMENT
if "%server_choice%"=="6" goto MAIN_MENU
goto INVALID_CHOICE

:CHECK_STATUS
cls
echo.
echo ===============================================
echo           🔍 CHECKING SERVER STATUS
echo ===============================================
echo.
echo Checking if server is running on localhost:8000...
echo.
python -c "import requests; r=requests.get('http://localhost:8000/api/health', timeout=5); print('✅ Server is RUNNING'); print('Status:', r.json())" 2>nul
if %errorlevel%==0 (
    echo.
    echo ✅ Server is accessible!
) else (
    echo ❌ Server is NOT running or not accessible.
    echo.
    echo To start the server:
    echo 1. Go back to main menu
    echo 2. Choose option 1
)
echo.
pause
goto SERVER_MANAGEMENT

:OPEN_BROWSER
echo.
echo 🌐 Opening server in browser...
start http://localhost:8000
echo ✅ Browser opened! (If server is running)
echo.
pause
goto SERVER_MANAGEMENT

:CHECK_HEALTH
cls
echo.
echo ===============================================
echo           📊 SERVER HEALTH CHECK
echo ===============================================
echo.
python -c "import requests, json; r=requests.get('http://localhost:8000/api/health', timeout=10); print('✅ Server Health:'); print(json.dumps(r.json(), indent=2))" 2>nul
if %errorlevel%==0 (
    echo.
    echo ✅ Health check completed!
) else (
    echo ❌ Health check failed - server may not be running.
)
echo.
pause
goto SERVER_MANAGEMENT

:REDIS_MANAGEMENT
cls
echo.
echo ===============================================
echo           🗄️ REDIS MANAGEMENT
echo ===============================================
echo.
echo Redis is optional but provides caching for better performance.
echo.
echo [1] 🔍 Check Redis Status
echo [2] 📥 Download Redis (Windows)
echo [3] 🚀 Start Redis (if installed)
echo [4] 🛑 Stop Redis
echo [5] 📊 Redis Info
echo [6] 🔙 Back to Server Management
echo.
set /p redis_choice="Enter your choice (1-6): "

if "%redis_choice%"=="1" goto CHECK_REDIS_STATUS
if "%redis_choice%"=="2" goto DOWNLOAD_REDIS
if "%redis_choice%"=="3" goto START_REDIS
if "%redis_choice%"=="4" goto STOP_REDIS
if "%redis_choice%"=="5" goto REDIS_INFO
if "%redis_choice%"=="6" goto SERVER_MANAGEMENT
goto INVALID_CHOICE

:CHECK_REDIS_STATUS
echo.
echo 🔍 Checking Redis status...
echo.
python -c "import redis; r=redis.Redis(); r.ping(); print('✅ Redis is running and accessible')" 2>nul
if %errorlevel%==0 (
    echo ✅ Redis connection successful!
) else (
    echo ❌ Redis is not running or not accessible.
    echo.
    echo Possible reasons:
    echo - Redis is not installed
    echo - Redis service is not started
    echo - Redis is running on different port
)
echo.
pause
goto REDIS_MANAGEMENT

:DOWNLOAD_REDIS
echo.
echo 📥 Redis Download Information:
echo ===============================================
echo.
echo For Windows, you can download Redis from:
echo 1. Official: https://redis.io/download
echo 2. Windows port: https://github.com/microsoftarchive/redis/releases
echo 3. Or use Docker: docker run -d -p 6379:6379 redis
echo.
echo 💡 Tip: Your app works without Redis, but caching improves performance.
echo.
set /p open_download="Open download page in browser? (y/n): "
if /i "%open_download%"=="y" (
    start https://github.com/microsoftarchive/redis/releases
    echo ✅ Download page opened in browser
)
echo.
pause
goto REDIS_MANAGEMENT

:START_REDIS
echo.
echo 🚀 Attempting to start Redis...
echo.
REM Try common Redis installation paths
if exist "C:\Program Files\Redis\redis-server.exe" (
    echo Starting Redis from Program Files...
    start "Redis Server" "C:\Program Files\Redis\redis-server.exe"
    echo ✅ Redis start command sent
) else if exist "redis-server.exe" (
    echo Starting Redis from current directory...
    start "Redis Server" redis-server.exe
    echo ✅ Redis start command sent
) else (
    echo ❌ Redis executable not found in common locations.
    echo.
    echo Please ensure Redis is installed and try:
    echo 1. Add Redis to your PATH
    echo 2. Or run redis-server.exe manually
    echo 3. Or use Docker: docker run -d -p 6379:6379 redis
)
echo.
pause
goto REDIS_MANAGEMENT

:STOP_REDIS
echo.
echo 🛑 Stopping Redis...
taskkill /f /im redis-server.exe >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Redis stopped successfully
) else (
    echo ⚠️ Redis process not found or already stopped
)
echo.
pause
goto REDIS_MANAGEMENT

:REDIS_INFO
echo.
echo 📊 Redis Information:
echo ===============================================
echo.
python -c "import redis; r=redis.Redis(); info=r.info(); print('✅ Redis Info:'); [print(f'{k}: {v}') for k,v in info.items() if k in ['redis_version', 'used_memory_human', 'connected_clients', 'total_commands_processed']]" 2>nul
if %errorlevel%==0 (
    echo.
    echo ✅ Redis info retrieved successfully
) else (
    echo ❌ Could not retrieve Redis info - Redis may not be running
)
echo.
pause
goto REDIS_MANAGEMENT

:VIEW_RESULTS
cls
echo.
echo ===============================================
echo           📁 VIEW TEST RESULTS
echo ===============================================
echo.
echo Available result files:
echo.
if exist "trending_test_results.json" (
    echo ✅ trending_test_results.json
) else (
    echo ❌ trending_test_results.json (not found)
)

if exist "api_trending_test_results.json" (
    echo ✅ api_trending_test_results.json
) else (
    echo ❌ api_trending_test_results.json (not found)
)
echo.
echo [1] 📄 View Quick Test Results
echo [2] 📄 View API Test Results
echo [3] 📁 Open Results Folder
echo [4] 🗑️  Clear All Results
echo [5] 🔙 Back to Main Menu
echo.
set /p result_choice="Enter your choice (1-5): "

if "%result_choice%"=="1" goto VIEW_QUICK_RESULTS
if "%result_choice%"=="2" goto VIEW_API_RESULTS
if "%result_choice%"=="3" goto OPEN_FOLDER
if "%result_choice%"=="4" goto CLEAR_RESULTS
if "%result_choice%"=="5" goto MAIN_MENU
goto INVALID_CHOICE

:VIEW_QUICK_RESULTS
if exist "trending_test_results.json" (
    echo.
    echo 📄 Quick Test Results:
    echo ===============================================
    type trending_test_results.json
) else (
    echo ❌ Quick test results not found. Run the quick test first.
)
echo.
pause
goto VIEW_RESULTS

:VIEW_API_RESULTS
if exist "api_trending_test_results.json" (
    echo.
    echo 📄 API Test Results:
    echo ===============================================
    type api_trending_test_results.json
) else (
    echo ❌ API test results not found. Run the API test first.
)
echo.
pause
goto VIEW_RESULTS

:OPEN_FOLDER
echo.
echo 📁 Opening current folder...
start .
echo ✅ Folder opened!
echo.
pause
goto VIEW_RESULTS

:CLEAR_RESULTS
echo.
echo 🗑️ Clearing all test results...
if exist "trending_test_results.json" del "trending_test_results.json"
if exist "api_trending_test_results.json" del "api_trending_test_results.json"
echo ✅ Results cleared!
echo.
pause
goto VIEW_RESULTS

:UTILITIES
cls
echo.
echo ===============================================
echo              🛠️ UTILITIES
echo ===============================================
echo.
echo [1] 🐍 Check Python Installation
echo [2] 📦 Check Required Packages
echo [3] 🌐 Test Internet Connection
echo [4] 🔧 Install Missing Packages
echo [5] 📋 Show System Info
echo [6] 🔙 Back to Main Menu
echo.
set /p util_choice="Enter your choice (1-6): "

if "%util_choice%"=="1" goto CHECK_PYTHON
if "%util_choice%"=="2" goto CHECK_PACKAGES
if "%util_choice%"=="3" goto TEST_INTERNET
if "%util_choice%"=="4" goto INSTALL_PACKAGES
if "%util_choice%"=="5" goto SYSTEM_INFO
if "%util_choice%"=="6" goto MAIN_MENU
goto INVALID_CHOICE

:CHECK_PYTHON
echo.
echo 🐍 Checking Python installation...
python --version
echo.
echo 📍 Python location:
where python
echo.
pause
goto UTILITIES

:CHECK_PACKAGES
echo.
echo 📦 Checking required packages...
echo.
python -c "import fastapi; print('✅ FastAPI installed')" 2>nul || echo "❌ FastAPI not installed"
python -c "import aiohttp; print('✅ aiohttp installed')" 2>nul || echo "❌ aiohttp not installed"
python -c "import cloudscraper; print('✅ cloudscraper installed')" 2>nul || echo "❌ cloudscraper not installed"
python -c "import redis; print('✅ redis installed')" 2>nul || echo "❌ redis not installed"
python -c "import bs4; print('✅ BeautifulSoup4 installed')" 2>nul || echo "❌ BeautifulSoup4 not installed"
echo.
pause
goto UTILITIES

:TEST_INTERNET
echo.
echo 🌐 Testing internet connection...
echo.
python -c "import requests; r=requests.get('https://www.google.com', timeout=5); print('✅ Internet connection OK')" 2>nul || echo "❌ Internet connection failed"
python -c "import requests; r=requests.get('https://www.etsy.com', timeout=10); print('✅ Etsy accessible')" 2>nul || echo "❌ Etsy not accessible"
echo.
pause
goto UTILITIES

:INSTALL_PACKAGES
echo.
echo 📦 Installing missing packages...
echo.
pip install fastapi uvicorn aiohttp cloudscraper redis beautifulsoup4 python-dotenv requests
echo.
echo ✅ Package installation completed!
echo.
pause
goto UTILITIES

:SYSTEM_INFO
echo.
echo 📋 System Information:
echo ===============================================
echo Date: %date%
echo Time: %time%
echo Computer: %computername%
echo User: %username%
echo Current Directory: %cd%
echo.
pause
goto UTILITIES

:INVALID_CHOICE
echo.
echo ❌ Invalid choice! Please try again.
echo.
pause
goto MAIN_MENU

:EXIT
cls
echo.
echo ===============================================
echo            👋 GOODBYE!
echo ===============================================
echo.
echo Thank you for using Etsy App Manager!
echo.
echo 🎯 Quick reminder:
echo - Your server runs on http://localhost:8000
echo - Test results are saved as JSON files
echo - Check the logs for any issues
echo.
echo Have a great day! 🚀
echo.
pause
exit
