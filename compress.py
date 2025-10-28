# compress files in a folder
import os
import zipfile

# select folders in the gui
import tkinter as tk
from tkinter import filedialog

"""Choose files to compress"""
def select_paths(choice):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    if choice == "files":
        file_paths = filedialog.askopenfilenames(title="Select Files to Compress")
    elif choice == "folders":
        file_paths = filedialog.askdirectory(title="Select Folder to Compress")
    return file_paths


"""Compress the selected files into a zip file"""
def compress_files(file_paths):
    zip_filename = file_paths.split("/")[-1] + ".zip" if isinstance(file_paths, str) else "compressed_files.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)
    print(f"Files compressed to '{zip_filename}'")
    
    
if __name__ == "__main__":

    print("Do you want to compress the selected folder? (y/n): ")
    print("y: compress the selected folder")
    print("n: compress the selected files")
    print("")
    folders_select_choice = input("Please enter your choice (y/n): ").strip().lower()
    
    if folders_select_choice not in ['y', 'n']:
        print("Invalid input. Please enter 'y' or 'n'.")
        os._exit(1)
    
    if folders_select_choice == 'y':
        path = select_paths("folders")
    elif folders_select_choice == 'n':
        path = select_paths("files")
    else:
        print("Invalid input. Please enter 'y' or 'n'.")
        os._exit(1)
    
    compress_files(path)