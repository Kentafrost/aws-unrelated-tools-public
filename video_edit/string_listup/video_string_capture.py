import os
import tkinter as tk
from tkinter import filedialog
import subprocess, sys

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
    """Configure Tesseract OCR path"""
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
    
    print("Warning: Tesseract not found. Please install Tesseract OCR.")
    print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    return False

# Configure Tesseract
if not configure_tesseract():
    print("Please install Tesseract OCR and restart the script.")
    input("Press Enter to exit...")
    sys.exit(1)

def check_japanese_language_data():
    try:
        # Test Japanese OCR capability
        import PIL.Image
        import numpy as np
        
        # Create a test image with Japanese text
        test_image = np.ones((100, 200, 3), dtype=np.uint8) * 255
        test_pil = PIL.Image.fromarray(test_image)
        
        # Try to use Japanese language
        pytesseract.image_to_string(test_pil, lang='jpn')
        print("Japanese language data is available for Tesseract")
        return True
    except Exception as e:
        print(f"Japanese language data not found: {e}")
        print("Please download Japanese language data from:")
        print("https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata")
        print("And place it in: C:\\Program Files\\Tesseract-OCR\\tessdata\\")
        return False

# Check Japanese language support
check_japanese_language_data()

def clean_japanese_text(text):
    """Clean and validate Japanese text"""
    if not text or not text.strip():
        return ""
    
    # Remove obvious OCR artifacts but be less restrictive
    cleaned = text.strip()
    
    # Remove lines that are mostly symbols or single characters
    lines = cleaned.split('\n')
    valid_lines = []
    
    for line in lines:
        line = line.strip()
        if len(line) < 1:  # Skip empty lines
            continue
            
        # Count Japanese characters
        japanese_chars = sum(1 for char in line 
                           if '\u3040' <= char <= '\u309F' or  # Hiragana
                              '\u30A0' <= char <= '\u30FF' or  # Katakana
                              '\u4E00' <= char <= '\u9FAF')    # Kanji
        
        # Be more lenient - keep any text that might be useful
        # Keep lines with Japanese characters, reasonable English text, or numbers
        if (japanese_chars > 0 or 
            (len(line) > 1 and any(c.isalnum() for c in line)) or
            len(line.replace(' ', '').replace('\t', '')) > 0):
        
            valid_lines.append(line)
    
    result = '\n'.join(valid_lines) if valid_lines else ""
    return result

# ルートウィンドウを非表示にする
root = tk.Tk()
root.withdraw()

# フォルダ選択ダイアログを表示
print("Please select a folder containing MP4 videos...")
selected_folder = filedialog.askdirectory(title="フォルダを選択してください")

if not selected_folder:
    print("No folder selected. Exiting...")
    sys.exit(0)

print(f"Selected folder: {selected_folder}")
current_dir = os.path.dirname(os.path.abspath(__file__))

# Find MP4 files
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
        
        frame_count = 0
        extracted_count = 0
        
        # Calculate frame interval (extract every N frames based on FPS)
        frame_interval = max(1, int(fps)) if fps > 0 else 30  # Default to 30 if FPS detection fails

        output_file = os.path.join(f"{current_dir}//results", 
                                   f"{os.path.splitext(filename)[0]}_output_text.txt")
        raw_output_file = os.path.join(f"{current_dir}//results", 
                                       f"{os.path.splitext(filename)[0]}_raw_output.txt")
        
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))

        with open(output_file, "w", encoding="utf-8") as f, \
             open(raw_output_file, "w", encoding="utf-8") as f_raw:
            f.write(f"Video: {filename}\n")
            f.write(f"FPS: {fps:.2f}, Duration: {duration:.2f}s\n")
            f.write("="*50 + "\n\n")
            
            f_raw.write(f"Video: {filename} (Raw OCR Output)\n")
            f_raw.write(f"FPS: {fps:.2f}, Duration: {duration:.2f}s\n")
            f_raw.write("="*50 + "\n\n")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # converting to Japanese text
                if frame_count % frame_interval == 0:  # Extract text every second
                    try:
                        # Enhanced image preprocessing for Japanese OCR
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        
                        # Multiple preprocessing techniques
                        # 1. Gaussian blur to reduce noise
                        blurred = cv2.GaussianBlur(gray, (1, 1), 0)
                        
                        # 2. OTSU threshold
                        _, thresh1 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                        
                        # 3. Adaptive threshold for varying lighting
                        thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                        
                        # 4. Morphological operations to clean up text
                        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
                        cleaned = cv2.morphologyEx(thresh1, cv2.MORPH_CLOSE, kernel)
                        
                        # Try multiple OCR configurations - use basic configs since Japanese data not installed
                        configs = [
                            r'--oem 3 --psm 6',                  # Basic - uniform text block
                            r'--oem 3 --psm 8',                  # Basic - single word
                            r'--oem 3 --psm 11',                 # Basic - sparse text
                            r'--oem 3 --psm 7',                  # Basic - single text line
                            r'--oem 1 --psm 6',                  # Different OCR engine
                        ]
                        
                        images_to_try = [frame_rgb, thresh1, thresh2, cleaned]
                        
                        best_text = ""
                        
                        # Try each configuration until we get some text
                        for config in configs:
                            for processed_frame in images_to_try:
                                try:
                                    text_candidate = pytesseract.image_to_string(processed_frame, config=config, timeout=10)
                                    
                                    # Accept any non-empty text
                                    if text_candidate and text_candidate.strip():
                                        best_text = text_candidate.strip()
                                        break
                                        
                                except Exception:
                                    continue
                            if best_text:
                                break
                        
                        # Process any text we found
                        if best_text:
                            cleaned_text = clean_japanese_text(best_text)
                            
                            print(f"Frame {frame_count}: Raw OCR: '{best_text[:50]}{'...' if len(best_text) > 50 else ''}'")
                            if cleaned_text:
                                print(f"Frame {frame_count}: Cleaned: '{cleaned_text[:50]}{'...' if len(cleaned_text) > 50 else ''}'")
                            
                            # Write to files if we have any text
                            timestamp = frame_count / fps if fps > 0 else frame_count / 30
                            
                            # Write to cleaned output file (use cleaned text if available, otherwise raw)
                            final_text = cleaned_text if cleaned_text else best_text
                            f.write(f"[Frame {frame_count} - Time: {timestamp:.2f}s]\n")
                            f.write(f"{final_text}\n")
                            f.write("-" * 30 + "\n\n")
                            
                            # Write to raw output file
                            f_raw.write(f"[Frame {frame_count} - Time: {timestamp:.2f}s]\n")
                            f_raw.write(f"{best_text}\n")
                            f_raw.write("-" * 30 + "\n\n")
                            
                            extracted_count += 1
                        
                    except Exception as ocr_error:
                        print(f"OCR error at frame {frame_count}: {ocr_error}")
                        
                frame_count += 1
                
                # Progress indicator
                if frame_count % (frame_interval * 10) == 0:
                    progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
                    print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")

        cap.release()
        print(f"Completed: {filename}")
        print(f"Extracted text from {extracted_count} frames")
        print(f"Cleaned output saved to: {output_file}")
        print(f"Raw output saved to: {raw_output_file}")
        print("-" * 50)
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        continue

print("All videos processed!")
root.destroy()