import os
import tempfile
import zipfile
from flask import Blueprint, request, jsonify, send_file
from youtube_search import YoutubeSearch
import yt_dlp
import threading
import time
from datetime import datetime

youtube_bp = Blueprint('youtube', __name__)

# Store conversion jobs in memory (in production, use Redis or database)
conversion_jobs = {}

@youtube_bp.route('/search', methods=['POST'])
def search_youtube():
    """Search for a track on YouTube"""
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Search for videos
        results = YoutubeSearch(query, max_results=5).to_dict()
        
        videos = []
        for video in results:
            videos.append({
                'id': video['id'],
                'title': video['title'],
                'duration': video['duration'],
                'views': video['views'],
                'channel': video['channel'],
                'url': f"https://www.youtube.com/watch?v={video['id']}",
                'thumbnail': video['thumbnails'][0] if video['thumbnails'] else None
            })
        
        return jsonify({'videos': videos})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/convert', methods=['POST'])
def convert_playlist():
    """Start conversion process for a playlist"""
    try:
        data = request.get_json()
        tracks = data.get('tracks', [])
        job_id = data.get('job_id', str(int(time.time())))
        
        if not tracks:
            return jsonify({'error': 'No tracks provided'}), 400
        
        # Initialize job status
        conversion_jobs[job_id] = {
            'status': 'started',
            'total_tracks': len(tracks),
            'completed_tracks': 0,
            'failed_tracks': 0,
            'current_track': None,
            'download_url': None,
            'created_at': datetime.now(),
            'tracks': tracks
        }
        
        # Start conversion in background thread
        thread = threading.Thread(target=convert_tracks_background, args=(job_id, tracks))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'started',
            'message': 'Conversion process started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@youtube_bp.route('/status/<job_id>', methods=['GET'])
def get_conversion_status(job_id):
    """Get the status of a conversion job"""
    if job_id not in conversion_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = conversion_jobs[job_id]
    return jsonify({
        'job_id': job_id,
        'status': job['status'],
        'total_tracks': job['total_tracks'],
        'completed_tracks': job['completed_tracks'],
        'failed_tracks': job['failed_tracks'],
        'current_track': job['current_track'],
        'download_url': job['download_url'],
        'progress': (job['completed_tracks'] / job['total_tracks']) * 100 if job['total_tracks'] > 0 else 0
    })

@youtube_bp.route('/download/<job_id>', methods=['GET'])
def download_zip(job_id):
    """Download the converted tracks as a ZIP file"""
    if job_id not in conversion_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = conversion_jobs[job_id]
    if job['status'] != 'completed' or not job['download_url']:
        return jsonify({'error': 'Conversion not completed or file not available'}), 400
    
    try:
        return send_file(job['download_url'], as_attachment=True, download_name=f'playlist_{job_id}.zip')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def convert_tracks_background(job_id, tracks):
    """Background function to convert tracks"""
    try:
        job = conversion_jobs[job_id]
        job['status'] = 'processing'
        
        # Create temporary directory for downloads
        temp_dir = tempfile.mkdtemp()
        downloaded_files = []
        
        for i, track in enumerate(tracks):
            try:
                job['current_track'] = f"{track['name']} - {', '.join(track['artists'])}"
                
                # Search for the track on YouTube
                search_query = f"{track['name']} {' '.join(track['artists'])}"
                results = YoutubeSearch(search_query, max_results=1).to_dict()
                
                if not results:
                    job['failed_tracks'] += 1
                    continue
                
                video_url = f"https://www.youtube.com/watch?v={results[0]['id']}"
                
                # Download and convert to MP3
                ffmpeg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg', 'ffmpeg.exe')
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(temp_dir, f'{i+1:02d}. %(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'ffmpeg_location': ffmpeg_path,
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Find the downloaded file
                for file in os.listdir(temp_dir):
                    if file.endswith('.mp3') and file.startswith(f'{i+1:02d}.'):
                        downloaded_files.append(os.path.join(temp_dir, file))
                        break
                
                job['completed_tracks'] += 1
                
            except Exception as e:
                print(f"Error converting track {track['name']}: {str(e)}")
                job['failed_tracks'] += 1
        
        # Create ZIP file
        if downloaded_files:
            zip_path = os.path.join(temp_dir, f'playlist_{job_id}.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in downloaded_files:
                    zipf.write(file_path, os.path.basename(file_path))
            
            job['download_url'] = zip_path
            job['status'] = 'completed'
        else:
            job['status'] = 'failed'
            job['error'] = 'No tracks were successfully converted'
        
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)

