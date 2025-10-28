import os
import cv2
import pytesseract
import numpy as np
import tkinter as tk
from tkinter import filedialog
import re

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def improved_japanese_text_cleaning(text):
    """Improved text cleaning specifically for Japanese content"""
    if not text or not text.strip():
        return ""
    
    # Remove obvious artifacts but preserve potential Japanese text
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if len(line) < 1:
            continue
            
        # Count different character types
        japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', line))
        latin_chars = len(re.findall(r'[a-zA-Z]', line))
        numbers = len(re.findall(r'[0-9]', line))
        
        # More lenient filtering - keep lines that might contain text
        if (japanese_chars > 0 or  # Has Japanese characters
            latin_chars >= 2 or    # Has multiple Latin characters
            (len(line) >= 3 and any(c.isalnum() for c in line))):  # Reasonable length with alphanumeric
            
            # Clean up common OCR artifacts
            cleaned_line = re.sub(r'[|\\/_\-=+<>(){}\[\]]+', ' ', line)  # Remove excessive symbols
            cleaned_line = re.sub(r'\s+', ' ', cleaned_line).strip()
            
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
    
    return '\n'.join(cleaned_lines) if cleaned_lines else ""

def extract_text_from_anime_frame(frame):
    """Optimized text extraction for anime content"""
    results = []
    
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Multiple preprocessing approaches
    preprocessing_methods = {
        'adaptive_thresh': cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
        'otsu_thresh': cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        'high_contrast': cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1],
        'low_contrast': cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]
    }
    
    # OCR configurations (prioritize working ones)
    configs = [
        '--oem 3 --psm 6',    # Uniform text block - this was working well
        '--oem 3 --psm 8',    # Single word
        '--oem 3 --psm 7',    # Single text line
        '--oem 3 --psm 11',   # Sparse text
    ]
    
    best_result = {"text": "", "confidence": 0, "method": ""}
    
    for method_name, processed_image in preprocessing_methods.items():
        for config in configs:
            try:
                # Extract text with timeout
                raw_text = pytesseract.image_to_string(processed_image, config=config, timeout=5)
                
                if raw_text and raw_text.strip():
                    # Calculate confidence based on text quality
                    confidence = calculate_text_quality(raw_text)
                    
                    if confidence > best_result["confidence"]:
                        best_result = {
                            "text": raw_text.strip(),
                            "confidence": confidence,
                            "method": f"{method_name}+{config}"
                        }
                        
            except Exception:
                continue
    
    return best_result

def calculate_text_quality(text):
    """Calculate text quality score"""
    if not text:
        return 0
    
    score = 0
    text = text.strip()
    
    # Length bonus
    score += min(len(text), 50) * 0.5
    
    # Japanese character bonus
    japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
    score += japanese_chars * 5  # High bonus for Japanese
    
    # Latin word bonus
    latin_words = len(re.findall(r'[a-zA-Z]{2,}', text))
    score += latin_words * 3
    
    # Penalty for excessive symbols
    symbols = len(re.findall(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
    score -= symbols * 0.3
    
    return max(score, 0)

def main():
    print("🎌 Anime Japanese Text Extractor 🎌")
    print("=" * 50)
    
    # Folder selection
    root = tk.Tk()
    root.withdraw()
    
    print("Please select a folder containing video files...")
    folder_path = filedialog.askdirectory()
    
    if not folder_path:
        print("No folder selected. Exiting.")
        return
    
    # Find video files
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    video_files = [f for f in os.listdir(folder_path) 
                   if any(f.lower().endswith(ext) for ext in video_extensions)]
    
    if not video_files:
        print("No video files found!")
        return
    
    print(f"Found {len(video_files)} video file(s)")
    
    # Create results directory
    results_dir = "anime_text_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    for video_file in video_files:
        print(f"\n📹 Processing: {video_file}")
        video_path = os.path.join(folder_path, video_file)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ Could not open {video_file}")
            continue
        
        # Get video info
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        print(f"📊 Video info: {fps:.1f} FPS, {duration:.1f}s duration")
        
        # Output file
        safe_filename = re.sub(r'[^\w\-_.]', '_', os.path.splitext(video_file)[0])
        output_file = os.path.join(results_dir, f"{safe_filename}_japanese_text.txt")
        
        # Process frames (every 2 seconds to avoid overwhelming)
        frame_interval = int(fps * 2)  # Every 2 seconds
        extracted_count = 0
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"🎌 Japanese Text Extraction Results\n")
            f.write(f"Video: {video_file}\n")
            f.write(f"Duration: {duration:.1f}s\n")
            f.write("=" * 60 + "\n\n")
            
            frame_count = 0
            while cap.isOpened() and frame_count < min(total_frames, 900):  # Limit to 30 seconds worth
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    try:
                        result = extract_text_from_anime_frame(frame)
                        
                        if result["text"] and result["confidence"] > 10:  # Minimum confidence threshold
                            timestamp = frame_count / fps
                            cleaned_text = improved_japanese_text_cleaning(result["text"])
                            
                            print(f"⏰ Frame {frame_count} ({timestamp:.1f}s): Confidence {result['confidence']:.1f}")
                            
                            # Write result
                            f.write(f"⏰ Time: {timestamp:.1f}s (Frame {frame_count})\n")
                            f.write(f"🔧 Method: {result['method']}\n")
                            f.write(f"📊 Confidence: {result['confidence']:.1f}\n")
                            
                            if cleaned_text:
                                f.write(f"🎌 Cleaned Text:\n{cleaned_text}\n")
                            
                            f.write(f"📝 Raw OCR:\n{result['text']}\n")
                            f.write("-" * 40 + "\n\n")
                            
                            extracted_count += 1
                            
                    except Exception as e:
                        print(f"❌ Error at frame {frame_count}: {e}")
                
                frame_count += 1
                
                # Progress update
                if frame_count % (frame_interval * 5) == 0:
                    progress = (frame_count / min(total_frames, 900)) * 100
                    print(f"📈 Progress: {progress:.1f}%")
        
        cap.release()
        print(f"✅ Completed! Extracted text from {extracted_count} frames")
        print(f"📄 Results saved to: {output_file}")
    
    print(f"\n🎉 All videos processed! Results in '{results_dir}' folder")

if __name__ == "__main__":
    main()
