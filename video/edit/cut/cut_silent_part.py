# Cut silent parts from video
from moviepy import *
import os
import shutil
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import string_listup.dir_path as dir_path


def remove_silence(target_dir, video_path, threshold=-30, min_silence_duration=0.5):
    # Prepare output path using os.path.join for cross-platform compatibility
    output_dir = os.path.join(target_dir, "silence/after")
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, os.path.basename(video_path))
    # Create a backup copy before processing
    
    copy_path = f"{output_dir}//backup//{os.path.basename(video_path)}"
    os.makedirs(copy_path, exist_ok=True)
    
    shutil.copy2(video_path, copy_path)
    
    path = os.path.join(output_dir, os.path.basename(video_path))

    clip = VideoFileClip(video_path)
    audio = clip.audio
    chunks = []
    t = 0
    while t < clip.duration:
        segment = audio.subclipped(t, min(t + min_silence_duration, clip.duration))
        # Use segment's dBFS for efficient silence detection
        try:
            dBFS = segment.to_soundarray(fps=22050).max()
        except Exception:
            dBFS = 0
        if dBFS > 10**(threshold / 20):
            chunks.append(clip.subclipped(t, min(t + min_silence_duration, clip.duration)))
        t += min_silence_duration
    if chunks:
        final = concatenate_videoclips(chunks)
        # Only write the output if the concatenated duration is different from the original
        if abs(final.duration - clip.duration) > 1e-3:
            final.write_videofile(path)
        else:
            print(f"No silence detected in {video_path}, skipping output.")
    else:
        print(f"No non-silent segments found in {video_path}")
        return


if __name__ == "__main__":
    target_dir = dir_path.d_drive_path()

    all_files = []

    for root, dirs, files in os.walk(target_dir):
        for filename in files:
            if filename.endswith(".mp4"):
                all_files.append(os.path.join(root, filename))

    for video in all_files:
        remove_silence(target_dir, video)
