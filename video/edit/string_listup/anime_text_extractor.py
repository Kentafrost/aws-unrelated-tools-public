import os
import tkinter as tk
from tkinter import filedialog
import subprocess, sys
import re
import json
from datetime import datetime

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
    "pillow>=9.0.0",
    "easyocr"  # Better for stylized text
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
    import easyocr
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
            import easyocr
            print("Packages installed and imported successfully!")
        except ImportError as e2:
            print(f"Still failed to import after installation: {e2}")
            sys.exit(1)
    else:
        sys.exit(1)

# Configure Tesseract path
def configure_tesseract():
    """Configure Tesseract OCR path"""
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME')),
        "tesseract"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"Tesseract configured at: {path}")
            try:
                version = pytesseract.get_tesseract_version()
                print(f"Tesseract version: {version}")
                return True
            except Exception as e:
                print(f"Tesseract test failed: {e}")
                continue
        elif path == "tesseract":
            try:
                pytesseract.pytesseract.tesseract_cmd = path
                version = pytesseract.get_tesseract_version()
                print(f"Tesseract found in PATH, version: {version}")
                return True
            except Exception:
                continue
    
    print("Warning: Tesseract not found.")
    return False

configure_tesseract()

def detect_text_regions(image):
    """Detect potential text regions in the image"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # Text region detection using MSER (Maximally Stable Extremal Regions)
    mser = cv2.MSER_create()
    regions, _ = mser.detectRegions(gray)
    
    # Create mask for text regions
    mask = np.zeros_like(gray)
    for region in regions:
        # Filter regions by size (typical text characteristics)
        if 50 < len(region) < 2000:  # Reasonable text region size
            hull = cv2.convexHull(region.reshape(-1, 1, 2))
            cv2.fillPoly(mask, [hull], 255)
    
    return mask

def preprocess_for_anime_text(image):
    """Advanced preprocessing specifically for anime text"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    processed_images = []
    
    # 1. Original grayscale
    processed_images.append(('original', gray))
    
    # 2. High contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    processed_images.append(('enhanced', enhanced))
    
    # 3. Text region detection and isolation
    text_mask = detect_text_regions(image)
    
    # Apply mask to enhanced image
    masked = cv2.bitwise_and(enhanced, enhanced, mask=text_mask)
    processed_images.append(('masked', masked))
    
    # 4. Multiple threshold approaches
    # OTSU with different preprocessing
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
    _, thresh_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    processed_images.append(('otsu', thresh_otsu))
    
    # Inverted OTSU for white text on dark backgrounds
    _, thresh_inv = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    processed_images.append(('otsu_inv', thresh_inv))
    
    # 5. Edge-preserving filter for text with effects
    bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
    _, thresh_bilateral = cv2.threshold(bilateral, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    processed_images.append(('bilateral', thresh_bilateral))
    
    # 6. Morphological operations to clean text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
    
    # Remove noise while preserving text
    cleaned = cv2.morphologyEx(thresh_otsu, cv2.MORPH_OPEN, kernel, iterations=1)
    closed = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=1)
    processed_images.append(('morphed', closed))
    
    return processed_images

def extract_text_easyocr(image, reader):
    """Extract text using EasyOCR (better for stylized text)"""
    try:
        # EasyOCR works with BGR images
        if len(image.shape) == 2:
            image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            image_bgr = image
            
        results = reader.readtext(image_bgr, detail=1, paragraph=True)
        
        extracted_texts = []
        for (bbox, text, confidence) in results:
            if confidence > 0.3 and len(text.strip()) > 0:  # Lower threshold for anime text
                extracted_texts.append({
                    'text': text.strip(),
                    'confidence': confidence,
                    'bbox': bbox
                })
        
        return extracted_texts
    except Exception as e:
        return []

def extract_text_tesseract(image):
    """Extract text using Tesseract with anime-optimized configs"""
    configs = [
        '--oem 3 --psm 6 -c tessedit_char_whitelist=あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンー',
        '--oem 3 --psm 8',  # Single word
        '--oem 3 --psm 7',  # Single text line
        '--oem 3 --psm 6',  # Uniform text block
        '--oem 3 --psm 11', # Sparse text
        '--oem 3 --psm 13'  # Raw line
    ]
    
    best_results = []
    
    for config in configs:
        try:
            # Get detailed data
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT, timeout=10)
            
            for i, text in enumerate(data['text']):
                if text.strip() and int(data['conf'][i]) > 20:  # Lower threshold for anime
                    best_results.append({
                        'text': text.strip(),
                        'confidence': int(data['conf'][i]) / 100.0,
                        'bbox': None
                    })
                    
        except Exception as e:
            continue
    
    return best_results

def is_valid_japanese_text(text):
    """Check if extracted text looks like valid Japanese"""
    if not text or len(text.strip()) < 1:
        return False
    
    text = text.strip()
    
    # Count Japanese characters
    hiragana = len(re.findall(r'[\u3040-\u309F]', text))
    katakana = len(re.findall(r'[\u30A0-\u30FF]', text))
    kanji = len(re.findall(r'[\u4E00-\u9FAF]', text))
    
    total_japanese = hiragana + katakana + kanji
    
    # Must have at least some Japanese characters or be reasonable length
    if total_japanese > 0:
        return True
    
    # For non-Japanese text, check if it looks like meaningful text
    if len(text) >= 2 and not re.match(r'^[^\w\s]+$', text):
        return True
    
    return False

def process_video_enhanced(video_path, output_dir):
    """Process video with enhanced anime text detection"""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    # Initialize EasyOCR reader for Japanese and English
    print("Initializing EasyOCR for Japanese text recognition...")
    reader = easyocr.Reader(['ja', 'en'], gpu=False)  # Japanese and English
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"Video info - FPS: {fps:.2f}, Total frames: {total_frames}, Duration: {duration:.2f}s")
    
    filename = os.path.basename(video_path)
    base_name = os.path.splitext(filename)[0]
    
    # Output files
    output_file = os.path.join(output_dir, f"{base_name}_japanese_text.txt")
    detailed_file = os.path.join(output_dir, f"{base_name}_detailed_results.json")
    
    frame_count = 0
    extracted_count = 0
    frame_interval = max(1, int(fps * 2))  # Extract every 2 seconds for better quality
    
    all_results = []
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Enhanced Japanese Text Extraction from: {filename}\n")
        f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"FPS: {fps:.2f}, Duration: {duration:.2f}s\n")
        f.write("="*80 + "\n\n")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                try:
                    print(f"Processing frame {frame_count} ({frame_count/total_frames*100:.1f}%)")
                    
                    # Get processed images for this frame
                    processed_images = preprocess_for_anime_text(frame)
                    
                    frame_results = []
                    
                    # Try EasyOCR on different processed versions
                    for name, img in processed_images:
                        easyocr_results = extract_text_easyocr(img, reader)
                        for result in easyocr_results:
                            result['method'] = f'easyocr_{name}'
                            if is_valid_japanese_text(result['text']):
                                frame_results.append(result)
                    
                    # Try Tesseract on best processed images
                    for name, img in processed_images[:3]:  # Test on top 3 processed images
                        tesseract_results = extract_text_tesseract(img)
                        for result in tesseract_results:
                            result['method'] = f'tesseract_{name}'
                            if is_valid_japanese_text(result['text']):
                                frame_results.append(result)
                    
                    # Process results for this frame
                    if frame_results:
                        timestamp = frame_count / fps if fps > 0 else frame_count / 30
                        
                        # Sort by confidence and remove duplicates
                        frame_results.sort(key=lambda x: x['confidence'], reverse=True)
                        unique_texts = set()
                        final_results = []
                        
                        for result in frame_results:
                            if result['text'] not in unique_texts:
                                unique_texts.add(result['text'])
                                final_results.append(result)
                        
                        if final_results:
                            f.write(f"[Frame {frame_count} - Time: {timestamp:.2f}s]\n")
                            for i, result in enumerate(final_results[:3]):  # Top 3 results
                                f.write(f"  {i+1}. {result['text']} (confidence: {result['confidence']:.2f}, method: {result['method']})\n")
                            f.write("-" * 50 + "\n\n")
                            
                            # Store for detailed JSON output
                            all_results.append({
                                'frame': frame_count,
                                'timestamp': timestamp,
                                'results': final_results
                            })
                            
                            extracted_count += 1
                            print(f"  Found {len(final_results)} text entries")
                
                except Exception as e:
                    print(f"Error processing frame {frame_count}: {e}")
            
            frame_count += 1
            
            # Progress indicator
            if frame_count % (frame_interval * 5) == 0:
                progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
                print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")
    
    # Save detailed results as JSON
    with open(detailed_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    cap.release()
    
    print(f"\nCompleted: {filename}")
    print(f"Extracted text from {extracted_count} frames")
    print(f"Results saved to: {output_file}")
    print(f"Detailed data saved to: {detailed_file}")
    return extracted_count

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    print("Enhanced Anime Japanese Text Extractor")
    print("=====================================")
    
    # For testing, use hardcoded path
    selected_folder = fold_path
    
    if not os.path.exists(selected_folder):
        print("Please select a folder containing MP4 videos...")
        selected_folder = filedialog.askdirectory(title="Select folder with anime videos")
    
    if not selected_folder:
        print("No folder selected. Exiting...")
        sys.exit(0)
    
    print(f"Selected folder: {selected_folder}")
    
    # Create results directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(current_dir, "enhanced_results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Find video files
    video_files = [f for f in os.listdir(selected_folder) if f.lower().endswith((".mp4", ".avi", ".mov"))]
    
    if not video_files:
        print("No video files found in the selected folder.")
        sys.exit(0)
    
    print(f"Found {len(video_files)} video file(s): {video_files}")
    
    total_extracted = 0
    for filename in video_files[:1]:  # Process first video for testing
        video_path = os.path.join(selected_folder, filename)
        print(f"\nProcessing: {filename}")
        extracted = process_video_enhanced(video_path, results_dir)
        total_extracted += extracted
    
    print(f"\n🎉 Processing completed!")
    print(f"Total text extractions: {total_extracted}")
    print(f"Results saved in: {results_dir}")
    
    root.destroy()
