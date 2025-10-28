import os
import tkinter as tk
from tkinter import filedialog
import subprocess, sys
import re
import json

json_path = os.path.join(os.path.dirname(__file__), 'package_versions.json')
with open(json_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)
fold_path = json_data.get("fold_path", "")

# Updated packages with compatible versions
packages_to_install = [
    "numpy>=1.21.0",
    "opencv-python>=4.8.0",
    "pytesseract>=0.3.10",
    "pillow>=9.0.0"
]

def install_packages():
    """Install required packages with proper versions"""
    try:
        for package in packages_to_install:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
        print("All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages: {e}")
        return False
    return True

# Try to import packages, install if missing
try:
    import cv2
    import pytesseract
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
    print("All packages imported successfully!")
except ImportError as e:
    print(f"Missing package detected: {e}")
    print("Installing required packages...")
    if install_packages():
        try:
            import cv2
            import pytesseract
            import numpy as np
            from PIL import Image, ImageEnhance, ImageFilter
            print("Packages installed and imported successfully!")
        except ImportError as e2:
            print(f"Still failed to import after installation: {e2}")
            sys.exit(1)
    else:
        sys.exit(1)

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def download_japanese_language_data():
    """Download Japanese language data for Tesseract"""
    import urllib.request
    
    tessdata_dir = r"C:\Program Files\Tesseract-OCR\tessdata"
    jpn_file = os.path.join(tessdata_dir, "jpn.traineddata")
    
    if os.path.exists(jpn_file):
        print("Japanese language data already exists")
        return True
    
    try:
        print("Downloading Japanese language data...")
        url = "https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata"
        
        # Download to current directory first
        local_file = "jpn.traineddata"
        urllib.request.urlretrieve(url, local_file)
        
        # Try to copy to tessdata directory
        import shutil
        try:
            shutil.copy(local_file, jpn_file)
            os.remove(local_file)
            print("Japanese language data installed successfully!")
            return True
        except PermissionError:
            print(f"Please manually copy {local_file} to {tessdata_dir}")
            print("You may need administrator privileges")
            return False
            
    except Exception as e:
        print(f"Error downloading Japanese data: {e}")
        return False

def enhance_image_for_text(image):
    """Advanced image preprocessing specifically for anime text"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    enhanced_images = []
    
    # 1. Original grayscale
    enhanced_images.append(gray)
    
    # 2. Contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    contrast_enhanced = clahe.apply(gray)
    enhanced_images.append(contrast_enhanced)
    
    # 3. Gaussian blur to smooth text
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    enhanced_images.append(blurred)
    
    # 4. Bilateral filter to preserve edges while smoothing
    bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
    enhanced_images.append(bilateral)
    
    # 5. Multiple threshold techniques
    # OTSU threshold
    _, thresh_otsu = cv2.threshold(contrast_enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    enhanced_images.append(thresh_otsu)
    
    # Inverted OTSU (for white text on dark background)
    _, thresh_otsu_inv = cv2.threshold(contrast_enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    enhanced_images.append(thresh_otsu_inv)
    
    # Adaptive threshold
    adaptive_thresh = cv2.adaptiveThreshold(contrast_enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
    enhanced_images.append(adaptive_thresh)
    
    # 6. Morphological operations to clean up text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    
    # Opening to remove noise
    opened = cv2.morphologyEx(thresh_otsu, cv2.MORPH_OPEN, kernel)
    enhanced_images.append(opened)
    
    # Closing to connect text components
    closed = cv2.morphologyEx(thresh_otsu, cv2.MORPH_CLOSE, kernel)
    enhanced_images.append(closed)
    
    # 7. Edge enhancement
    edges = cv2.Canny(contrast_enhanced, 50, 150)
    enhanced_images.append(edges)
    
    return enhanced_images

def is_likely_japanese_text(text):
    """Check if text contains Japanese characters or patterns"""
    if not text or len(text.strip()) < 1:
        return False
    
    # Count different character types
    hiragana_count = len(re.findall(r'[\u3040-\u309F]', text))
    katakana_count = len(re.findall(r'[\u30A0-\u30FF]', text))
    kanji_count = len(re.findall(r'[\u4E00-\u9FAF]', text))
    
    japanese_chars = hiragana_count + katakana_count + kanji_count
    
    # Also check for common Japanese patterns in romanized form
    japanese_patterns = [
        r'(?i)(desu|masu|kara|nani|sore|kore|watashi|anata|arigatou)',
        r'(?i)(hai|iie|onegai|sumimasen|gomen|demo|doko|naze)',
        r'(?i)(chan|kun|san|sama|sensei|senpai)'
    ]
    
    pattern_matches = sum(1 for pattern in japanese_patterns if re.search(pattern, text))
    
    return japanese_chars > 0 or pattern_matches > 0

def clean_and_validate_japanese_text(text):
    """Advanced cleaning for Japanese text"""
    if not text or not text.strip():
        return ""
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove obvious OCR artifacts
    # Remove isolated punctuation and symbols
    text = re.sub(r'\b[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\s]\b', '', text)
    
    # Remove isolated single characters that are likely artifacts
    words = text.split()
    cleaned_words = []
    
    for word in words:
        # Keep if it's a Japanese character, or a reasonable English/number sequence
        if (len(word) >= 2 or 
            any('\u3040' <= c <= '\u309F' or '\u30A0' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FAF' for c in word) or
            word.isdigit()):
            cleaned_words.append(word)
    
    result = ' '.join(cleaned_words)
    
    # Must have some meaningful content
    if len(result.replace(' ', '')) < 2:
        return ""
    
    return result

def extract_text_with_confidence(image, configs):
    """Extract text with confidence scoring"""
    best_text = ""
    best_confidence = 0
    best_japanese_score = 0
    
    for config in configs:
        try:
            # Get text with confidence data
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT, timeout=15)
            
            # Filter high-confidence text
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 30]
            texts = [data['text'][i] for i, conf in enumerate(data['conf']) if int(conf) > 30 and data['text'][i].strip()]
            
            if not texts:
                continue
                
            combined_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Score based on Japanese likelihood
            japanese_score = 1 if is_likely_japanese_text(combined_text) else 0
            
            # Combined scoring
            total_score = avg_confidence + (japanese_score * 50)  # Boost Japanese text
            
            if total_score > best_confidence:
                best_confidence = total_score
                best_text = combined_text
                best_japanese_score = japanese_score
                
        except Exception as e:
            continue
    
    return best_text, best_confidence, best_japanese_score

# Download Japanese data if needed
download_japanese_language_data()

# Main processing
root = tk.Tk()
root.withdraw()

print("Please select a folder containing MP4 videos...")
selected_folder = fold_path

if not selected_folder:
    print("No folder selected. Exiting...")
    sys.exit(0)

print(f"Selected folder: {selected_folder}")
current_dir = os.path.dirname(os.path.abspath(__file__))

# Find video files
video_files = [f for f in os.listdir(selected_folder) if f.lower().endswith((".mp4", ".avi", ".mov"))]

if not video_files:
    print("No video files found in the selected folder.")
    sys.exit(0)

print(f"Found {len(video_files)} video file(s): {video_files}")

# Enhanced OCR configurations for Japanese text
enhanced_configs = [
    # Japanese-specific configurations
    '--oem 3 --psm 6 -l jpn',              # Japanese, uniform text block
    '--oem 3 --psm 8 -l jpn',              # Japanese, single word
    '--oem 3 --psm 7 -l jpn',              # Japanese, single text line
    '--oem 3 --psm 13 -l jpn',             # Japanese, raw line
    '--oem 3 --psm 6 -l jpn+eng',          # Japanese + English
    '--oem 1 --psm 6 -l jpn',              # Different engine, Japanese
    
    # Fallback configurations
    '--oem 3 --psm 6',                     # Basic uniform text
    '--oem 3 --psm 8',                     # Basic single word
    '--oem 3 --psm 7',                     # Basic single line
    '--oem 3 --psm 11',                    # Sparse text
    '--oem 3 --psm 13',                    # Raw line
]

for filename in video_files:
    video_path = os.path.join(selected_folder, filename)
    print(f"\nProcessing video: {video_path}")

    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Error: Could not open video file {filename}")
            continue
            
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        print(f"Video info - FPS: {fps:.2f}, Total frames: {total_frames}, Duration: {duration:.2f}s")
        
        frame_count = 0
        extracted_count = 0
        
        # Extract every 2 seconds for more thorough analysis
        frame_interval = max(1, int(fps * 2)) if fps > 0 else 60

        # Create output files
        base_name = os.path.splitext(filename)[0]
        output_file = os.path.join(current_dir, "results", f"{base_name}_enhanced_output.txt")
        raw_output_file = os.path.join(current_dir, "results", f"{base_name}_enhanced_raw_output.txt")
        
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))

        with open(output_file, "w", encoding="utf-8") as f, \
             open(raw_output_file, "w", encoding="utf-8") as f_raw:
            
            f.write(f"Enhanced Japanese OCR Analysis\n")
            f.write(f"Video: {filename}\n")
            f.write(f"FPS: {fps:.2f}, Duration: {duration:.2f}s\n")
            f.write("="*60 + "\n\n")
            
            f_raw.write(f"Enhanced Raw OCR Output\n")
            f_raw.write(f"Video: {filename}\n")
            f_raw.write(f"FPS: {fps:.2f}, Duration: {duration:.2f}s\n")
            f_raw.write("="*60 + "\n\n")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    try:
                        # Enhanced preprocessing
                        enhanced_images = enhance_image_for_text(frame)
                        
                        best_overall_text = ""
                        best_overall_confidence = 0
                        best_japanese_score = 0
                        raw_results = []
                        
                        # Try OCR on each enhanced image
                        for i, enhanced_img in enumerate(enhanced_images):
                            text, confidence, jp_score = extract_text_with_confidence(enhanced_img, enhanced_configs)
                            
                            if text:
                                raw_results.append(f"Method {i+1}: {text}")
                                
                                if confidence > best_overall_confidence:
                                    best_overall_confidence = confidence
                                    best_overall_text = text
                                    best_japanese_score = jp_score
                        
                        # Process the best result
                        if best_overall_text:
                            cleaned_text = clean_and_validate_japanese_text(best_overall_text)
                            
                            timestamp = frame_count / fps if fps > 0 else frame_count / 60
                            
                            # Only save if we have meaningful text
                            if cleaned_text or (best_japanese_score > 0 and best_overall_text.strip()):
                                print(f"Frame {frame_count} ({timestamp:.1f}s): Found text!")
                                if best_japanese_score > 0:
                                    print(f"  Japanese detected: '{best_overall_text[:50]}'")
                                if cleaned_text:
                                    print(f"  Cleaned: '{cleaned_text[:50]}'")
                                
                                # Write to cleaned output
                                f.write(f"[Frame {frame_count} - Time: {timestamp:.2f}s]\n")
                                f.write(f"Confidence: {best_overall_confidence:.1f}\n")
                                f.write(f"Japanese Score: {best_japanese_score}\n")
                                f.write(f"Raw: {best_overall_text}\n")
                                if cleaned_text:
                                    f.write(f"Cleaned: {cleaned_text}\n")
                                f.write("-" * 40 + "\n\n")
                                
                                # Write to raw output
                                f_raw.write(f"[Frame {frame_count} - Time: {timestamp:.2f}s]\n")
                                f_raw.write(f"Confidence: {best_overall_confidence:.1f}\n")
                                for result in raw_results:
                                    f_raw.write(f"{result}\n")
                                f_raw.write("-" * 40 + "\n\n")
                                
                                extracted_count += 1
                        
                    except Exception as ocr_error:
                        print(f"OCR error at frame {frame_count}: {ocr_error}")
                        
                frame_count += 1
                
                # Progress indicator
                if frame_count % (frame_interval * 5) == 0:
                    progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
                    print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")

        cap.release()
        print(f"\nCompleted: {filename}")
        print(f"Extracted meaningful text from {extracted_count} frames")
        print(f"Enhanced output saved to: {output_file}")
        print(f"Raw output saved to: {raw_output_file}")
        print("-" * 60)
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        continue

print("\nAll videos processed with enhanced Japanese OCR!")
root.destroy()
