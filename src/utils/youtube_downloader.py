"""
Enhanced YouTube downloader with anti-bot measures
"""
import os
import time
import random
import yt_dlp
from youtube_search import YoutubeSearch

class EnhancedYouTubeDownloader:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        ]
    
    def get_ydl_opts(self, output_path, filename):
        """Get yt-dlp options with anti-bot measures"""
        ffmpeg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ffmpeg', 'ffmpeg.exe')
        return {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, f'{filename}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': ffmpeg_path,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'ignoreerrors': True,
            'http_headers': {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['configs'],
                }
            },
            'sleep_interval_requests': 1,
            'sleep_interval_subtitles': 1,
            'sleep_interval': 1,
            'max_sleep_interval': 5,
        }
    
    def search_youtube(self, query, max_results=5):
        """Search YouTube with multiple fallbacks"""
        search_variations = [
            query,
            f"{query} official",
            f"{query} audio",
            f"{query} music",
            query.replace(" - ", " "),
        ]
        
        for search_query in search_variations:
            try:
                results = YoutubeSearch(search_query, max_results=max_results).to_dict()
                if results:
                    return results
            except Exception as e:
                print(f"Search failed for '{search_query}': {e}")
                continue
        
        return []
    
    def download_track(self, track_name, artists, output_dir, max_retries=3):
        """Download a track with enhanced error handling"""
        # Create search query
        search_query = f"{track_name} {' '.join(artists)}"
        
        # Search for videos
        videos = self.search_youtube(search_query)
        if not videos:
            return False, "No videos found"
        
        # Try each video until one works
        for video in videos:
            video_url = f"https://www.youtube.com/watch?v={video['id']}"
            
            # Create safe filename
            safe_filename = "".join(c for c in f"{track_name} - {', '.join(artists)}" 
                                  if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            
            # Try downloading with retries
            for attempt in range(max_retries):
                try:
                    ydl_opts = self.get_ydl_opts(output_dir, safe_filename)
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    
                    # Check if file was created
                    for file in os.listdir(output_dir):
                        if file.startswith(safe_filename) and file.endswith('.mp3'):
                            return True, f"Downloaded: {video['title']}"
                    
                except Exception as e:
                    print(f"Download attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(random.uniform(2, 5))
                    continue
            
            # Wait before trying next video
            time.sleep(random.uniform(1, 3))
        
        return False, "All download attempts failed"