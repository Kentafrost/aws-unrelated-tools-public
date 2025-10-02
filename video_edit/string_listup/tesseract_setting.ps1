# install tesseract-ocr for Japanese text recognition
# 1. Install Japanese Language Data for Tesseract
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata' -OutFile '$env:TEMP\jpn.traineddata'"
powershell -Command "Start-Process powershell -ArgumentList 'Copy-Item \"$env:TEMP\jpn.traineddata\" \"C:\Program Files\Tesseract-OCR\tessdata\jpn.traineddata\"' -Verb RunAs"
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata' -OutFile 'jpn.traineddata'"

# 2-4. Enhanced Script with All Improvements
# invoke enhanced_video_ocr.py
python3 enhanced_video_ocr.py
cd "g:\My Drive\IT_Learning\Git\aws-unrelated-tools-private\video-edit" && dir "C:\Program Files\Tesseract-OCR\tessdata\eng.traineddata"