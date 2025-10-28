import os
import tkinter as tk
from tkinter import filedialog
import subprocess, sys
import re
import shutil
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
    print("All packages imported successfully!")
except ImportError as e:
    print(f"Missing package detected: {e}")
    print("Installing required packages...")
    if install_packages():
        try:
            import cv2
            import pytesseract
            import numpy as np
            print("Packages installed and imported successfully!")
        except ImportError as e2:
            print(f"Still failed to import after installation: {e2}")
            sys.exit(1)
    else:
        sys.exit(1)

# Configure Tesseract path (adjust if needed)
def configure_tesseract():
    
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME')),
        "tesseract"  # If in PATH
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"Tesseract configured at: {path}")
            # Test Tesseract
            try:
                version = pytesseract.get_tesseract_version()
                print(f"Tesseract version: {version}")
                
                # Check and setup Japanese language data
                setup_japanese_language_data(path)
                return True
            except Exception as e:
                print(f"Tesseract test failed: {e}")
                continue
        elif path == "tesseract":
            try:
                pytesseract.pytesseract.tesseract_cmd = path
                version = pytesseract.get_tesseract_version()
                print(f"Tesseract found in PATH, version: {version}")
                setup_japanese_language_data("tesseract")
                return True
            except Exception:
                continue
    
    print("Warning: Tesseract not found. Please install Tesseract OCR.")
    print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    return False

def setup_japanese_language_data(tesseract_path):
    
    # Find tessdata directory
    if tesseract_path == "tesseract":
        tessdata_dir = None
        # Try to find tessdata directory
        try:
            result = subprocess.run([tesseract_path, 
                                     "--print-parameters"], 
                                    capture_output=True, 
                                    text=True)
            for line in result.stderr.split('\n'):
                if 'tessdata' in line and 'TESSDATA_PREFIX' in line:
                    tessdata_dir = line.split()[-1]
                    break
        except:
            pass
    else:
        tessdata_dir = os.path.join(os.path.dirname(tesseract_path), "tessdata")
    
    if tessdata_dir and os.path.exists(tessdata_dir):
        jpn_data_path = os.path.join(tessdata_dir, "jpn.traineddata")
        
        if not os.path.exists(jpn_data_path):
            # Check if we have the downloaded file in current directory
            current_jpn_path = os.path.join(os.getcwd(), "jpn.traineddata")
            if os.path.exists(current_jpn_path):
                try:
                    shutil.copy2(current_jpn_path, jpn_data_path)
                    print("Japanese language data installed successfully!")
                except PermissionError:
                    print(f"Permission denied. Please manually copy 'jpn.traineddata' to: {tessdata_dir}")
                    print("You may need to run as administrator.")
            else:
                print(f"Japanese language data not found. Please download jpn.traineddata and place it in: {tessdata_dir}")
        else:
            print("Japanese language data already installed!")
    else:
        print("Could not locate tessdata directory")

def check_japanese_language_data():
    try:
        # Test Japanese OCR capability without changing TESSDATA_PREFIX
        import PIL.Image
        import numpy as np
        
        # Create a test image
        test_image = np.ones((100, 200, 3), dtype=np.uint8) * 255
        test_pil = PIL.Image.fromarray(test_image)
        
        # Try to use Japanese language
        pytesseract.image_to_string(test_pil, lang='jpn')
        print("✓ Japanese language data is available for Tesseract")
        return True
    except Exception as e:
        print(f"✗ Japanese language data not found: {e}")
        
        # Check if we have local jpn.traineddata file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_jpn_file = os.path.join(current_dir, "jpn.traineddata")
        
        if os.path.exists(local_jpn_file):
            print(f"Note: jpn.traineddata found locally but needs to be installed.")
            print("Please run install_japanese_ocr.bat as administrator to install it.")
        
        return False

def advanced_preprocessing(frame):
    
    # Convert to different color spaces for better text extraction
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Method 1: Enhanced contrast with CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Method 2: Multiple threshold techniques
    # OTSU threshold
    _, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Adaptive threshold (good for varying lighting)
    thresh_adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
    
    # Custom threshold based on image statistics
    mean_val = np.mean(gray)
    thresh_custom = int(max(mean_val * 0.7, 100))
    _, thresh_custom_bin = cv2.threshold(gray, thresh_custom, 255, cv2.THRESH_BINARY)
    
    # Method 3: Morphological operations to clean text
    # Remove noise while preserving text structure
    kernel_noise = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1,1))
    denoised = cv2.morphologyEx(thresh_otsu, cv2.MORPH_OPEN, kernel_noise)
    
    # Close gaps in characters
    kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (2,1))
    closed = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel_close)
    
    # Method 4: Edge-based preprocessing for outlined text
    edges = cv2.Canny(gray, 50, 150)
    # Dilate edges to connect text parts
    kernel_edge = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    edge_dilated = cv2.dilate(edges, kernel_edge, iterations=1)
    
    # Method 5: Color-based extraction (for colored text)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Extract white/light colored text
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Extract black/dark colored text
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 80])
    black_mask = cv2.inRange(hsv, lower_black, upper_black)
    
    return {
        'original_gray': gray,
        'enhanced_contrast': enhanced,
        'thresh_otsu': thresh_otsu,
        'thresh_adaptive': thresh_adaptive,
        'thresh_custom': thresh_custom_bin,
        'morphology_cleaned': closed,
        'edge_enhanced': edge_dilated,
        'white_text': white_mask,
        'black_text': black_mask
    }

def get_optimized_ocr_configs(has_japanese=False):
    
    configs = []
    
    if has_japanese:
        # Japanese-optimized configurations
        configs.extend([
            '--oem 3 --psm 6 -l jpn',           # Japanese uniform text block
            '--oem 3 --psm 8 -l jpn',           # Japanese single word
            '--oem 3 --psm 7 -l jpn',           # Japanese single text line
            '--oem 3 --psm 11 -l jpn',          # Japanese sparse text
            '--oem 3 --psm 13 -l jpn',          # Japanese raw line
            '--oem 3 --psm 6 -l jpn+eng',       # Japanese + English
            '--oem 1 --psm 6 -l jpn',           # Different engine, Japanese
            '--oem 3 --psm 6 -l jpn -c tessedit_char_whitelist=あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンー１２３４５６７８９０',
        ])
    
    # English/General configurations (fallback)
    configs.extend([
        '--oem 3 --psm 6',                     # Uniform text block
        '--oem 3 --psm 8',                     # Single word
        '--oem 3 --psm 7',                     # Single text line
        '--oem 3 --psm 11',                    # Sparse text
        '--oem 3 --psm 13',                    # Raw line
        '--oem 1 --psm 6',                     # Different OCR engine
        '--oem 3 --psm 6 -c tessedit_char_blacklist=|[]{}()<>',  # Remove common OCR artifacts
    ])
    
    return configs

def advanced_text_cleaning(text):
    
    if not text or not text.strip():
        return ""
    
    # Step 1: Basic cleanup
    text = text.strip()
    
    # Step 2: Remove obvious OCR artifacts
    # Remove isolated single characters that are likely noise
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Remove lines that are just punctuation or symbols
        if re.match(r'^[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+$', line):
            continue
            
        # Remove lines with excessive special characters
        special_char_ratio = len(re.findall(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', line)) / max(len(line), 1)
        if special_char_ratio > 0.7:
            continue
            
        # Count Japanese characters
        japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', line))
        english_chars = len(re.findall(r'[a-zA-Z]', line))
        numbers = len(re.findall(r'[0-9]', line))
        
        # Keep lines with substantial content
        if (japanese_chars > 0 or english_chars > 1 or 
            (len(line) > 2 and (english_chars + numbers + japanese_chars) > len(line) * 0.5)):
            cleaned_lines.append(line)
    
    # Step 3: Join and final cleanup
    result = '\n'.join(cleaned_lines)
    
    # Remove excessive whitespace
    result = re.sub(r'\n\s*\n', '\n', result)
    result = re.sub(r' +', ' ', result)
    
    return result.strip()

def extract_text_with_confidence(image, configs, timeout=15):
    
    best_result = {"text": "", "confidence": 0, "config": ""}
    
    for config in configs:
        try:
            text = pytesseract.image_to_string(image, config=config, timeout=timeout)
            
            if not text or not text.strip():
                continue
            confidence = calculate_text_confidence(text)
            
            if confidence > best_result["confidence"]:
                best_result = {
                    "text": text.strip(),
                    "confidence": confidence,
                    "config": config
                }
        except Exception as e:
            print(f"OCR config error: {e}")
            continue
    return best_result

def calculate_text_confidence(text):
    
    if not text or not text.strip():
        return 0
    
    score = 0
    text = text.strip()
    
    # Length bonus (longer text usually more reliable)
    score += min(len(text), 50) * 0.1
    
    # Japanese character bonus
    japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
    score += japanese_chars * 2
    
    # English word bonus
    english_words = len(re.findall(r'\b[a-zA-Z]{2,}\b', text))
    score += english_words * 1.5
    
    # Penalty for excessive special characters
    special_chars = len(re.findall(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
    score -= special_chars * 0.5
    
    # Penalty for isolated single characters
    isolated_chars = len(re.findall(r'\b\w\b', text))
    score -= isolated_chars * 0.3
    return max(score, 0)

# Configure Tesseract
if not configure_tesseract():
    print("Please install Tesseract OCR and restart the script.")
    input("Press Enter to exit...")
    sys.exit(1)

# Check Japanese language support
has_japanese = check_japanese_language_data()

root = tk.Tk()
root.withdraw()
print("Please select a folder containing MP4 videos...")
selected_folder = fold_path

if not selected_folder:
    print("No folder selected. Exiting...")
    sys.exit(0)

# Find MP4 files
print(f"Selected folder: {selected_folder}")
current_dir = os.path.dirname(os.path.abspath(__file__))
mp4_files = [f for f in os.listdir(selected_folder) if f.lower().endswith((".mp4", ".avi", ".mov"))]

if not mp4_files:
    print("No video files found in the selected folder.")
    sys.exit(0)

print(f"Found {len(mp4_files)} video file(s): {mp4_files}")

for filename in mp4_files:
    video_path = os.path.join(selected_folder, filename)
    print(f"Processing video: {video_path}")

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
        print(f"Japanese OCR: {'Enabled' if has_japanese else 'Disabled (using basic OCR)'}")
        frame_count = 0
        extracted_count = 0
        
        # Calculate frame interval (extract every N frames based on FPS)
        # Limit processing to avoid extremely long runs
        frame_interval = max(1, int(fps)) if fps > 0 else 30  # Default to 30 if FPS detection fails
        max_frames_to_process = min(total_frames, 300)  # Limit to 300 frames max (10 minutes at 30fps)
        
        print(f"Processing every {frame_interval} frames, max {max_frames_to_process} frames total")

        output_file = os.path.join(f"{current_dir}//results", 
                                   f"{os.path.splitext(filename)[0]}_enhanced_output.txt")
        raw_output_file = os.path.join(f"{current_dir}//results", 
                                       f"{os.path.splitext(filename)[0]}_enhanced_raw.txt")
        debug_output_file = os.path.join(f"{current_dir}//results", 
                                        f"{os.path.splitext(filename)[0]}_debug_info.txt")
        
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))

        # Get optimized OCR configurations
        ocr_configs = get_optimized_ocr_configs(has_japanese)

        with open(output_file, "w", encoding="utf-8") as f, \
             open(raw_output_file, "w", encoding="utf-8") as f_raw, \
             open(debug_output_file, "w", encoding="utf-8") as f_debug:
            
            f.write(f"Video: {filename} (Enhanced Processing)\n")
            f.write(f"FPS: {fps:.2f}, Duration: {duration:.2f}s\n")
            f.write(f"Japanese OCR: {'Enabled' if has_japanese else 'Disabled'}\n")
            f.write("="*50 + "\n\n")
            
            f_raw.write(f"Video: {filename} (Enhanced Raw OCR Output)\n")
            f_raw.write(f"FPS: {fps:.2f}, Duration: {duration:.2f}s\n")
            f_raw.write("="*50 + "\n\n")
            
            f_debug.write(f"Debug Info for: {filename}\n")
            f_debug.write(f"OCR Configurations: {len(ocr_configs)}\n")
            f_debug.write("="*50 + "\n\n")
            
            while cap.isOpened() and frame_count < max_frames_to_process:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Enhanced text extraction with safety checks
                if frame_count % frame_interval == 0:  # Extract text every second
                    try:
                        print(f"Processing frame {frame_count}...")
                        
                        # Step 1: Advanced preprocessing with error handling
                        try:
                            processed_images = advanced_preprocessing(frame)
                        except Exception as prep_error:
                            print(f"Preprocessing error at frame {frame_count}: {prep_error}")
                            f_debug.write(f"Frame {frame_count}: Preprocessing failed: {prep_error}\n")
                            frame_count += 1
                            continue
                        
                        # Step 2: Try OCR on different preprocessed versions
                        best_overall_result = {"text": "", "confidence": 0, "method": "", "config": ""}
                        
                        # Convert to list to avoid dictionary iteration issues
                        preprocessing_methods = list(processed_images.items())
                        
                        for method_name, processed_image in preprocessing_methods:
                            try:
                                result = extract_text_with_confidence(processed_image, ocr_configs)
                                
                                if result["confidence"] > best_overall_result["confidence"]:
                                    best_overall_result = {
                                        "text": result["text"],
                                        "confidence": result["confidence"],
                                        "method": method_name,
                                        "config": result["config"]
                                    }
                            except Exception as method_error:
                                f_debug.write(f"Frame {frame_count}: Method {method_name} failed: {method_error}\n")
                                continue
                        
                        # Step 3: Post-process the best result
                        if best_overall_result["text"]:
                            cleaned_text = advanced_text_cleaning(best_overall_result["text"])
                            
                            timestamp = frame_count / fps if fps > 0 else frame_count / 30
                            
                            print(f"Frame {frame_count}: Method={best_overall_result['method']}, "
                                  f"Confidence={best_overall_result['confidence']:.1f}")
                            
                            if cleaned_text or best_overall_result["text"]:
                                # Write to enhanced output file
                                final_text = cleaned_text if cleaned_text else best_overall_result["text"]
                                f.write(f"[Frame {frame_count} - Time: {timestamp:.2f}s]\n")
                                f.write(f"Method: {best_overall_result['method']}\n")
                                f.write(f"Confidence: {best_overall_result['confidence']:.1f}\n")
                                f.write(f"{final_text}\n")
                                f.write("-" * 40 + "\n\n")
                                
                                # Write to raw output file
                                f_raw.write(f"[Frame {frame_count} - Time: {timestamp:.2f}s]\n")
                                f_raw.write(f"{best_overall_result['text']}\n")
                                f_raw.write("-" * 30 + "\n\n")
                                
                                # Write debug info
                                f_debug.write(f"Frame {frame_count}: {best_overall_result['method']} "
                                             f"(conf: {best_overall_result['confidence']:.1f}) "
                                             f"Config: {best_overall_result['config']}\n")
                                extracted_count += 1
                        
                    except Exception as ocr_error:
                        print(f"OCR error at frame {frame_count}: {ocr_error}")
                        f_debug.write(f"Frame {frame_count}: ERROR - {ocr_error}\n")
                        
                frame_count += 1
                
                # Progress indicator
                if frame_count % (frame_interval * 10) == 0:
                    progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
                    print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")

        cap.release()
        print(f"Completed: {filename}")
        print(f"Extracted text from {extracted_count} frames")
        print(f"Enhanced output saved to: {output_file}")
        print(f"Raw output saved to: {raw_output_file}")
        print(f"Debug info saved to: {debug_output_file}")
        print("-" * 50)
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        continue

print("All videos processed with enhanced Japanese OCR!")
print("\nManual Installation Note:")
print("If Japanese characters are still not recognized properly, please:")
print("1. Copy 'jpn.traineddata' from this folder to: C:\\Program Files\\Tesseract-OCR\\tessdata\\")
print("2. You may need administrator privileges to copy the file")
print("3. Restart the script after copying")

root.destroy()
