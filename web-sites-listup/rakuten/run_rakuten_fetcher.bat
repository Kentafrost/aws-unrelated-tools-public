@echo off
echo 🛍️ Starting Rakuten Product Fetcher...
echo.

cd /d "%~dp0"
node rakuten_item_listup_builtin.js

echo.
echo ✅ Script completed!
echo Press any key to exit...
pause > nul