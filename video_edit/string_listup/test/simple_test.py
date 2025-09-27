import cv2
import pytesseract
import os
import sys
from pathlib import Path
import re

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def clean_japanese_text(text):
    """Clean and validate text with focus on Japanese content"""
    if not text or not text.strip():
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove obvious OCR artifacts (isolated single characters, excessive punctuation)
    text = re.sub(r'\b[a-zA-Z]\b', '', text)  # Remove isolated single letters
    text = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', ' ', text)  # Keep only alphanumeric, Japanese chars, and spaces
    text = re.sub(r'\s+', ' ', text.strip())  # Clean up spaces again
    
    # Must have at least 2 characters to be considered valid
    if len(text) < 2:
        return ""
        
    return text

# Simple test - hardcode a video path for testing
video_path = r"G:/My Drive/Entertainment/Anime/original/サキュバス/[Live2D]ミシェルおっぱい押し付け.mp4"

if not os.path.exists(video_path):
    print(f"Video file not found: {video_path}")
    sys.exit(1)

# Create results directory
results_dir = "results"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

output_file = os.path.join(results_dir, "test_output.txt")
raw_output_file = os.path.join(results_dir, "test_raw_output.txt")

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error opening video")
    sys.exit(1)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"Video opened successfully - {total_frames} frames, {fps} FPS")

# Open output files
with open(output_file, "w", encoding="utf-8") as f, \
     open(raw_output_file, "w", encoding="utf-8") as f_raw:
    
    f.write("Test OCR Output\n")
    f.write("="*30 + "\n\n")
    f_raw.write("Test Raw OCR Output\n")
    f_raw.write("="*30 + "\n\n")
    
    extracted_count = 0
    
    # Test on several frames
    for frame_idx in [1000, 2000, 3000]:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if not ret:
            continue
            
        print(f"\nProcessing frame {frame_idx}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        
        # Try OCR
        try:
            raw_text = pytesseract.image_to_string(binary, config='--oem 3 --psm 6', timeout=10)
            
            print(f"Raw OCR: '{raw_text.strip()[:100]}'")
            
            if raw_text.strip():
                cleaned_text = clean_japanese_text(raw_text)
                print(f"Cleaned: '{cleaned_text[:100]}'")
                
                # Write to files regardless of cleaning results
                timestamp = frame_idx / fps
                
                f.write(f"[Frame {frame_idx} - Time: {timestamp:.2f}s]\n")
                if cleaned_text:
                    f.write(f"Cleaned: {cleaned_text}\n")
                else:
                    f.write(f"Raw: {raw_text.strip()}\n")
                f.write("-" * 30 + "\n\n")
                
                f_raw.write(f"[Frame {frame_idx} - Time: {timestamp:.2f}s]\n")
                f_raw.write(f"{raw_text.strip()}\n")
                f_raw.write("-" * 30 + "\n\n")
                
                extracted_count += 1
                
        except Exception as e:
            print(f"OCR error: {e}")

cap.release()

print(f"\nTest completed!")
print(f"Extracted text from {extracted_count} frames")
print(f"Output files created:")
print(f"  - {output_file}")
print(f"  - {raw_output_file}")

# Show file sizes
if os.path.exists(output_file):
    size = os.path.getsize(output_file)
    print(f"  Clean output file size: {size} bytes")

if os.path.exists(raw_output_file):
    size = os.path.getsize(raw_output_file)
    print(f"  Raw output file size: {size} bytes")
