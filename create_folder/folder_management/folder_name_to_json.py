# -*- coding: utf-8 -*-
import json
import os, re
import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip
import logging
import time
import secrets_convert_filename

current_directory = os.path.dirname(os.path.abspath(__file__))

base_json_path = os.path.join(current_directory, "GUI", "json")
folder_json = os.path.join(base_json_path, 'folder_path.json')
json_output = os.path.join(base_json_path, 'files_data.json')

# create log directory and set up logging
os.makedirs(f"{current_directory}/log", exist_ok=True)
log_file_path = f"{current_directory}/log/{time.strftime('%Y-%m-%d-%H-%M-%S')}.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO)

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
    
    if file_path.endswith('.mp4'):
        # preview the video before renaming
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
            logging.info(f"File renamed from {file_name} to {new_file_name}")


def get_video_length(file_path):
    if file_path.endswith(".mp4"):
        file_data_length = VideoFileClip(file_path).duration  # in seconds
        if file_data_length > 60:
            file_data_length_min = file_data_length / 60
            
            if not file_data_length_min.is_integer():
                file_data_length_min = f"{int(file_data_length_min)} minutes {int(file_data_length % 60)} seconds"
            else:
                file_data_length_min = f"{int(file_data_length_min)} minutes"
        else:
            file_data_length_min = ""
            
        if file_data_length > 3600:
            file_data_length_hour = file_data_length / 3600
            
            if not file_data_length_hour.is_integer():
                file_data_length_hour = f"{int(file_data_length_hour)} hours {int((file_data_length % 3600) / 60)} minutes"
            else:
                file_data_length_hour = f"{int(file_data_length_hour)} hours"
        else:
            file_data_length_hour = ""
        file_data_length = f"{file_data_length_hour}{file_data_length_min}"
    else:
        file_data_length = "-"
    return file_data_length

# walk through directory and get all files
def walk_directory(folder, all_files):
    
    # str化
    folder = folder[0]
        
    # list up all folders in folder_path
    if os.path.isdir(folder):
        for root, dirs, files in os.walk(folder):
            print(f"Processing folder: {root}")
            
            for file in files:
                all_files.append(os.path.join(root, file))
    return all_files


def main():

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

    print("1: Change each file name before processing")
    print("2: Convert file names to tags using default conversion")
    print("3: Both 1 and 2")
    change_file_name_check = input(f"\nSelect an option (1/2/3) or press Enter to skip: ")

    # list up all folders in the json file including parent key, value in json files
    drives = list(folder_names.keys())
    
    first_drive = drives[0]
    second_drive = drives[1]
    
    folder1 = folder_names[first_drive]
    folder2 = folder_names[second_drive]

    # walk through each folder and get all files
    all_files = walk_directory(folder1, all_files=[])
    all_files = walk_directory(folder2, all_files=all_files)
                            
    print(f"Total files found: {len(all_files)}")

    # put files path, and name, tag(separated files name with "-") into json file
    files_data = []
    extentions = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"]


    for file_path in all_files:
        file_name = os.path.basename(file_path)

        if change_file_name_check.lower() == "1":
            rename_file(file_path, file_name)

        elif change_file_name_check.lower() == "2":
            logging.info(f"Processing file for conversion: {file_name}")
            secrets_converted_name = secrets_convert_filename.convert_to_filename_to_tag(file_name, file_path)
            # if conversion returns a valid name, rename the file
            logging.info(f"Converted file name: {secrets_converted_name}")

            # if secrets_converted_name:
            #     new_file_name = secrets_converted_name
            #     new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
            #     os.rename(file_path, new_file_path)
            #     file_path = new_file_path
            #     file_name = new_file_name
            #     print("")
            #     print(f"File renamed to: {file_name}")
            #     logging.info(f"File renamed from {file_name} to {new_file_name}")

        
        """ files data size """
        file_data_size = os.path.getsize(file_path) / 1024 / 1024  # in MB
        
        """ file length check """
        file_data_length = get_video_length(file_path)

        tag_list = []
        file_name = file_name.replace(" - Made with Clipchamp.mp4", "")
        
        # delete extensions string from file name
        for ext in extentions:
            file_name = file_name.replace(ext, "")    
        
        if not "-" in file_name:
            tag_list = "<No Tag>"
        else:
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

        logging.info(f"Processed file: {file_name}, Size: {file_data_size:.2f} MB, Length: {file_data_length}")
        

    try:
        with open(json_output, 'w', encoding='utf-8') as json_file:
            json.dump(files_data, json_file, indent=4, ensure_ascii=False)
        print(f"File data has been written to {json_output}")
    except FileNotFoundError:
        print(f"Error: The directory for {json_output} does not exist. Please create it and try again.")
        os._exit(1)
    except Exception as e:
        print(f"An error occurred while writing to {json_output}: {e}")
        os._exit(1)


if __name__ == "__main__":
    main()

    print("----------------")
    print("")
