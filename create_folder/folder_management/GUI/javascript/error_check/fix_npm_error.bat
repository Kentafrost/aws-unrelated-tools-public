@echo off
echo =================================
echo NPM EBADF Error Fix Script
echo =================================
echo.

echo Step 1: Cleaning npm cache...
npm cache clean --force
if %errorlevel% neq 0 (
    echo Cache cleaning failed, continuing...
)

echo.
echo Step 2: Removing node_modules...
if exist "node_modules" (
    rmdir /s /q "node_modules"
    echo node_modules removed
) else (
    echo node_modules directory not found
)

echo.
echo Step 3: Removing package-lock.json...
if exist "package-lock.json" (
    del "package-lock.json"
    echo package-lock.json removed
) else (
    echo package-lock.json not found
)

echo.
echo Step 4: Installing dependencies with alternative method...
echo Trying npm install with verbose logging...
npm install --verbose --no-optional
if %errorlevel% neq 0 (
    echo.
    echo Standard install failed, trying alternative methods...
    
    echo.
    echo Method 2: Using --legacy-peer-deps...
    npm install --legacy-peer-deps
    if %errorlevel% neq 0 (
        echo.
        echo Method 3: Using yarn (if available)...
        where yarn >nul 2>nul
        if %errorlevel% equ 0 (
            yarn install
        ) else (
            echo Yarn not found, trying final method...
            echo.
            echo Method 4: Installing fluent-ffmpeg specifically...
            npm install fluent-ffmpeg --no-optional --verbose
        )
    )
)

echo.
echo =================================
echo Installation process completed
echo =================================
echo.
echo Checking if fluent-ffmpeg is installed...
npm list fluent-ffmpeg

pause