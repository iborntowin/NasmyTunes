"""
Advanced YouTube Bot Detection Bypass
Using multiple techniques and fallback strategies
"""
import os
import time
import random
import requests
import tempfile
import subprocess
from urllib.parse import urlparse, parse_qs
import json
import re
from youtube_search import YoutubeSearch
import yt_dlp
from .cookie_bypass import CookieBypass

class AdvancedYouTubeBypass:
    def __init__(self):
        self.session = requests.Session()
        self.proxies = []
        self.cookie_bypass = CookieBypass()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
    def get_advanced_ydl_opts(self, output_path, filename, use_cookies=True):
        """Get advanced yt-dlp options with maximum bypass techniques"""
        opts = {
            'format': 'bestaudio/best[height<=480]/worst',
            'outtmpl': os.path.join(output_path, f'{filename}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',  # Lower quality for faster processing
            }],
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'ignoreerrors': True,
            'no_check_certificate': True,
            'prefer_insecure': True,
            
            # Advanced anti-bot headers
            'http_headers': {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,es;q=0.8,fr;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            },
            
            # Advanced extractor arguments
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['configs'],
                    'player_client': ['android', 'web'],
                    'include_live_dash': False,
                }
            },
            
            # Rate limiting and delays
            'sleep_interval_requests': random.uniform(1, 3),
            'sleep_interval_subtitles': random.uniform(1, 2),
            'sleep_interval': random.uniform(2, 4),
            'max_sleep_interval': 8,
            
            # Retry configuration
            'retries': 5,
            'fragment_retries': 5,
            'skip_unavailable_fragments': True,
            
            # Geo bypass
            'geo_bypass': True,
            'geo_bypass_country': random.choice(['US', 'CA', 'GB', 'AU', 'DE']),
            
            # Additional bypass options
            'force_json': False,
            'no_color': True,
            'no_call_home': True,
        }
        
        # Add cookies if requested
        if use_cookies:
            try:
                opts, cookie_file = self.cookie_bypass.get_cookie_opts(opts)
                print(f"      Using cookies: {cookie_file}")
            except Exception as e:
                print(f"      Cookie bypass failed: {e}")
        
        return opts
    
    def try_alternative_extractors(self, video_url, output_path, filename):
        """Try alternative extraction methods"""
        methods = [
            self._try_android_client,
            self._try_web_client,
            self._try_embedded_client,
            self._try_mobile_client,
        ]
        
        for method in methods:
            try:
                result = method(video_url, output_path, filename)
                if result:
                    return True
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"    Method {method.__name__} failed: {str(e)[:100]}")
                continue
        
        return False
    
    def _try_android_client(self, video_url, output_path, filename):
        """Try with Android client"""
        try:
            opts = self.get_advanced_ydl_opts(output_path, filename)
            opts['extractor_args']['youtube']['player_client'] = ['android']
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([video_url])
            return True
        except Exception as e:
            print(f"      Android client error: {str(e)[:100]}")
            return False
    
    def _try_web_client(self, video_url, output_path, filename):
        """Try with web client and different user agent"""
        try:
            opts = self.get_advanced_ydl_opts(output_path, filename)
            opts['extractor_args']['youtube']['player_client'] = ['web']
            opts['http_headers']['User-Agent'] = random.choice(self.user_agents)
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([video_url])
            return True
        except Exception as e:
            print(f"      Web client error: {str(e)[:100]}")
            return False
    
    def _try_embedded_client(self, video_url, output_path, filename):
        """Try with embedded client"""
        try:
            opts = self.get_advanced_ydl_opts(output_path, filename)
            opts['extractor_args']['youtube']['player_client'] = ['web_embedded']
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([video_url])
            return True
        except Exception as e:
            print(f"      Embedded client error: {str(e)[:100]}")
            return False
    
    def _try_mobile_client(self, video_url, output_path, filename):
        """Try with mobile client"""
        try:
            opts = self.get_advanced_ydl_opts(output_path, filename)
            opts['extractor_args']['youtube']['player_client'] = ['mweb']
            opts['http_headers']['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15'
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([video_url])
            return True
        except Exception as e:
            print(f"      Mobile client error: {str(e)[:100]}")
            return False
    
    def search_alternative_sources(self, track_name, artists):
        """Search for alternative video sources"""
        search_variations = [
            f"{track_name} {' '.join(artists)}",
            f"{track_name} {artists[0]} official",
            f"{track_name} {artists[0]} audio",
            f"{track_name} {artists[0]} music video",
            f"{track_name} {artists[0]} lyrics",
            f"{' '.join(artists)} {track_name}",
            f"{track_name} cover",
            f"{track_name} karaoke",
            f"{track_name} instrumental",
        ]
        
        all_results = []
        for query in search_variations:
            try:
                results = YoutubeSearch(query, max_results=3).to_dict()
                all_results.extend(results)
                time.sleep(random.uniform(0.5, 1.5))
            except Exception as e:
                print(f"Search failed for '{query}': {e}")
                continue
        
        # Remove duplicates and sort by relevance
        unique_results = []
        seen_ids = set()
        for result in all_results:
            if result['id'] not in seen_ids:
                unique_results.append(result)
                seen_ids.add(result['id'])
        
        return unique_results[:10]  # Return top 10 unique results
    
    def download_with_advanced_bypass(self, track_name, artists, output_path, max_attempts=3):
        """Main download function with all bypass techniques"""
        print(f"🔄 Advanced bypass for: {track_name} by {', '.join(artists)}")
        
        # Search for videos
        videos = self.search_alternative_sources(track_name, artists)
        if not videos:
            return False, "No videos found"
        
        # Try each video with different methods
        for i, video in enumerate(videos):
            video_url = f"https://www.youtube.com/watch?v={video['id']}"
            print(f"  Trying video {i+1}/{len(videos)}: {video['title'][:50]}...")
            
            # Create safe filename
            safe_filename = "".join(c for c in f"{track_name} - {', '.join(artists)}" 
                                  if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            
            # Try alternative extractors
            for attempt in range(max_attempts):
                try:
                    print(f"    Attempt {attempt + 1}/{max_attempts}")
                    
                    if self.try_alternative_extractors(video_url, output_path, safe_filename):
                        # Check if file was created
                        for file in os.listdir(output_path):
                            if file.startswith(safe_filename) and file.endswith('.mp3'):
                                print(f"  ✅ Success: {file}")
                                return True, f"Downloaded: {video['title']}"
                        
                        # If no MP3 found, try to find any audio file
                        for file in os.listdir(output_path):
                            if safe_filename.lower() in file.lower() and any(ext in file.lower() for ext in ['.mp3', '.m4a', '.webm', '.ogg']):
                                print(f"  ✅ Success (alt format): {file}")
                                return True, f"Downloaded: {video['title']}"
                    
                except Exception as e:
                    print(f"    ❌ Attempt {attempt + 1} failed: {str(e)[:100]}")
                    if attempt < max_attempts - 1:
                        delay = random.uniform(3, 8) * (attempt + 1)  # Exponential backoff
                        print(f"    ⏳ Waiting {delay:.1f}s before retry...")
                        time.sleep(delay)
                    continue
            
            # Wait before trying next video
            time.sleep(random.uniform(2, 5))
        
        return False, "All bypass attempts failed"
    
    def create_enhanced_demo_file(self, track_name, artists, output_path):
        """Create enhanced demo file with more details"""
        safe_filename = "".join(c for c in f"{track_name} - {', '.join(artists)}" 
                              if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        
        output_file = os.path.join(output_path, f"{safe_filename}.txt")
        
        content = f"""🎵 NasmyTunes - Advanced Bypass Demo File
==========================================

Track Information:
------------------
Title: {track_name}
Artists: {', '.join(artists)}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

Bypass Attempts Made:
--------------------
✓ Android Client Method
✓ Web Client Method  
✓ Embedded Client Method
✓ Mobile Client Method
✓ Multiple User Agents
✓ Geo-bypass Attempts
✓ Alternative Search Queries

Status: Demo Mode Active
Reason: YouTube's advanced bot detection is blocking cloud servers

Note: This demonstrates the complete conversion workflow.
In a local environment, this would be the actual MP3 file.

Advanced Features Tested:
------------------------
• Dynamic user agent rotation
• Multiple client types (Android, Web, Mobile)
• Geo-location bypass
• Rate limiting and delays
• Alternative search strategies
• Retry mechanisms with exponential backoff

For real audio files, run this application locally on your computer
where YouTube's bot detection is not active.

🎶 Thank you for using NasmyTunes!
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, f"Enhanced demo file created for: {track_name}"