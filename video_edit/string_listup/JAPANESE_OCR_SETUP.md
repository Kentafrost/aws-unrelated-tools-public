# Manual Installation Guide for Japanese OCR

## Step 1: Download Japanese Language Data

1. Open your web browser
2. Go to: https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata
3. Save the file to your Downloads folder

## Step 2: Install the Language Data

### Option A: Automatic (if you have admin rights)
Run the enhanced script - it will try to install automatically.

### Option B: Manual Installation
1. Open File Explorer
2. Navigate to: `C:\Program Files\Tesseract-OCR\tessdata\`
3. Copy the downloaded `jpn.traineddata` file into this folder
4. You may need to run as Administrator:
   - Right-click on File Explorer
   - Select "Run as administrator"
   - Then copy the file

## Step 3: Verify Installation

Run this command in PowerShell to test:
```powershell
cd "C:\Program Files\Tesseract-OCR"
.\tesseract.exe --list-langs
```

You should see "jpn" in the list of available languages.

## Step 4: Run Enhanced OCR Script

The enhanced script includes:
- ✅ Japanese language support
- ✅ Advanced image preprocessing for anime text
- ✅ Confidence-based text selection
- ✅ Japanese text pattern recognition
- ✅ Better filtering of OCR artifacts

## Common Issues and Solutions

### Issue: "Permission denied" when copying language data
**Solution**: 
- Run PowerShell as Administrator
- Use this command to copy:
```powershell
Copy-Item "C:\Users\[YourUsername]\Downloads\jpn.traineddata" "C:\Program Files\Tesseract-OCR\tessdata\"
```

### Issue: Still getting garbled text
**Possible causes**:
- Anime text uses stylized fonts that don't match OCR training data
- Text is too small or has special effects
- Background is too complex

**Solutions**:
- The enhanced script tries multiple preprocessing techniques
- Results will be better but may still not be perfect for heavily stylized anime text
- Consider using specialized anime OCR tools for better accuracy

### Issue: OCR is slow
**Solution**: 
- The enhanced script processes fewer frames (every 2 seconds instead of every 1 second)
- Each frame uses multiple processing methods for better accuracy
- This is normal for comprehensive analysis

## Expected Results

With the enhanced script, you should see:
- Better detection of actual Japanese characters (ひらがな, カタカナ, 漢字)
- Confidence scores for each detection
- Multiple processing methods tried per frame
- Filtered results that remove obvious OCR artifacts
- Separate files for cleaned and raw results
