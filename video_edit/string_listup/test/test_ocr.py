import cv2
import pytesseract
import numpy as np
import os
from pathlib import Path
from tkinter import filedialog
import tkinter as tk

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def test_ocr_on_video():
    """Test OCR on a small sample of video frames"""
    
    # Create UI for folder selection
    root = tk.Tk()
    root.withdraw()
    
    print("Please select a folder containing MP4 videos...")
    folder_path = filedialog.askdirectory()
    
    if not folder_path:
        print("No folder selected. Exiting.")
        return
    
    # Find video files
    video_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')]
    
    if not video_files:
        print("No MP4 files found in selected folder.")
        return
    
    # Test on first video only
    video_path = os.path.join(folder_path, video_files[0])
    print(f"Testing OCR on: {video_files[0]}")
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error opening video: {video_path}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Test on 5 frames spread throughout the video
    test_frames = [int(total_frames * i / 5) for i in range(1, 6)]
    
    for frame_idx in test_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if not ret:
            continue
            
        print(f"\n--- Testing frame {frame_idx} ---")
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Simple threshold
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        
        # Test different OCR configurations
        configs = [
            '--oem 3 --psm 6',
            '--oem 3 --psm 8',
            '--oem 3 --psm 11'
        ]
        
        for i, config in enumerate(configs):
            try:
                # Use timeout to prevent hanging
                text = pytesseract.image_to_string(binary, config=config, timeout=5)
                text = text.strip()
                
                if text:
                    print(f"Config {i+1}: '{text[:50]}{'...' if len(text) > 50 else ''}'")
                else:
                    print(f"Config {i+1}: No text detected")
                    
            except Exception as e:
                print(f"Config {i+1}: Error - {e}")
    
    cap.release()
    print("\nOCR test completed!")

if __name__ == "__main__":
    test_ocr_on_video()
