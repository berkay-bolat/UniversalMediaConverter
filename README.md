# UniversalMediaConverter

UNIVERSAL VIDEO & AUDIO CONVERTER (GUI)

A modern, dark-themed desktop application to download and convert media from various platforms using yt-dlp and FFmpeg. Built with Python and CustomTkinter.

## FEATURES

* **Universal Support:** Downloads media not just from YouTube, but from hundreds of sites supported by yt-dlp.
* **Media Analysis:** Fetches and displays the title, thumbnail, and duration automatically before downloading.
* **Video Conversion:** Downloads the best available quality and automatically merges video and audio into MP4 format.
* **Audio Conversion:** Extracts and converts audio to WAV, FLAC, MP3, M4A (AAC), OPUS, and OGG (Vorbis).
* **Custom Output Path:** Easily change the directory where your downloaded files are saved (Defaults to `Documents/Universal Media Converter`).
* **Threading & Live Progress:** Non-blocking UI ensures the app doesn't freeze during downloads, complete with a live progress bar, speed tracker, and status updates.
* **Smart Dependency Check:** Automatically checks if FFmpeg is installed on your system and alerts you if it's missing.

## INSTALLATION & USAGE

**Prerequisites:** You must have **FFmpeg** installed on your system and added to your environment variables (PATH).

1. **Install Dependencies:**
   Make sure you install the required Python libraries.
   ```bash
   pip install -r requirements.txt

2. **Run The App:**
   ```bash
   python UniversalMediaConverter.py

## LEGAL DISCLAIMER

This project is developed for educational purposes (to demonstrate proficiency in Python GUI development using CustomTkinter, multithreading, API handling, and subprocess management) only. The developer does not condone the downloading of copyrighted content without permission. Users are solely responsible for ensuring that their actions comply with the respective platform's Terms of Service and applicable copyright laws.
