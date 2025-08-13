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
    
    def validate_playlist_access(self, playlist_id):
        """Check if playlist is accessible before full processing"""
        try:
            # Try to get basic playlist info first
            playlist = self.sp.playlist(playlist_id, fields="name,public,owner,tracks.total")
            
            # Check if playlist is public
            if not playlist.get('public', True):
                print("⚠️  Warning: This playlist appears to be private")
                print("   You can only convert public playlists")
                return False
                
            print(f"✅ Playlist found: {playlist.get('name', 'Unknown')}")
            print(f"📊 Total tracks: {playlist.get('tracks', {}).get('total', 0)}")
            return True
            
        except Exception as e:
            if "404" in str(e):
                print("❌ Playlist not found or not accessible")
                print("💡 Possible reasons:")
                print("   • Playlist is private or deleted")
                print("   • Playlist is region-restricted")
                print("   • Invalid playlist URL")
                print("   • You don't have access to this playlist")
            else:
                print(f"❌ Error accessing playlist: {e}")
            return False
    
    def get_playlist_tracks(self, playlist_url):
        """Get tracks from Spotify playlist"""
        print(f"🔍 Analyzing playlist...")
        
        playlist_id = self.extract_playlist_id(playlist_url)
        if not playlist_id:
            print("❌ Invalid Spotify playlist URL")
            print("💡 Make sure your URL looks like:")
            print("   https://open.spotify.com/playlist/PLAYLIST_ID")
            return None, []
        
        # Validate playlist access first
        if not self.validate_playlist_access(playlist_id):
            print("\n🎵 Try these working playlists instead:")
            print("   • https://open.spotify.com/playlist/5VZvJmyPmCIsY6rJ5JJ10X")
            print("   • https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd")
            print("   • Or use any PUBLIC playlist you own")
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
            error_msg = str(e)
            print(f"❌ Error fetching playlist: {error_msg}")
            
            # Provide helpful error messages
            if "404" in error_msg or "Resource not found" in error_msg:
                print("\n💡 Possible reasons:")
                print("   • Playlist is private (make it public)")
                print("   • Playlist doesn't exist or was deleted")
                print("   • Playlist is region-restricted")
                print("   • You don't have access to this playlist")
                print("\n🔧 Solutions:")
                print("   • Try a different playlist")
                print("   • Make sure the playlist is public")
                print("   • Use a playlist you own or have access to")
            elif "401" in error_msg or "invalid_client" in error_msg:
                print("\n💡 This is an API credentials issue:")
                print("   • Check your .env file")
                print("   • Verify your Client ID and Secret")
                print("   • Visit: https://developer.spotify.com/dashboard")
            
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

def show_welcome():
    """Show welcome message on first run"""
    print("🎵 Welcome to NasmyTunes!")
    print("=" * 50)
    print("✅ Setup complete! Ready to convert Spotify playlists to MP3")
    print("💡 Make sure your .env file has valid Spotify API credentials")
    print("🔗 Get credentials: https://developer.spotify.com/dashboard")
    print("=" * 50)

def show_menu():
    """Display the main menu"""
    print("\n🎵 NasmyTunes CLI - Main Menu")
    print("=" * 40)
    print("1. 🎵 Convert Spotify Playlist to MP3")
    print("2. 🧪 Test Download (Single Track)")
    print("3. 📖 Help & Instructions")
    print("4. 🚪 Exit")
    print("=" * 40)

def get_user_choice():
    """Get user menu choice"""
    while True:
        try:
            choice = input("👉 Select an option (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return int(choice)
            else:
                print("❌ Please enter a number between 1-4")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except:
            print("❌ Please enter a valid number")

def show_help():
    """Show help and instructions"""
    print("\n📖 NasmyTunes Help & Instructions")
    print("=" * 50)
    
    print("\n🔑 SPOTIFY API SETUP:")
    print("1. Visit: https://developer.spotify.com/dashboard")
    print("2. Create a new app")
    print("3. Copy Client ID and Client Secret")
    print("4. Edit .env file with your credentials")
    
    print("\n🎵 HOW TO CONVERT PLAYLISTS:")
    print("1. Get your Spotify playlist URL:")
    print("   • Open Spotify app or web player")
    print("   • Go to your playlist")
    print("   • Click 'Share' → 'Copy link to playlist'")
    print("   • Example: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
    print("\n2. Select option 1 in the main menu")
    print("3. Paste the playlist URL when prompted")
    print("4. Choose your preferences (or press Enter for defaults)")
    print("5. Wait for conversion to complete")
    print("6. Find your MP3 files in the downloads folder")
    
    print("\n💡 TIPS & TROUBLESHOOTING:")
    print("• Make sure your playlist is public or you own it")
    print("• Conversion time depends on playlist size")
    print("• Files are saved as high-quality MP3s")
    print("• A ZIP file is created with all tracks")
    print("• Use option 2 to test if everything works")
    
    print("\n🎵 EXAMPLE PLAYLISTS TO TRY:")
    print("• Test Playlist: https://open.spotify.com/playlist/5VZvJmyPmCIsY6rJ5JJ10X")
    print("• Make sure to use PUBLIC playlists only!")
    
    print("\n🔗 USEFUL LINKS:")
    print("• Spotify Developer Dashboard: https://developer.spotify.com/dashboard")
    print("• Web API Documentation: https://developer.spotify.com/documentation/web-api")
    print("• GitHub Repository: https://github.com/iborntowin/NasmyTunes")

def get_playlist_options():
    """Get playlist conversion options from user"""
    print("\n🎵 Playlist Conversion Setup")
    print("=" * 30)
    
    # Get playlist URL
    while True:
        playlist_url = input("📋 Paste your Spotify playlist URL: ").strip()
        if not playlist_url:
            print("❌ Please enter a playlist URL")
            continue
        if 'spotify.com/playlist/' not in playlist_url and 'spotify:playlist:' not in playlist_url:
            print("❌ Please enter a valid Spotify playlist URL")
            continue
        break
    
    # Get output directory (optional)
    output_dir = input("📁 Output folder (press Enter for default 'downloads'): ").strip()
    if not output_dir:
        output_dir = None
    
    # Get max tracks (optional)
    while True:
        max_tracks_input = input("🔢 Max tracks to convert (press Enter for all): ").strip()
        if not max_tracks_input:
            max_tracks = None
            break
        try:
            max_tracks = int(max_tracks_input)
            if max_tracks <= 0:
                print("❌ Please enter a positive number")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid number")
    
    return playlist_url, output_dir, max_tracks

def run_test():
    """Run a test download"""
    print("\n🧪 Testing Download...")
    print("=" * 30)
    print("Testing with: 'Never Gonna Give You Up' by Rick Astley")
    
    os.makedirs("./test_downloads", exist_ok=True)
    cli = NasmyTunesCLI()
    success, message = cli.download_track("Never Gonna Give You Up", ["Rick Astley"], "./test_downloads")
    
    if success:
        print(f"✅ Test successful: {message}")
        print("📁 Check the 'test_downloads' folder for the MP3 file")
    else:
        print(f"❌ Test failed: {message}")
    
    input("\nPress Enter to continue...")

def main():
    """Main application loop"""
    try:
        # Show welcome message on first run
        show_welcome()
        
        while True:
            show_menu()
            choice = get_user_choice()
            
            if choice == 1:
                # Convert playlist
                try:
                    playlist_url, output_dir, max_tracks = get_playlist_options()
                    cli = NasmyTunesCLI()
                    cli.convert_playlist(playlist_url, output_dir, max_tracks)
                    input("\nPress Enter to continue...")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    input("Press Enter to continue...")
            
            elif choice == 2:
                # Test download
                run_test()
            
            elif choice == 3:
                # Show help
                show_help()
                input("\nPress Enter to continue...")
            
            elif choice == 4:
                # Exit
                print("\n👋 Thanks for using NasmyTunes!")
                break
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please try again or report this issue.")

if __name__ == "__main__":
    main()