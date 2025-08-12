#!/usr/bin/env python3
"""
NasmyTunes Setup Script
Downloads FFmpeg and sets up the CLI for easy use
"""
import os
import sys
import platform
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path

def get_ffmpeg_url():
    """Get the appropriate FFmpeg download URL for the current platform"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "windows":
        if "64" in arch or "amd64" in arch:
            return "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        else:
            return "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win32-gpl.zip"
    elif system == "darwin":  # macOS
        return "https://evermeet.cx/ffmpeg/ffmpeg-6.1.zip"
    elif system == "linux":
        if "64" in arch or "amd64" in arch:
            return "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        else:
            return "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz"
    else:
        return None

def download_file(url, filename):
    """Download a file with progress"""
    print(f"📥 Downloading {filename}...")
    
    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, (downloaded * 100) // total_size)
            print(f"\r  Progress: {percent}% ({downloaded // 1024 // 1024}MB)", end="")
    
    urllib.request.urlretrieve(url, filename, progress_hook)
    print()  # New line after progress

def extract_ffmpeg(archive_path, extract_to):
    """Extract FFmpeg from downloaded archive"""
    print(f"📦 Extracting FFmpeg...")
    
    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    elif archive_path.endswith('.tar.xz'):
        with tarfile.open(archive_path, 'r:xz') as tar_ref:
            tar_ref.extractall(extract_to)
    
    # Find the ffmpeg executable
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            if file.startswith('ffmpeg') and (file.endswith('.exe') or 'ffmpeg' == file):
                ffmpeg_path = os.path.join(root, file)
                return ffmpeg_path
    
    return None

def setup_ffmpeg():
    """Download and setup FFmpeg"""
    print("🔧 Setting up FFmpeg...")
    
    # Create ffmpeg directory
    ffmpeg_dir = os.path.join(os.path.dirname(__file__), 'ffmpeg')
    os.makedirs(ffmpeg_dir, exist_ok=True)
    
    # Check if FFmpeg already exists
    system = platform.system().lower()
    ffmpeg_exe = 'ffmpeg.exe' if system == 'windows' else 'ffmpeg'
    ffmpeg_path = os.path.join(ffmpeg_dir, ffmpeg_exe)
    
    if os.path.exists(ffmpeg_path):
        print("✅ FFmpeg already installed")
        return ffmpeg_path
    
    # Get download URL
    url = get_ffmpeg_url()
    if not url:
        print("❌ Unsupported platform for automatic FFmpeg download")
        print("Please manually download FFmpeg and place it in the 'ffmpeg' folder")
        return None
    
    # Download FFmpeg
    temp_dir = os.path.join(ffmpeg_dir, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    archive_name = url.split('/')[-1]
    archive_path = os.path.join(temp_dir, archive_name)
    
    try:
        download_file(url, archive_path)
        
        # Extract FFmpeg
        extracted_ffmpeg = extract_ffmpeg(archive_path, temp_dir)
        if extracted_ffmpeg:
            # Move to final location
            shutil.move(extracted_ffmpeg, ffmpeg_path)
            print(f"✅ FFmpeg installed to: {ffmpeg_path}")
            
            # Make executable on Unix systems
            if system != 'windows':
                os.chmod(ffmpeg_path, 0o755)
            
            # Cleanup
            shutil.rmtree(temp_dir)
            return ffmpeg_path
        else:
            print("❌ Could not find FFmpeg executable in archive")
            return None
            
    except Exception as e:
        print(f"❌ Error setting up FFmpeg: {e}")
        return None

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Use minimal requirements for CLI
    requirements_file = 'requirements_cli.txt' if os.path.exists('requirements_cli.txt') else 'requirements.txt'
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Error installing dependencies: {result.stderr}")
            print("Trying to install individual packages...")
            
            # Fallback: install core packages individually
            core_packages = ['spotipy', 'yt-dlp', 'youtube-search', 'python-dotenv', 'requests']
            for package in core_packages:
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                 capture_output=True, text=True, check=True)
                    print(f"  ✅ {package}")
                except:
                    print(f"  ❌ {package}")
            return True
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_launcher():
    """Create platform-specific launcher scripts"""
    print("🚀 Creating launcher scripts...")
    
    system = platform.system().lower()
    
    if system == 'windows':
        # Create batch file
        batch_content = '''@echo off
cd /d "%~dp0"
python nasmytunes_cli.py %*
pause
'''
        with open('nasmytunes.bat', 'w') as f:
            f.write(batch_content)
        print("✅ Created nasmytunes.bat")
        
    else:
        # Create shell script
        shell_content = '''#!/bin/bash
cd "$(dirname "$0")"
python3 nasmytunes_cli.py "$@"
'''
        with open('nasmytunes.sh', 'w') as f:
            f.write(shell_content)
        os.chmod('nasmytunes.sh', 0o755)
        print("✅ Created nasmytunes.sh")

def create_env_template():
    """Create .env template if it doesn't exist"""
    if not os.path.exists('.env'):
        env_content = '''# Spotify API Credentials
# Get these from: https://developer.spotify.com/dashboard/applications
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
'''
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env template")
        print("⚠️  Please edit .env file with your Spotify API credentials")
    else:
        print("✅ .env file already exists")

def main():
    print("🎵 NasmyTunes Setup")
    print("=" * 40)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed: Could not install dependencies")
        return
    
    # Setup FFmpeg
    ffmpeg_path = setup_ffmpeg()
    if not ffmpeg_path:
        print("❌ Setup failed: Could not setup FFmpeg")
        return
    
    # Create launcher
    create_launcher()
    
    # Create env template
    create_env_template()
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("=" * 40)
    print("\nNext steps:")
    print("1. Edit .env file with your Spotify API credentials")
    print("2. Run the CLI:")
    
    system = platform.system().lower()
    if system == 'windows':
        print("   - Double-click nasmytunes.bat")
        print("   - Or run: nasmytunes.bat <playlist_url>")
    else:
        print("   - Run: ./nasmytunes.sh <playlist_url>")
        print("   - Or: python3 nasmytunes_cli.py <playlist_url>")
    
    print("\nExample:")
    print("  nasmytunes.bat https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
    print("\nFor help: python nasmytunes_cli.py --help")

if __name__ == "__main__":
    main()