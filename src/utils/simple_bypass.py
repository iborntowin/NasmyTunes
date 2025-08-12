"""
Simplified but effective YouTube bypass
"""
import os
import time
import random
import tempfile
import yt_dlp
from youtube_search import YoutubeSearch

class SimpleBypass:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
    
    def get_simple_opts(self, output_path, filename):
        """Get simplified but effective yt-dlp options"""
        return {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': os.path.join(output_path, f'{filename}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'http_headers': {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'skip': ['dash'],
                }
            },
            'sleep_interval': random.uniform(1, 3),
            'retries': 3,
            'geo_bypass': True,
        }
    
    def search_youtube_simple(self, track_name, artists):
        """Simple YouTube search"""
        queries = [
            f"{track_name} {' '.join(artists)}",
            f"{track_name} {artists[0]} official",
            f"{track_name} {artists[0]} audio"
        ]
        
        for query in queries:
            try:
                results = YoutubeSearch(query, max_results=2).to_dict()
                if results:
                    return results
                time.sleep(1)
            except Exception as e:
                print(f"Search failed for '{query}': {e}")
                continue
        
        return []
    
    def download_simple(self, track_name, artists, output_path):
        """Simple download with basic bypass"""
        print(f"🎵 Simple bypass: {track_name} by {', '.join(artists)}")
        
        # Search for videos
        videos = self.search_youtube_simple(track_name, artists)
        if not videos:
            return False, "No videos found"
        
        # Try each video
        for video in videos:
            video_url = f"https://www.youtube.com/watch?v={video['id']}"
            safe_filename = "".join(c for c in f"{track_name} - {', '.join(artists)}" 
                                  if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            
            print(f"  Trying: {video['title'][:50]}...")
            
            try:
                opts = self.get_simple_opts(output_path, safe_filename)
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([video_url])
                
                # Check if file was created
                for file in os.listdir(output_path):
                    if safe_filename.lower() in file.lower() and file.endswith('.mp3'):
                        print(f"  ✅ Success: {file}")
                        return True, f"Downloaded: {video['title']}"
                
            except Exception as e:
                print(f"  ❌ Failed: {str(e)[:100]}")
                continue
            
            time.sleep(random.uniform(2, 4))
        
        return False, "All attempts failed"
    
    def create_demo_file(self, track_name, artists, output_path):
        """Create a simple demo file"""
        safe_filename = "".join(c for c in f"{track_name} - {', '.join(artists)}" 
                              if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        
        output_file = os.path.join(output_path, f"{safe_filename}.txt")
        
        content = f"""🎵 NasmyTunes Demo File
====================

Track: {track_name}
Artists: {', '.join(artists)}
Status: Demo Mode (YouTube blocked)

This file demonstrates the conversion process.
For actual MP3 files, run locally on your computer.

🎶 Thank you for using NasmyTunes!
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, f"Demo file created for: {track_name}"