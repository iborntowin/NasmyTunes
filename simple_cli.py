#!/usr/bin/env python3
"""
Simple CLI for NasmyTunes - Works without FFmpeg
"""
import os
import sys
import argparse
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Spotify credentials
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("❌ Spotify credentials missing!")
        print("Please add to .env file:")
        print("SPOTIFY_CLIENT_ID=your_client_id")
        print("SPOTIFY_CLIENT_SECRET=your_client_secret")
        return False
    
    print("✅ Spotify credentials found")
    
    # Check FFmpeg
    import subprocess
    import shutil
    
    # Try multiple ways to find FFmpeg
    ffmpeg_found = False
    
    # Method 1: Try running ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, timeout=5)
        ffmpeg_found = True
    except:
        pass
    
    # Method 2: Check if ffmpeg is in PATH
    if not ffmpeg_found:
        ffmpeg_found = shutil.which('ffmpeg') is not None
    
    # Method 3: Check common installation paths
    if not ffmpeg_found:
        common_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe"
        ]
        for path in common_paths:
            if os.path.exists(path):
                ffmpeg_found = True
                break
    
    if ffmpeg_found:
        print("✅ FFmpeg is available")
        return True
    else:
        print("❌ FFmpeg not found")
        print("Install FFmpeg:")
        print("  Windows: winget install ffmpeg")
        print("  Then restart your terminal")
        return False

def simple_download(track_name, artists):
    """Simple download function"""
    from youtube_search import YoutubeSearch
    import yt_dlp
    import tempfile
    
    print(f"🎵 Searching: {track_name} by {', '.join(artists)}")
    
    # Search YouTube
    search_query = f"{track_name} {' '.join(artists)}"
    try:
        results = YoutubeSearch(search_query, max_results=1).to_dict()
        if not results:
            return False, "No YouTube results"
        
        video_url = f"https://www.youtube.com/watch?v={results[0]['id']}"
        print(f"  Found: {results[0]['title']}")
        
        # Simple download options
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': f"{track_name} - {', '.join(artists)}.%(ext)s",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        return True, f"Downloaded: {results[0]['title']}"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_playlist_tracks(playlist_url):
    """Get tracks from Spotify playlist"""
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    from src.routes.spotify import extract_playlist_id
    
    print(f"🔍 Analyzing playlist...")
    
    # Setup Spotify
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Get playlist
    playlist_id = extract_playlist_id(playlist_url)
    if not playlist_id:
        print("❌ Invalid playlist URL")
        return None, []
    
    try:
        playlist = sp.playlist(playlist_id)
        tracks = []
        
        results = sp.playlist_tracks(playlist_id)
        while results:
            for item in results['items']:
                if item['track'] and item['track']['type'] == 'track':
                    track = item['track']
                    tracks.append({
                        'name': track['name'],
                        'artists': [artist['name'] for artist in track['artists']]
                    })
            
            if results['next']:
                results = sp.next(results)
            else:
                results = None
        
        print(f"✅ Found: {playlist['name']} ({len(tracks)} tracks)")
        return playlist['name'], tracks
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, []

def main():
    parser = argparse.ArgumentParser(description='Simple NasmyTunes CLI')
    parser.add_argument('playlist_url', nargs='?', help='Spotify playlist URL')
    parser.add_argument('--check', action='store_true', help='Check requirements')
    parser.add_argument('--test', action='store_true', help='Test with single track')
    
    args = parser.parse_args()
    
    print("🎵 NasmyTunes Simple CLI")
    print("=" * 30)
    
    if args.check:
        if check_requirements():
            print("\n✅ All requirements met! Ready to convert.")
        else:
            print("\n❌ Please fix the issues above.")
        return
    
    if args.test:
        print("🧪 Testing with Rick Astley...")
        success, message = simple_download("Never Gonna Give You Up", ["Rick Astley"])
        print(f"Result: {message}")
        return
    
    if not args.playlist_url:
        print("Usage: python simple_cli.py <spotify_playlist_url>")
        print("       python simple_cli.py --check")
        print("       python simple_cli.py --test")
        return
    
    # Check requirements first
    if not check_requirements():
        return
    
    # Get playlist
    playlist_name, tracks = get_playlist_tracks(args.playlist_url)
    if not tracks:
        return
    
    # Convert tracks
    print(f"\n🚀 Starting conversion...")
    successful = 0
    failed = 0
    
    for i, track in enumerate(tracks[:5], 1):  # Limit to 5 tracks for testing
        print(f"\n[{i}/5] Converting...")
        success, message = simple_download(track['name'], track['artists'])
        
        if success:
            print(f"  ✅ {message}")
            successful += 1
        else:
            print(f"  ❌ {message}")
            failed += 1
    
    print(f"\n📊 Results: {successful} successful, {failed} failed")

if __name__ == "__main__":
    main()