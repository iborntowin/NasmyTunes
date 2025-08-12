import os
import tempfile
import zipfile
import shutil
from flask import Blueprint, request, jsonify, send_file
from youtube_search import YoutubeSearch
import yt_dlp
import threading
import time
from datetime import datetime, timedelta
import uuid

conversion_bp = Blueprint('conversion', __name__)

# Store conversion jobs in memory (in production, use Redis or database)
conversion_jobs = {}

@conversion_bp.route('/start', methods=['POST'])
def start_conversion():
    """Start conversion process for a playlist"""
    try:
        data = request.get_json()
        tracks = data.get('tracks', [])
        playlist_name = data.get('playlist_name', 'Playlist')
        
        if not tracks:
            return jsonify({'error': 'No tracks provided'}), 400
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        conversion_jobs[job_id] = {
            'status': 'queued',
            'playlist_name': playlist_name,
            'total_tracks': len(tracks),
            'completed_tracks': 0,
            'failed_tracks': 0,
            'current_track': None,
            'download_url': None,
            'created_at': datetime.now(),
            'tracks': tracks,
            'temp_dir': None,
            'zip_path': None,
            'error': None
        }
        
        # Start conversion in background thread
        thread = threading.Thread(target=convert_tracks_background, args=(job_id,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'message': 'Conversion process started',
            'total_tracks': len(tracks)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversion_bp.route('/status/<job_id>', methods=['GET'])
def get_conversion_status(job_id):
    """Get the status of a conversion job"""
    if job_id not in conversion_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = conversion_jobs[job_id]
    
    # Calculate progress percentage
    progress = 0
    if job['total_tracks'] > 0:
        progress = (job['completed_tracks'] / job['total_tracks']) * 100
    
    return jsonify({
        'job_id': job_id,
        'status': job['status'],
        'playlist_name': job['playlist_name'],
        'total_tracks': job['total_tracks'],
        'completed_tracks': job['completed_tracks'],
        'failed_tracks': job['failed_tracks'],
        'current_track': job['current_track'],
        'progress': round(progress, 1),
        'download_ready': job['status'] == 'completed' and job['zip_path'] is not None,
        'error': job.get('error'),
        'created_at': job['created_at'].isoformat()
    })

@conversion_bp.route('/download/<job_id>', methods=['GET'])
def download_zip(job_id):
    """Download the converted tracks as a ZIP file"""
    if job_id not in conversion_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = conversion_jobs[job_id]
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Conversion not completed'}), 400
    
    if not job['zip_path'] or not os.path.exists(job['zip_path']):
        return jsonify({'error': 'Download file not available'}), 404
    
    try:
        # Generate a clean filename
        safe_name = "".join(c for c in job['playlist_name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name or 'playlist'}_{job_id[:8]}.zip"
        
        return send_file(
            job['zip_path'], 
            as_attachment=True, 
            download_name=filename,
            mimetype='application/zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversion_bp.route('/cleanup/<job_id>', methods=['DELETE'])
def cleanup_job(job_id):
    """Clean up job files and remove from memory"""
    if job_id not in conversion_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = conversion_jobs[job_id]
    
    try:
        # Clean up temporary directory
        if job['temp_dir'] and os.path.exists(job['temp_dir']):
            shutil.rmtree(job['temp_dir'])
        
        # Remove job from memory
        del conversion_jobs[job_id]
        
        return jsonify({'message': 'Job cleaned up successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def convert_tracks_background(job_id):
    """Background function to convert tracks"""
    job = conversion_jobs[job_id]
    
    try:
        job['status'] = 'processing'
        
        # Create temporary directory for downloads
        temp_dir = tempfile.mkdtemp(prefix=f'spotify_converter_{job_id}_')
        job['temp_dir'] = temp_dir
        
        downloaded_files = []
        
        for i, track in enumerate(job['tracks']):
            try:
                # Update current track status
                track_name = f"{track['name']} - {', '.join(track['artists'])}"
                job['current_track'] = track_name
                
                print(f"Processing track {i+1}/{len(job['tracks'])}: {track_name}")
                
                # Search for the track on YouTube
                search_query = f"{track['name']} {' '.join(track['artists'])}"
                results = YoutubeSearch(search_query, max_results=1).to_dict()
                
                if not results:
                    print(f"No YouTube results for: {search_query}")
                    job['failed_tracks'] += 1
                    continue
                
                video_url = f"https://www.youtube.com/watch?v={results[0]['id']}"
                print(f"Found video: {results[0]['title']}")
                
                # Create safe filename
                safe_filename = "".join(c for c in f"{i+1:02d}. {track['name']} - {', '.join(track['artists'])}" 
                                      if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                
                # Download and convert to MP3
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(temp_dir, f'{safe_filename}.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # Find the downloaded MP3 file
                for file in os.listdir(temp_dir):
                    if file.startswith(safe_filename) and file.endswith('.mp3'):
                        downloaded_files.append(os.path.join(temp_dir, file))
                        print(f"Successfully converted: {file}")
                        break
                
                job['completed_tracks'] += 1
                
            except Exception as e:
                print(f"Error converting track {track['name']}: {str(e)}")
                job['failed_tracks'] += 1
                continue
        
        # Create ZIP file if we have any successful downloads
        if downloaded_files:
            zip_filename = f"playlist_{job_id}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in downloaded_files:
                    # Add file to zip with just the filename (no path)
                    zipf.write(file_path, os.path.basename(file_path))
            
            job['zip_path'] = zip_path
            job['status'] = 'completed'
            job['current_track'] = None
            
            print(f"Conversion completed! Created ZIP with {len(downloaded_files)} files")
            
        else:
            job['status'] = 'failed'
            job['error'] = 'No tracks were successfully converted'
            print("Conversion failed: No tracks were successfully converted")
        
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)
        print(f"Conversion failed with error: {str(e)}")

# Cleanup old jobs periodically (in production, use a proper job scheduler)
def cleanup_old_jobs():
    """Remove jobs older than 24 hours"""
    cutoff_time = datetime.now() - timedelta(hours=24)
    jobs_to_remove = []
    
    for job_id, job in conversion_jobs.items():
        if job['created_at'] < cutoff_time:
            jobs_to_remove.append(job_id)
    
    for job_id in jobs_to_remove:
        try:
            job = conversion_jobs[job_id]
            if job['temp_dir'] and os.path.exists(job['temp_dir']):
                shutil.rmtree(job['temp_dir'])
            del conversion_jobs[job_id]
            print(f"Cleaned up old job: {job_id}")
        except Exception as e:
            print(f"Error cleaning up job {job_id}: {str(e)}")

# Start cleanup thread
cleanup_thread = threading.Thread(target=lambda: [time.sleep(3600), cleanup_old_jobs()])
cleanup_thread.daemon = True
cleanup_thread.start()

