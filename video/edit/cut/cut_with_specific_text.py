# Cut video from the specific text to another specific text
import cv2
import pytesseract
import os
import tkinter as tk
from tkinter import filedialog

# ルートウィンドウを非表示にする
root = tk.Tk()
root.withdraw()

# フォルダ選択ダイアログを表示
selected_folder = filedialog.askdirectory(title="フォルダを選択してください")
print("選択されたフォルダ:", selected_folder)

# 全動画ファイルを処理

for filename in os.listdir(selected_folder):
    if filename.endswith(".mp4"):
        video_path = os.path.join(selected_folder, filename)
        cap = cv2.VideoCapture(video_path)

        start_frame = None
        end_frame = None
        frame_index = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            text = pytesseract.image_to_string(frame)

            if "その後" in text and start_frame is None:
                start_frame = frame_index

            if "その後" in text and start_frame is not None:
                end_frame = frame_index
                break

            frame_index += 1

        cap.release()

        # FFmpegで切り出し（例）
        import subprocess
        fps = 30  # 動画のFPSに合わせる
        start_time = start_frame / fps
        duration = (end_frame - start_frame) / fps

        subprocess.run([
            "ffmpeg", "-i", video_path,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c", "copy", "output.mp4"
        ])

        print(f"Processed {filename}: start_frame={start_frame}, end_frame={end_frame}")
print("All videos processed.")
