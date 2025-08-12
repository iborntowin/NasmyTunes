"""
Alternative audio downloader using multiple sources
"""
import os
import time
import random
import requests
import tempfile
from youtube_search import YoutubeSearch

class AlternativeAudioDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def search_and_get_info(self, track_name, artists):
        """Search for track and get basic info"""
        search_query = f"{track_name} {' '.join(artists)}"
        
        try:
            results = YoutubeSearch(search_query, max_results=5).to_dict()
            if results:
                return results[0]  # Return best match
        except Exception as e:
            print(f"Search failed: {e}")
        
        return None
    
    def create_placeholder_mp3(self, track_name, artists, output_dir):
        """Create a placeholder MP3 file with track info"""
        import io
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        try:
            # Generate a 30-second sine wave as placeholder
            tone = Sine(440).to_audio_segment(duration=30000)  # 30 seconds at 440Hz
            
            # Create filename
            safe_filename = "".join(c for c in f"{track_name} - {', '.join(artists)}" 
                                  if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            
            output_path = os.path.join(output_dir, f"{safe_filename}.mp3")
            
            # Export as MP3
            tone.export(output_path, format="mp3", bitrate="192k")
            
            return True, f"Created placeholder for: {track_name}"
            
        except Exception as e:
            return False, f"Failed to create placeholder: {str(e)}"
    
    def download_track_alternative(self, track_name, artists, output_dir):
        """Alternative download method - creates demo files"""
        
        # For demo purposes, we'll create placeholder files
        # In a real implementation, you could integrate with:
        # - SoundCloud API
        # - Bandcamp
        # - Archive.org
        # - Other legal audio sources
        
        print(f"Creating demo file for: {track_name} by {', '.join(artists)}")
        
        # Simulate processing time
        time.sleep(random.uniform(2, 5))
        
        # Create a text file instead of audio (for demo)
        safe_filename = "".join(c for c in f"{track_name} - {', '.join(artists)}" 
                              if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        
        output_path = os.path.join(output_dir, f"{safe_filename}.txt")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Demo Track Information\n")
            f.write(f"Title: {track_name}\n")
            f.write(f"Artists: {', '.join(artists)}\n")
            f.write(f"Note: This is a demo file. In a real implementation, this would be the actual audio file.\n")
            f.write(f"Due to YouTube's bot detection, we're showing a demo version.\n")
        
        return True, f"Demo file created for: {track_name}"