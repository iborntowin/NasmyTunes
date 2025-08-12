#!/usr/bin/env python3
"""
NasmyTunes CLI - Simple Spotify to MP3 Converter
"""
import os
import sys
import tempfile
import zipfile
from pathlib import Path
import argparse
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.simple_bypass import SimpleBypass
from src.routes.spotify import extract_playlist_id
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables
load_dotenv()

class NasmyTunesCLI:
    def __init__(self):
        self.bypass = SimpleBypass()
        self.setup_spotify()
    
    def setup_spotify(self):
        """Initialize Spotify client"""
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
    
    def get_playlist_tracks(self, playlist_url):
        """Get tracks from Spotify playlist"""
        print(f"🔍 Analyzing playlist: {playlist_url}")
        
        playlist_id = extract_playlist_id(playlist_url)
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
    
    def convert_tracks(self, tracks, output_dir, playlist_name="playlist"):
        """Convert tracks to MP3"""
        print(f"\n🎵 Starting conversion to: {output_dir}")
        
        successful = []
        failed = []
        
        for i, track in enumerate(tracks, 1):
            track_name = f"{track['name']} - {', '.join(track['artists'])}"
            print(f"\n[{i}/{len(tracks)}] Converting: {track_name}")
            
            try:
                success, message = self.bypass.download_simple(
                    track['name'], 
                    track['artists'], 
                    output_dir
                )
                
                if success:
                    print(f"  ✅ {message}")
                    successful.append(track_name)
                else:
                    print(f"  ❌ {message}")
                    failed.append(track_name)
                    
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                failed.append(track_name)
        
        return successful, failed
    
    def create_zip(self, output_dir, playlist_name):
        """Create ZIP file with converted tracks"""
        mp3_files = [f for f in os.listdir(output_dir) if f.endswith('.mp3')]
        
        if not mp3_files:
            print("❌ No MP3 files to zip")
            return None
        
        zip_name = f"{playlist_name.replace(' ', '_')}.zip"
        zip_path = os.path.join(output_dir, zip_name)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for mp3_file in mp3_files:
                file_path = os.path.join(output_dir, mp3_file)
                zipf.write(file_path, mp3_file)
        
        print(f"📦 Created ZIP: {zip_path}")
        return zip_path
    
    def run(self, playlist_url, output_dir=None, create_zip_file=False):
        """Main conversion process"""
        print("🎵 NasmyTunes CLI - Spotify to MP3 Converter")
        print("=" * 50)
        
        # Get playlist tracks
        playlist_name, tracks = self.get_playlist_tracks(playlist_url)
        if not tracks:
            return
        
        # Setup output directory
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), "downloads")
        
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output directory: {output_dir}")
        
        # Convert tracks
        successful, failed = self.convert_tracks(tracks, output_dir, playlist_name)
        
        # Create ZIP if requested
        if create_zip_file and successful:
            self.create_zip(output_dir, playlist_name or "playlist")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 CONVERSION SUMMARY")
        print("=" * 50)
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"📁 Output: {output_dir}")
        
        if failed:
            print(f"\n❌ Failed tracks:")
            for track in failed:
                print(f"  - {track}")
        
        if successful:
            print(f"\n🎉 Successfully converted {len(successful)} tracks!")
        else:
            print(f"\n😞 No tracks were converted successfully.")

def main():
    parser = argparse.ArgumentParser(description='NasmyTunes CLI - Convert Spotify playlists to MP3')
    parser.add_argument('playlist_url', help='Spotify playlist URL')
    parser.add_argument('-o', '--output', help='Output directory (default: ./downloads)')
    parser.add_argument('-z', '--zip', action='store_true', help='Create ZIP file')
    parser.add_argument('--check-ffmpeg', action='store_true', help='Check FFmpeg installation')
    
    args = parser.parse_args()
    
    # Check FFmpeg if requested
    if args.check_ffmpeg:
        import subprocess
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            print("✅ FFmpeg is installed and working!")
            print(f"Version: {result.stdout.split()[2]}")
        except FileNotFoundError:
            print("❌ FFmpeg not found!")
            print("Install FFmpeg:")
            print("  Windows: winget install ffmpeg")
            print("  macOS: brew install ffmpeg")
            print("  Linux: sudo apt install ffmpeg")
        return
    
    # Run conversion
    cli = NasmyTunesCLI()
    cli.run(args.playlist_url, args.output, args.zip)

if __name__ == "__main__":
    main()