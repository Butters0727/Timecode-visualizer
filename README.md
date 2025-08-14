# Timecode Visualizer

A simple, local web-based tool to visualize and align timecode data from `.tc` and `.mp4` files. This tool provides an interactive timeline interface to compare the time ranges of multiple files, making it easy to see their relative offsets and durations.

## Features

- **Multi-File Support**: Add and visualize multiple `.tc` and `.mp4` files on the same timeline.
- **Automatic Parsing**: Extracts timecode from `.tc` files (first and last line) and from `.mp4` files using `ffprobe`.
- **Interactive UI**:
    - Global drag-and-drop or click-to-upload files.
    - UI adapts after the first file is added for a cleaner workspace.
    - Dynamically add and remove files from the timeline.
- **Advanced Timeline Controls**:
    - Zoom and pan the timeline.
    - Vertical hover line shows the precise time under the cursor.
    - Snapping to the start and end points of each clip for precision analysis.
    - Tooltips on clips to show their exact start and end times.

## Prerequisites

- Python 3.x
- `pip` (Python's package installer)

## Setup

There are two one-time setup steps to get the tool running.

**1. Install Python Dependencies**

Open a terminal or command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

**2. Download and Place `ffprobe.exe`**

This tool requires the `ffprobe.exe` command-line program to read timecode from MP4 files. The server is configured to automatically use it if it's placed alongside `server.py`.

1.  **Download FFmpeg**: Visit a trusted source for static FFmpeg builds, such as [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/).
2.  **Find and Download**: Scroll to the "release builds" section and download the `ffmpeg-release-full.7z` archive.
3.  **Extract**: Unzip the downloaded file.
4.  **Copy**: Find `ffprobe.exe` inside the `bin` folder of the extracted files. Copy this single `ffprobe.exe` file into the root of this project directory (the same folder where `server.py` is located).

## Running the Application

After the one-time setup is complete, running the application is a single step.

1.  **Execute the server script** in a terminal from the project directory:
    ```bash
    python server.py
    ```
2.  This command will start the local server and **automatically open the application** in your default web browser at `http://127.0.0.1:5000`.

## How to Use the App

- **Adding Files**: Drag and drop your `.tc` or `.mp4` files anywhere onto the page. After the first file is added, you can also use the `+ Add Files` button at the top right.
- **Viewing Tooltips**: Hover your mouse over the colored bars on the timeline to see their start and end times. Hover over the timeline's empty space to see the precise time on the axis.
- **Snapping**: The vertical line that follows your mouse will automatically snap to the start and end edges of the bars as you move close to them.
- **Deleting Files**: Hover over a file's name in the left-hand panel. An `×` button will appear. Click it to remove the file from the timeline.
