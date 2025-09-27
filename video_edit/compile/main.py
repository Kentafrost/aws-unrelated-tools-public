import os
import logging
import json
from tkinter import Tk, filedialog

def compile_video(video_list, output_path):
    from moviepy.video.io.VideoFileClip import concatenate_videoclips, VideoFileClip
    clips = []
    for video_path in video_list:
        if os.path.exists(video_path):
            clip = VideoFileClip(video_path)
            clips.append(clip)
        else:
            logging.warning(f"Video file {video_path} does not exist and will be skipped.")
    
    if clips:
        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        for clip in clips:
            clip.close()
        final_clip.close()
        
        logging.info(f"Compiled video saved to {output_path}")
        logging.info(f"Compiled {len(clips)} video clips into {output_path}")
        logging.info(f"Compiled video duration: {final_clip.duration} seconds and size: "
                     f"{os.path.getsize(output_path)/(1024*1024):.2f} MB")
    else:
        logging.error("No valid video clips to compile.")

# Define paths from JSON configuration
def define_path():
    output_folder = ""
    json_path = os.path.join(os.path.dirname(__file__), 'path.json')
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            paths = json.load(f)
            logging.info(f"Loaded paths from JSON: {paths}")
    else:
        logging.error(f"Path JSON file not found at {json_path}. Exiting.")
        os._exit(1)
    
    output_folder = paths.get("video_path1", "")
    
    if not output_folder:
        logging.error("Output folder path not found in JSON. Exiting.")
        os._exit(1)
    
    return output_folder

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    # choose the video files to compile on GUI
    
    selected_videos = Tk().withdraw() or filedialog.askopenfilenames(
        title="Select video files to compile",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    logging.info(f"Selected videos: {selected_videos}")
    
    if not selected_videos:
        logging.error("No videos selected. Exiting.")
        os._exit(1)
    elif len(selected_videos) < 2:
        logging.error("At least two videos are required to compile. Exiting.")
        os._exit(1)
    elif not ".mp4" in selected_videos[0]:
        logging.error("Selected files must be .mp4 format. Exiting.")
        os._exit(1)

    output_folder = define_path()
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logging.info(f"Created output directory at {output_folder}")
        
    output_file = os.path.join(output_folder, "compiled_video.mp4")
    compile_video(selected_videos, output_file)