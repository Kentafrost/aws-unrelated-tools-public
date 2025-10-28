# Automation Scripts in Python

## Overview(概略)
This repository contains Python scripts for automating various tasks, such as:
- creating new folders and moving files based on data from a Google Sheets file.
- retrieving email data from Gmail and calculating totals based on extracted information.
- set up task scheduler
- editing video including crop, merge, merge same mp4 files several times, merge a mp4 file with a audio file.
- automatic click buttons to record video efficiently

## Features(特徴)
- **Folder Automation**: Automatically organizes files into folders based on structured data.
- **Gmail Data Retrieval**: Fetches specific emails and performs calculations on relevant data.

## Requirements(必要条件)
Before running the scripts, ensure you have the following installed:
- Python 3.x
- Required dependencies (listed in `requirements.txt`)

## Setup to use(使用方法)
1. Clone this repository:
```bash
- git clone <repository_url>
```

2. requirements.txtからインストール
```bash
- pip install -r requirements.txt
```

3. 仮想環境をセットアップする場合
```bash
- python -m venv .venv
- rem Activate the virtual environment
- call .\.venv\Scripts\activate
- pip install -r requirements.txt
```