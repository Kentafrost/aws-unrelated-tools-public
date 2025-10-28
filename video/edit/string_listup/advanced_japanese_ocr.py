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

# Only use packages we already have
try:
    import cv2
    import pytesseract
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter
    print("All packages imported successfully!")
except ImportError as e:
    print(f"Missing package detected: {e}")
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
    """Advanced text region detection using multiple methods"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # Method 1: MSER (Maximally Stable Extremal Regions) - good for text
    mser = cv2.MSER_create()
    regions, _ = mser.detectRegions(gray)
    
    mask = np.zeros_like(gray)
    for region in regions:
        if 20 < len(region) < 1000:  # Filter by region size
            hull = cv2.convexHull(region.reshape(-1, 1, 2))
            cv2.fillPoly(mask, [hull], 255)
    
    # Method 2: Edge-based text detection
    edges = cv2.Canny(gray, 50, 200)
    
    # Find contours from edges
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours that look like text
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Text-like aspect ratio and size
        if 10 < w < 200 and 8 < h < 50 and 0.2 < h/w < 5:
            cv2.rectangle(mask, (x, y), (x+w, y+h), 255, -1)
    
    return mask

def advanced_preprocess_for_japanese(image):
    """Advanced preprocessing specifically designed for Japanese anime text"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    processed_images = []
    
    # 1. Original
    processed_images.append(('original', gray))
    
    # 2. Super contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(4,4))
    enhanced = clahe.apply(gray)
    processed_images.append(('enhanced', enhanced))
    
    # 3. Text region isolation
    text_mask = detect_text_regions(image)
    
    # Apply text region mask
    masked = cv2.bitwise_and(enhanced, enhanced, mask=text_mask)
    # Fill background with white
    masked[text_mask == 0] = 255
    processed_images.append(('masked', masked))
    
    # 4. Multiple sophisticated thresholding
    # OTSU on enhanced
    _, thresh1 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    processed_images.append(('otsu_enhanced', thresh1))
    
    # OTSU inverted (for white text on dark background)
    _, thresh2 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    processed_images.append(('otsu_inv', thresh2))
    
    # Triangle threshold (good for bimodal distributions)
    _, thresh3 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)
    processed_images.append(('triangle', thresh3))
    
    # Adaptive threshold with different parameters
    adaptive1 = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    processed_images.append(('adaptive_gauss', adaptive1))
    
    adaptive2 = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 3)
    processed_images.append(('adaptive_mean', adaptive2))
    
    # 5. Edge-preserving smoothing before threshold
    bilateral = cv2.bilateralFilter(gray, 9, 80, 80)
    _, thresh_bilateral = cv2.threshold(bilateral, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    processed_images.append(('bilateral_otsu', thresh_bilateral))
    
    # 6. Morphological operations for text cleanup
    kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    kernel_medium = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    
    # Clean small noise
    cleaned1 = cv2.morphologyEx(thresh1, cv2.MORPH_OPEN, kernel_small)
    cleaned1 = cv2.morphologyEx(cleaned1, cv2.MORPH_CLOSE, kernel_medium)
    processed_images.append(('morph_cleaned', cleaned1))
    
    # 7. Gradient-based enhancement
    gradient_x = cv2.Sobel(enhanced, cv2.CV_64F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(enhanced, cv2.CV_64F, 0, 1, ksize=3)
    gradient_mag = np.sqrt(gradient_x**2 + gradient_y**2)
    gradient_mag = np.uint8(gradient_mag * 255 / gradient_mag.max())
    _, thresh_gradient = cv2.threshold(gradient_mag, 50, 255, cv2.THRESH_BINARY)
    processed_images.append(('gradient', thresh_gradient))
    
    return processed_images

def extract_text_with_confidence(image):
    """Extract text using multiple Tesseract configurations optimized for Japanese"""
    
    # Japanese-optimized configurations
    configs = [
        # Basic configurations
        '--oem 3 --psm 6',   # Uniform text block
        '--oem 3 --psm 7',   # Single text line
        '--oem 3 --psm 8',   # Single word
        '--oem 3 --psm 11',  # Sparse text
        '--oem 3 --psm 13',  # Raw line
        
        # With language hints (even without jpn data, sometimes helps)
        '--oem 3 --psm 6 -l eng',
        '--oem 3 --psm 7 -l eng',
        '--oem 3 --psm 8 -l eng',
        
        # Whitelist for common Japanese patterns (romaji)
        '--oem 3 --psm 6 -c tessedit_char_whitelist=あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンーABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789',
        '--oem 3 --psm 7 -c tessedit_char_whitelist=あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンーABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789',
    ]
    
    best_results = []
    
    for config in configs:
        try:
            # Get detailed OCR data
            data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT, timeout=10)
            
            # Process each detected word/character
            for i, text in enumerate(data['text']):
                confidence = int(data['conf'][i])
                
                # More lenient filtering for anime text
                if text.strip() and confidence > 15:  # Lower threshold
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    best_results.append({
                        'text': text.strip(),
                        'confidence': confidence / 100.0,
                        'bbox': (x, y, w, h),
                        'config': config
                    })
                    
        except Exception as e:
            continue
    
    return best_results

def is_meaningful_japanese_text(text):
    """Enhanced Japanese text validation"""
    if not text or len(text.strip()) < 1:
        return False
    
    text = text.strip()
    
    # Count character types
    hiragana = len(re.findall(r'[\u3040-\u309F]', text))
    katakana = len(re.findall(r'[\u30A0-\u30FF]', text))
    kanji = len(re.findall(r'[\u4E00-\u9FAF]', text))
    alphanumeric = len(re.findall(r'[A-Za-z0-9]', text))
    
    total_japanese = hiragana + katakana + kanji
    total_chars = len(text)
    
    # Scoring system
    score = 0
    
    # Japanese characters get high score
    if total_japanese > 0:
        score += total_japanese * 3
    
    # Alphanumeric text (might be romanized Japanese)
    if alphanumeric > 0 and len(text) > 1:
        score += alphanumeric
    
    # Length bonus for longer meaningful text
    if len(text) >= 2:
        score += 2
    if len(text) >= 4:
        score += 3
    
    # Penalty for mostly symbols
    symbol_count = len(re.findall(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
    if symbol_count > len(text) * 0.7:  # More than 70% symbols
        score -= symbol_count * 2
    
    # Common Japanese words/patterns bonus
    japanese_patterns = [
        r'[あいうえお]',  # Hiragana vowels
        r'[かきくけこ]',  # Ka group
        r'[さしすせそ]',  # Sa group
        r'です',          # Desu
        r'ます',          # Masu
        r'[アイウエオ]',  # Katakana vowels
    ]
    
    for pattern in japanese_patterns:
        if re.search(pattern, text):
            score += 5
    
    return score > 3  # Minimum score threshold

def consolidate_text_results(results):
    """Consolidate overlapping or duplicate text results"""
    if not results:
        return []
    
    # Sort by confidence
    sorted_results = sorted(results, key=lambda x: x['confidence'], reverse=True)
    
    consolidated = []
    used_texts = set()
    
    for result in sorted_results:
        text = result['text']
        
        # Skip if we've seen this exact text
        if text in used_texts:
            continue
        
        # Skip if this text is contained in a longer text we already have
        is_substring = False
        texts_to_remove = []
        
        for existing_text in list(used_texts):  # Convert to list to avoid iteration error
            if text in existing_text or existing_text in text:
                if len(text) <= len(existing_text):
                    is_substring = True
                    break
                else:
                    # Mark shorter existing text for removal
                    texts_to_remove.append(existing_text)
        
        # Remove shorter texts
        for text_to_remove in texts_to_remove:
            used_texts.discard(text_to_remove)
            consolidated = [r for r in consolidated if r['text'] != text_to_remove]
        
        if not is_substring and is_meaningful_japanese_text(text):
            consolidated.append(result)
            used_texts.add(text)
    
    return consolidated[:3]  # Return top 3 results only

def process_video_advanced(video_path, output_dir):
    """Advanced video processing for Japanese anime text"""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"Video info - FPS: {fps:.2f}, Total frames: {total_frames}, Duration: {duration:.2f}s")
    
    filename = os.path.basename(video_path)
    base_name = os.path.splitext(filename)[0]
    
    # Output files
    output_file = os.path.join(output_dir, f"{base_name}_japanese_extracted.txt")
    detailed_file = os.path.join(output_dir, f"{base_name}_detailed_analysis.json")
    
    frame_count = 0
    extracted_count = 0
    frame_interval = max(1, int(fps * 1.5))  # Extract every 1.5 seconds
    
    all_results = []
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Advanced Japanese Text Extraction\n")
        f.write(f"Video: {filename}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Settings: FPS: {fps:.2f}, Duration: {duration:.2f}s, Interval: {frame_interval} frames\n")
        f.write("="*80 + "\n\n")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                try:
                    print(f"Analyzing frame {frame_count} ({frame_count/total_frames*100:.1f}%)")
                    
                    # Get all preprocessed versions
                    processed_images = advanced_preprocess_for_japanese(frame)
                    
                    frame_results = []
                    
                    # Extract text from each processed image
                    for name, img in processed_images:
                        try:
                            results = extract_text_with_confidence(img)
                            for result in results:
                                result['preprocessing'] = name
                                frame_results.append(result)
                        except Exception as e:
                            print(f"  Error processing {name}: {e}")
                            continue
                    
                    # Consolidate and filter results
                    final_results = consolidate_text_results(frame_results)
                    
                    if final_results:
                        timestamp = frame_count / fps if fps > 0 else frame_count / 30
                        
                        f.write(f"[Frame {frame_count} - Time: {timestamp:.2f}s]\n")
                        
                        for i, result in enumerate(final_results):
                            f.write(f"  {i+1}. \"{result['text']}\" ")
                            f.write(f"(confidence: {result['confidence']:.2f}, method: {result['preprocessing']})\n")
                        
                        f.write("-" * 60 + "\n\n")
                        
                        # Store detailed results
                        all_results.append({
                            'frame': frame_count,
                            'timestamp': timestamp,
                            'results': final_results
                        })
                        
                        extracted_count += 1
                        
                        # Show what we found
                        print(f"  ✓ Found {len(final_results)} text entries:")
                        for result in final_results[:2]:  # Show top 2
                            print(f"    \"{result['text']}\" (conf: {result['confidence']:.2f})")
                
                except Exception as e:
                    print(f"Error processing frame {frame_count}: {e}")
            
            frame_count += 1
            
            # Progress updates
            if frame_count % (frame_interval * 10) == 0:
                progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
                print(f"Overall progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")
    
    # Save detailed JSON results
    with open(detailed_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    cap.release()
    
    print(f"\n🎌 Analysis completed for: {filename}")
    print(f"📊 Extracted meaningful text from {extracted_count} frames")
    print(f"📄 Results saved to: {output_file}")
    print(f"📋 Detailed data: {detailed_file}")
    
    return extracted_count

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    print("🎌 Advanced Japanese Anime Text Extractor")
    print("==========================================")
    print("Specialized for detecting Japanese text in anime videos")
    print()
    
    # Test folder
    test_folder = fold_path
    
    if os.path.exists(test_folder):
        selected_folder = test_folder
        print(f"Using test folder: {selected_folder}")
    else:
        print("Please select a folder containing anime videos...")
        selected_folder = filedialog.askdirectory(title="Select anime video folder")
    
    if not selected_folder:
        print("No folder selected. Exiting...")
        sys.exit(0)
    
    # Create enhanced results directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(current_dir, "japanese_text_results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Find video files
    video_files = [f for f in os.listdir(selected_folder) 
                   if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))]
    
    if not video_files:
        print("❌ No video files found in the selected folder.")
        sys.exit(0)
    
    print(f"📁 Found {len(video_files)} video file(s):")
    for i, f in enumerate(video_files, 1):
        print(f"  {i}. {f}")
    print()
    
    total_extracted = 0
    
    # Process first video for testing
    for filename in video_files[:1]:
        video_path = os.path.join(selected_folder, filename)
        print(f"🎬 Processing: {filename}")
        print("=" * 60)
        
        extracted = process_video_advanced(video_path, results_dir)
        total_extracted += extracted
        
        print()
    
    print("🎉 Processing completed!")
    print(f"📈 Total meaningful text extractions: {total_extracted}")
    print(f"📂 All results saved in: {results_dir}")
    
    root.destroy()
