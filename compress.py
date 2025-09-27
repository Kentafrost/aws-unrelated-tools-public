# compress files in a folder
import os
import zipfile

# select folders in the gui
import tkinter as tk
from tkinter import filedialog

"""Choose files to compress"""
def select_files():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_paths = filedialog.askopenfilenames(title="Select Files to Compress")
    return file_paths


"""Compress the selected files into a zip file"""
def compress_files(file_paths):    
    zip_filename = "compressed_files.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)
    print(f"Files compressed to '{zip_filename}'")
    
if __name__ == "__main__":
    selected_files = select_files()

    if selected_files:
        compress_files(selected_files)
    else:
        print("No files selected.")
        os._exit(1)