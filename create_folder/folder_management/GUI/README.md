# Video File Management System

A Python-based video file management system that scans directories, extracts video metadata, and provides a web interface for file selection and organization.

## Overview

This system consists of a Python backend that processes video files in specified directories and extracts metadata such as file size, duration, and tags from filenames. It generates JSON data files that can be used by a web interface for file browsing and selection.

## Features

- **Video File Scanning**: Recursively scans specified directories for video files
- **Metadata Extraction**: Extracts video duration, file size, and filename-based tags
- **Interactive Preview**: Displays video preview using OpenCV before processing
- **File Renaming**: Optional interactive file renaming functionality
- **JSON Output**: Generates structured JSON files for web interface consumption
- **Web Interface**: HTML/JavaScript frontend for file selection and management

## File Structure

```
folder_management/
├── folder_name_to_json.py          # Main Python script
├── GUI/
│   ├── README.md                   # This file
│   ├── mp4_file_select.html        # Web interface
│   ├── javascript/                 # Frontend JavaScript files
│   └── json/                       # JSON data files
│       ├── folder_path.json        # Directory configuration
│       ├── files_data.json         # Generated file metadata
│       └── abbre_txt.json          # Additional configuration
```

## Prerequisites

### Required Python Packages

```bash
pip install opencv-python
pip install moviepy
```

### System Requirements

- Python 3.7+
- OpenCV compatible system
- Video codec support for various formats

## Setup

1. **Install Dependencies**
   ```bash
   pip install opencv-python moviepy
   ```

2. **Configure Directory Paths**
   
   Create or edit `GUI/json/folder_path.json` with your directory structure:
   ```json
   {
     "drive1": {
       "folders": {
         "folder1": "path/to/your/first/directory",
         "folder2": "path/to/your/second/directory"
       }
     },
     "drive2": {
       "folders": {
         "folder3": "path/to/another/directory",
         "folder4": "path/to/yet/another/directory"
       }
     }
   }
   ```

3. **Directory Structure**
   
   Ensure the following directories exist:
   - `GUI/json/` - For JSON data files
   - Video directories specified in `folder_path.json`

## Usage

### Running the Scanner

1. **Navigate to the script directory:**
   ```bash
   cd path/to/folder_management
   ```

2. **Run the main script:**
   ```bash
   python folder_name_to_json.py
   ```

3. **Interactive Options:**
   - Choose whether to enable file renaming (`y/n`)
   - For each video file (if renaming enabled):
     - Preview the video using OpenCV
     - Press 'q' or 'c' to close preview
     - Optionally rename the file

### Expected Output

The script generates `GUI/json/files_data.json` with the following structure:

```json
[
  {
    "path": "/full/path/to/video.mp4",
    "name": "video_name_without_extension",
    "size_MB": "150.25 MB",
    "video_length": "5 minutes 30 seconds",
    "tags": ["tag1", "tag2", "tag3"]
  }
]
```

## Supported Video Formats

- `.mp4` (with duration extraction)
- `.mkv`
- `.avi`
- `.mov`
- `.wmv`
- `.flv`
- `.webm`

## Filename Tag System

The system extracts tags from filenames using the hyphen (`-`) separator:

**Example:** `action-comedy-2023-hd.mp4`
- **Tags:** `["action", "comedy", "2023", "hd"]`
- **Name:** `action-comedy-2023-hd`

### Special Handling

- Removes Clipchamp watermark text: `" - Made with Clipchamp.mp4"`
- Skips files without hyphens in the name
- Supports all listed video extensions

## Web Interface

The `mp4_file_select.html` file provides a web-based interface for:

- Browsing processed video files
- Filtering by tags
- Viewing file metadata
- File selection functionality

To use the web interface:
1. Run the Python scanner first to generate JSON data
2. Open `GUI/mp4_file_select.html` in a web browser
3. Browse and select files using the interface

## Configuration Files

### folder_path.json
Defines the directory structure to scan:
```json
{
  "drive_name": {
    "folders": {
      "folder_key": "relative_or_absolute_path"
    }
  }
}
```

### files_data.json (Generated)
Contains processed file metadata - automatically created by the scanner.

### abbre_txt.json
Additional configuration file for abbreviations or custom settings.

## Error Handling

The system includes comprehensive error handling for:

- Missing configuration files
- Invalid JSON formats
- Directory access issues
- Video processing errors
- File I/O operations

### Common Issues

1. **FileNotFoundError for folder_path.json**
   - Ensure the file exists in `GUI/json/`
   - Check JSON format validity

2. **Video preview not working**
   - Verify OpenCV installation
   - Check video codec support

3. **Permission errors**
   - Ensure read/write access to target directories
   - Run with appropriate permissions

## Development Notes

### Key Functions

- `walk_directory()`: Recursively scans directories for files
- `get_video_length()`: Extracts video duration using MoviePy
- `preview_video()`: Displays video preview using OpenCV
- `rename_file()`: Interactive file renaming functionality

### Performance Considerations

- Processing time depends on:
  - Number of video files
  - File sizes
  - Video duration calculation overhead
- Large directories may take several minutes to process

## Customization

### Adding New Video Formats

Edit the `extentions` list in `main()`:
```python
extentions = [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".your_format"]
```

### Modifying Tag Extraction

The tag extraction logic can be customized in the main processing loop:
```python
tags = file_name.split("-")  # Current: hyphen separator
# Modify this line for different tag extraction methods
```

## Contributing

When contributing to this project:

1. Maintain backward compatibility with existing JSON formats
2. Test with various video formats and directory structures
3. Update documentation for new features
4. Follow existing code style and error handling patterns

