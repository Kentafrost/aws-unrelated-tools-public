# -*- coding: utf-8 -*-
import json
import os, time
import cv2
from moviepy import VideoFileClip

current_directory = os.path.dirname(os.path.abspath(__file__))
folder_json = os.path.join(current_directory, "json", 'folder_path.json')


# preview the video file
def preview_video(video_path):

    try:
        # Play the preview video
        cap = cv2.VideoCapture(video_path)
        
        print("Playing preview... Press 'q' to stop")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            cv2.imshow("Cropped Preview", frame)
            if cv2.waitKey(25) & 0xFF == ord('q') or cv2.waitKey(25) & 0xFF == ord('c'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return True
        
    except Exception as e:
        print(f"Preview creation error: {e}")
        return False

def rename_file(file_path, file_name):
    
    if change_file_name_check.lower() == 'y':
        if file_path.endswith('.mp4'):
            # preview the video
            print(f"\nPreviewing video: {file_name}")
            preview_video(file_path)
            
            change_file_name = input("Do you want to change the file name? (y/n): ")
            if change_file_name.lower() == 'y':
                print("")
                print(f"Current file name: {file_name}")
                new_file_name = input("Enter the new file name:")
                
                new_file_path = os.path.join(os.path.dirname(file_path), new_file_name + ".mp4")
                os.rename(file_path, new_file_path)
                file_path = new_file_path
                file_name = new_file_name
                print("")
                print(f"File renamed to: {file_name}")

# open json file to get folder names
try:
    with open(folder_json, 'r', encoding='utf-8') as json_file:
        folder_names = json.load(json_file)
except json.JSONDecodeError:
    folder_names = []
except FileNotFoundError:
    print(f"Error: The file {folder_json} was not found.")
    print("Please create the file and add folder names in JSON format, e.g., [\"folder1\", \"folder2\"]")
    os._exit(1)

change_file_name_check = input(f"\nDo you want to change each file name? (y/n): ")
all_files = []

# list up all folders in the json file including parent key, value in json files
folder1 = folder_names["D-Drive"]["Entertainment-folders"]
folder2 = folder_names["Google-Drive"]["folders"]

# print(key and value in folder1)
for key, value in folder1.items():

    folder_path = os.path.join(current_directory, str(value))
    print("")
    print(folder_path)
    time.sleep(1.0)
    
    # list up all folders in folder_path
    if os.path.isdir(folder_path):
        for root, dirs, files in os.walk(folder_path):
            print(f"Processing folder: {root}")
            
            for file in files:
                all_files.append(os.path.join(root, file))
                         
print(f"Total files found: {len(all_files)}")

# put files path, and name, tag(separated files name with "-") into json file
files_data = []
extentions = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"]


for file_path in all_files:
    file_name = os.path.basename(file_path)

    if change_file_name_check.lower() == 'y':
        rename_file(file_path, file_name)

    if not "-" in file_name:
        print("")
        print(f"No '-' in file name: '{file_name}'")
        print("Skipping this file.")
        continue
    
    """ files data size """
    file_data_size = os.path.getsize(file_path) / 1024 / 1024  # in MB
    
    """ file length check """
    if file_path.endswith(".mp4"):
        file_data_length = VideoFileClip(file_path).duration  # in seconds
        if file_data_length > 60:
            file_data_length_min = file_data_length / 60
            
            if not file_data_length_min.is_integer():
                file_data_length_min = f"{int(file_data_length_min)} minutes {int(file_data_length % 60)} seconds"
            else:
                file_data_length_min = f"{int(file_data_length_min)} minutes"
        else:
            file_data_length_min = 0
            
        if file_data_length > 3600:
            file_data_length_hour = file_data_length / 3600
            
            if not file_data_length_hour.is_integer():
                file_data_length_hour = f"{int(file_data_length_hour)} hours {int((file_data_length % 3600) / 60)} minutes"
            else:
                file_data_length_hour = f"{int(file_data_length_hour)} hours"
        else:
            file_data_length_hour = 0
        file_data_length = file_data_length_hour + file_data_length_min + file_data_length
    else:
        file_data_length = "-"

    tag_list = []
    file_name = file_name.replace(" - Made with Clipchamp.mp4", "")
    
    # delete extensions string from file name
    for ext in extentions:
        file_name = file_name.replace(ext, "")    
    
    tags = file_name.split("-")

    for tag in tags:
        tag_list.append(tag)
    
    files_data.append({
        "path": file_path,
        "name": file_name,
        "size_MB": f"{file_data_size:.2f} MB",
        "video_length": file_data_length,
        "tags": tag_list
    })
    
json_output = os.path.join(current_directory, 'json', 'files_data.json')

with open(json_output, 'w', encoding='utf-8') as json_file:
    json.dump(files_data, json_file, indent=4, ensure_ascii=False)

print(f"File data has been written to {json_output}")
