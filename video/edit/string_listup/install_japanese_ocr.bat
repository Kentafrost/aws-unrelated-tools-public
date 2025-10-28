@echo off
echo Installing Japanese Language Data for Tesseract OCR
echo ================================================

echo.
echo Step 1: Checking if jpn.traineddata exists in current directory...
if exist "jpn.traineddata" (
    echo ✓ Found jpn.traineddata in current directory
) else (
    echo ✗ jpn.traineddata not found. Please download it first.
    echo Download from: https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata
    pause
    exit /b 1
)

echo.
echo Step 2: Checking Tesseract installation...
if exist "C:\Program Files\Tesseract-OCR\tessdata" (
    echo ✓ Found Tesseract tessdata directory
    set "TESSDATA_DIR=C:\Program Files\Tesseract-OCR\tessdata"
) else if exist "C:\Program Files (x86)\Tesseract-OCR\tessdata" (
    echo ✓ Found Tesseract tessdata directory (x86)
    set "TESSDATA_DIR=C:\Program Files (x86)\Tesseract-OCR\tessdata"
) else (
    echo ✗ Tesseract tessdata directory not found
    echo Please install Tesseract OCR first
    pause
    exit /b 1
)

echo.
echo Step 3: Copying Japanese language data...
echo Copying to: %TESSDATA_DIR%\jpn.traineddata

copy "jpn.traineddata" "%TESSDATA_DIR%\jpn.traineddata"

if %ERRORLEVEL% EQU 0 (
    echo ✓ Successfully installed Japanese language data!
    echo.
    echo Testing Japanese OCR capability...
    tesseract --list-langs | findstr jpn
    if %ERRORLEVEL% EQU 0 (
        echo ✓ Japanese language is now available in Tesseract!
    ) else (
        echo ⚠ Japanese language might not be fully configured
    )
) else (
    echo ✗ Failed to copy file. You may need to run as Administrator.
    echo.
    echo Manual installation steps:
    echo 1. Right-click on this batch file and select "Run as administrator"
    echo 2. Or manually copy jpn.traineddata to: %TESSDATA_DIR%
)

echo.
echo Installation complete!
pause
