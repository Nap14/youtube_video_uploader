# Zoom -> YouTube Uploader 🚀

Automatic uploading of lesson recordings from Zoom to YouTube with playlist organization and report generation.

## Features
- 📂 **Automatic Search**: Finds `.mp4` files in Zoom folders.
- 📅 **Smart Schedule**: Determines course name based on recording date and time.
- 📺 **YouTube API**: Automatic upload as "Unlisted".
- 🎼 **Playlists**: Automatically creates or finds a playlist for a specific group and adds the video.
- 🖼️ **Thumbnails**: Ability to set custom thumbnails for each course.
- 🗑️ **Safe Cleanup**: After successful upload, the Zoom folder is moved to the Trash.

## Setup

### 1. Google API
Place the `client_secret.json` file (obtained in Google Cloud Console) in the root project folder.

### 2. Schedule (`schedule.json`)
Create a `schedule.json` file in the project root based on this example:
```json
{
  "Monday": {
    "15:00": {
      "name": "Python Group 1",
      "thumbnail": "python.jpg"
    },
    "19:00": "Unity Mon+Wed 19:00"
  },
  "Wednesday": {
    "19:00": "Unity Mon+Wed 19:00"
  }
}
```
*Note: Day names must be in English (`Monday`, `Tuesday`, etc.).*

### 3. Thumbnails
All images (e.g., `python.jpg`) should be located in the `thumbnails/` folder.

## Running

### Windows
Run the **`Run.bat`** file. On the first run, it will automatically create a virtual environment and install dependencies.
To create a standalone EXE file, use **`BuildEXE.bat`**.

### macOS / Linux
Use the terminal:
```bash
chmod +x run.sh
./run.sh
```
