# NasmyTunes CLI - Installation Guide

## Quick Setup (Recommended)

1. **Download the project**
   ```bash
   git clone <repository-url>
   cd nasmytunes
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```
   This will:
   - Install all Python dependencies
   - Download and setup FFmpeg automatically
   - Create launcher scripts
   - Create .env template

3. **Configure Spotify API**
   - Edit the `.env` file with your Spotify credentials:
   ```
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   ```
   - Get credentials from: https://developer.spotify.com/dashboard/applications

4. **Start using NasmyTunes**
   
   **Windows:**
   ```cmd
   nasmytunes.bat https://open.spotify.com/playlist/YOUR_PLAYLIST_ID
   ```
   
   **Mac/Linux:**
   ```bash
   ./nasmytunes.sh https://open.spotify.com/playlist/YOUR_PLAYLIST_ID
   ```

## Manual Setup (Alternative)

If the automatic setup doesn't work:

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download FFmpeg manually**
   - Windows: Download from https://ffmpeg.org/download.html
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`
   - Place the executable in `ffmpeg/ffmpeg.exe` (Windows) or `ffmpeg/ffmpeg` (Mac/Linux)

3. **Configure .env file** (same as step 3 above)

4. **Run directly**
   ```bash
   python nasmytunes_cli.py https://open.spotify.com/playlist/YOUR_PLAYLIST_ID
   ```

## Usage Examples

```bash
# Convert entire playlist
nasmytunes.bat "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

# Convert first 10 tracks only
nasmytunes.bat "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" -n 10

# Specify output directory
nasmytunes.bat "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M" -o "C:\Music"

# Test with single track
nasmytunes.bat --test
```

## Troubleshooting

**"FFmpeg not found" error:**
- Run `python setup.py` again
- Or manually download FFmpeg and place in `ffmpeg/` folder

**"Spotify credentials not found" error:**
- Make sure `.env` file exists and has valid credentials
- Get credentials from Spotify Developer Dashboard

**Downloads failing:**
- Try running with `--test` first
- Check your internet connection
- Some tracks may not be available on YouTube

## Features

- ✅ Automatic FFmpeg setup
- ✅ Spotify playlist integration
- ✅ YouTube audio download
- ✅ MP3 conversion
- ✅ Batch processing
- ✅ ZIP file creation
- ✅ Cross-platform support
- ✅ Progress tracking
- ✅ Error handling

## System Requirements

- Python 3.7+
- Internet connection
- ~100MB free space (for FFmpeg)