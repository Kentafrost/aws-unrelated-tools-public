# merger all mp4 videos in a folder
from moviepy import VideoFileClip, concatenate_videoclips
import os
import logging
import tkinter as tk
from tkinter import Tk, filedialog

def merge_videos(input_folder):
    
    video_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]
    video_files.sort()
    video_clips = []
    
    # select some mp4 files in the folder with button in explorer
    if not video_files:
        print("No mp4 files found in the selected folder.")
        return
    else:
        selected_videos = filedialog.askopenfilenames(
            title="Select MP4 files to merge",
            filetypes=[("MP4 files", "*.mp4")]
        )
    
    # all mp4 files into a list
    for video_file in selected_videos:
        video_path = os.path.join(input_folder, video_file)
        video_clips.append(VideoFileClip(video_path))
    
    if video_clips:
        try:
            final_clip = concatenate_videoclips(video_clips)
            
            output_file = os.path.join(input_folder, "merged_video.mp4")
            final_clip.write_videofile(output_file, codec='libx264')
            print(f"Merged video saved as {output_file}")
            
        except Exception as e:
            logging.error(f"Error merging videos: {e}")
            print(f"Error merging videos: {e}")
    else:
        print("No video files found to merge.")


def merge_same_vid(video_path, number, merged_mp4_name, output_path=None):
    
    logging.info(f"Video path: {video_path}")
    logging.info(f"Number of repetitions: {number}")

    clip = VideoFileClip(video_path)
    clips = [clip] * number  # Repeat the same clip n times
    final_clip = concatenate_videoclips(clips)
    if not output_path:
        output_path = os.path.join(os.path.dirname(video_path), merged_mp4_name)
        
    final_clip.write_videofile(output_path, codec='libx264')
    print(f"Merged video saved as {output_path}")
    
    logging.info(f"Merged video saved as {output_path}")

    
if __name__ == "__main__":
    
    # Get the input folder from the user
    root = Tk()
    root.withdraw()  # Hide the root window
    input_folder = filedialog.askdirectory(title="Select Video Folder")
    
    if input_folder:
        # choose one mp4 file
        video_file = filedialog.askopenfilename(
            title="Select an MP4 file to repeat",
            filetypes=[("MP4 files", "*.mp4")]
        )
        
        merge_mp4_name = input("please write merged files name")
        
        if not merge_mp4_name:
            merge_mp4_name = "merged_video.mp4"
        if not ".mp4" in merge_mp4_name:
            merge_mp4_name = merge_mp4_name + ".mp4"
        
        # merge_videos(input_folder) # merge several different videos
        merge_same_vid(video_file, 30, merge_mp4_name) # merge same videos several times
        
        logging.info("Video merging completed successfully.")
    else:
        print("No folder selected. Exiting.")
        logging.info("No folder selected. Exiting.")
        os._exit(0)