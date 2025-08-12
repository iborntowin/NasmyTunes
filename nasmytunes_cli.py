#!/usr/bin/env python3
"""
NasmyTunes CLI - Robust Spotify to MP3 Converter
Works with bundled FFmpeg for easy deployment
"""
import os
import sys
import argparse
import tempfile
import zipfile
import platform
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

def get_ffmpeg_path():
    """Get the path to bundled FFmpeg executable"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    system = platform.system().lower()
    
    if system == 'windows':
        ffmpeg_path = os.path.join(script_dir, 'ffmpeg', 'ffmpeg.exe')
    else:
        ffmpeg_path = os.path.join(script_dir, 'ffmpeg', 'ffmpeg')
    
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    
    # Fallback to system FFmpeg
    return 'ffmpeg'

class NasmyTunesCLI:
    def __init__(self):
        self.setup_spotify()
    
    def setup_spotify(self):
        """Initialize Spotify client"""
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
        
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("❌ Error: Spotify credentials not found!")
            print("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file")
            sys.exit(1)
        
        try:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            print("✅ Spotify API connected")
        except Exception as e:
            print(f"❌ Spotify API error: {e}")
            sys.exit(1)
    
    def extract_playlist_id(self, url):
        """Extract playlist ID from Spotify URL"""
        try:
            if 'open.spotify.com/playlist/' in url:
                return url.split('playlist/')[1].split('?')[0]
            elif 'spotify:playlist:' in url:
                return url.split('playlist:')[1]
            else:
                return None
        except:
            return None
    
    def get_playlist_tracks(self, playlist_url):
        """Get tracks from Spotify playlist"""
        print(f"🔍 Analyzing playlist...")
        
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            print("❌ Invalid Spotify playlist URL")
            return None, []
        
        try:
            playlist = self.sp.playlist(playlist_id)
            tracks = []
            
            results = self.sp.playlist_tracks(playlist_id)
            while results:
                for item in results['items']:
                    if item['track'] and item['track']['type'] == 'track':
                        track = item['track']
                        tracks.append({
                            'name': track['name'],
                            'artists': [artist['name'] for artist in track['artists']],
                            'duration_ms': track['duration_ms']
                        })
                
                if results['next']:
                    results = self.sp.next(results)
                else:
                    results = None
            
            print(f"✅ Found playlist: {playlist['name']}")
            print(f"📊 Total tracks: {len(tracks)}")
            return playlist['name'], tracks
            
        except Exception as e:
            print(f"❌ Error fetching playlist: {e}")
            return None, []
    
    def download_track(self, track_name, artists, output_dir):
        """Download a single track using the most reliable method"""
        from youtube_search import YoutubeSearch
        import yt_dlp
        import random
        
        print(f"  🎵 {track_name} by {', '.join(artists)}")
        
        # Search YouTube
        search_query = f"{track_name} {' '.join(artists)}"
        try:
            results = YoutubeSearch(search_query, max_results=2).to_dict()
            if not results:
                return False, "No YouTube results found"
            
            # Try each result
            for result in results:
                video_url = f"https://www.youtube.com/watch?v={result['id']}"
                print(f"    Trying: {result['title'][:50]}...")
                
                # Create safe filename
                safe_name = "".join(c for c in f"{track_name} - {', '.join(artists)}" 
                                  if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                
                # Get FFmpeg path
                ffmpeg_path = get_ffmpeg_path()
                
                # Robust yt-dlp options with bundled FFmpeg
                ydl_opts = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'outtmpl': os.path.join(output_dir, f'{safe_name}.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '128',  # Lower quality for reliability
                    }],
                    'ffmpeg_location': ffmpeg_path,
                    'quiet': True,
                    'no_warnings': True,
                    'ignoreerrors': True,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android'],
                        }
                    },
                    'retries': 3,
                }
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    
                    # Check if file was created
                    for file in os.listdir(output_dir):
                        if safe_name.lower() in file.lower() and file.endswith('.mp3'):
                            print(f"    ✅ Success: {file}")
                            return True, f"Downloaded: {result['title']}"
                    
                except Exception as e:
                    print(f"    ❌ Failed: {str(e)[:50]}...")
                    continue
            
            return False, "All download attempts failed"
            
        except Exception as e:
            return False, f"Search error: {str(e)}"
    
    def convert_playlist(self, playlist_url, output_dir=None, max_tracks=None):
        """Convert entire playlist"""
        print("🎵 NasmyTunes CLI - Spotify to MP3 Converter")
        print("=" * 50)
        
        # Get playlist tracks
        playlist_name, tracks = self.get_playlist_tracks(playlist_url)
        if not tracks:
            return
        
        # Limit tracks if specified
        if max_tracks:
            tracks = tracks[:max_tracks]
            print(f"📝 Limited to first {max_tracks} tracks")
        
        # Setup output directory
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), "downloads")
        
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output directory: {output_dir}")
        
        # Convert tracks
        print(f"\n🚀 Starting conversion...")
        successful = []
        failed = []
        
        for i, track in enumerate(tracks, 1):
            print(f"\n[{i}/{len(tracks)}] Converting:")
            
            try:
                success, message = self.download_track(
                    track['name'], 
                    track['artists'], 
                    output_dir
                )
                
                if success:
                    successful.append(f"{track['name']} - {', '.join(track['artists'])}")
                else:
                    failed.append(f"{track['name']} - {', '.join(track['artists'])}: {message}")
                    
            except Exception as e:
                failed.append(f"{track['name']} - {', '.join(track['artists'])}: {str(e)}")
        
        # Create ZIP file
        mp3_files = [f for f in os.listdir(output_dir) if f.endswith('.mp3')]
        if mp3_files:
            zip_name = f"{playlist_name.replace(' ', '_')}.zip"
            zip_path = os.path.join(output_dir, zip_name)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for mp3_file in mp3_files:
                    file_path = os.path.join(output_dir, mp3_file)
                    zipf.write(file_path, mp3_file)
            
            print(f"\n📦 Created ZIP: {zip_path}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 CONVERSION SUMMARY")
        print("=" * 50)
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"📁 Output: {output_dir}")
        
        if successful:
            print(f"\n✅ Successfully converted:")
            for track in successful:
                print(f"  - {track}")
        
        if failed:
            print(f"\n❌ Failed tracks:")
            for track in failed[:5]:  # Show first 5 failures
                print(f"  - {track}")
            if len(failed) > 5:
                print(f"  ... and {len(failed) - 5} more")
        
        if successful:
            print(f"\n🎉 Conversion completed! {len(successful)} tracks ready.")
        else:
            print(f"\n😞 No tracks were converted successfully.")

def main():
    parser = argparse.ArgumentParser(description='NasmyTunes CLI - Convert Spotify playlists to MP3')
    parser.add_argument('playlist_url', nargs='?', help='Spotify playlist URL')
    parser.add_argument('-o', '--output', help='Output directory (default: ./downloads)')
    parser.add_argument('-n', '--number', type=int, help='Maximum number of tracks to convert')
    parser.add_argument('--test', action='store_true', help='Test with single track')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Testing with a single track...")
        os.makedirs("./test_downloads", exist_ok=True)
        cli = NasmyTunesCLI()
        success, message = cli.download_track("Never Gonna Give You Up", ["Rick Astley"], "./test_downloads")
        print(f"Test result: {message}")
        return
    
    if not args.playlist_url:
        print("❌ Please provide a Spotify playlist URL")
        print("Usage: python nasmytunes_cli.py <playlist_url>")
        print("       python nasmytunes_cli.py --test")
        return
    
    # Run conversion
    cli = NasmyTunesCLI()
    cli.convert_playlist(args.playlist_url, args.output, args.number)

if __name__ == "__main__":
    main()