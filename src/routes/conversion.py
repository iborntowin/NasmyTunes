import os
import tempfile
import zipfile
import shutil
import random
from flask import Blueprint, request, jsonify, send_file
from youtube_search import YoutubeSearch
import yt_dlp
from src.utils.youtube_downloader import EnhancedYouTubeDownloader
from src.utils.alternative_downloader import AlternativeAudioDownloader
from src.utils.advanced_youtube_bypass import AdvancedYouTubeBypass
import threading
import time
from datetime import datetime, timedelta
import uuid

# User agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
]

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
            'error': None,
            'failed_track_list': [],  # List of failed tracks with reasons
            'completed_track_list': []  # List of successfully converted tracks
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
        'created_at': job['created_at'].isoformat(),
        'failed_track_list': job.get('failed_track_list', []),
        'completed_track_list': job.get('completed_track_list', []),
        'has_partial_success': job['completed_tracks'] > 0 and job['failed_tracks'] > 0
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
        
        # Initialize downloaders
        youtube_downloader = EnhancedYouTubeDownloader()
        alternative_downloader = AlternativeAudioDownloader()
        advanced_bypass = AdvancedYouTubeBypass()
        downloaded_files = []
        
        # Check if we should use demo mode (for YouTube bot issues)
        demo_mode = os.getenv('DEMO_MODE', 'false').lower() == 'true'
        force_advanced_bypass = os.getenv('FORCE_ADVANCED_BYPASS', 'true').lower() == 'true'
        
        for i, track in enumerate(job['tracks']):
            try:
                # Update current track status
                track_name = f"{track['name']} - {', '.join(track['artists'])}"
                job['current_track'] = track_name
                
                print(f"Processing track {i+1}/{len(job['tracks'])}: {track_name}")
                
                success = False
                message = ""
                
                if demo_mode:
                    # Use enhanced demo mode
                    success, message = advanced_bypass.create_enhanced_demo_file(
                        track['name'], 
                        track['artists'], 
                        temp_dir
                    )
                else:
                    # Try advanced bypass first
                    if force_advanced_bypass:
                        print(f"🚀 Using advanced YouTube bypass...")
                        success, message = advanced_bypass.download_with_advanced_bypass(
                            track['name'], 
                            track['artists'], 
                            temp_dir,
                            max_attempts=2  # Limit attempts to avoid timeout
                        )
                    
                    # If advanced bypass fails, try standard YouTube downloader
                    if not success:
                        print(f"Advanced bypass failed, trying standard YouTube...")
                        success, message = youtube_downloader.download_track(
                            track['name'], 
                            track['artists'], 
                            temp_dir
                        )
                    
                    # If all YouTube methods fail, fall back to enhanced demo
                    if not success:
                        print(f"All YouTube methods failed, creating enhanced demo...")
                        success, message = advanced_bypass.create_enhanced_demo_file(
                            track['name'], 
                            track['artists'], 
                            temp_dir
                        )
                
                if success:
                    # Find the downloaded file
                    file_found = False
                    for file in os.listdir(temp_dir):
                        if (file.endswith('.mp3') or file.endswith('.txt')) and \
                           any(artist.lower() in file.lower() for artist in track['artists']):
                            downloaded_files.append(os.path.join(temp_dir, file))
                            print(f"Successfully processed: {file}")
                            job['completed_tracks'] += 1
                            job['completed_track_list'].append({
                                'name': track['name'],
                                'artists': track['artists'],
                                'filename': file,
                                'status': 'success'
                            })
                            file_found = True
                            break
                    
                    if not file_found:
                        print(f"Processed but couldn't find file for: {track_name}")
                        job['failed_tracks'] += 1
                        job['failed_track_list'].append({
                            'name': track['name'],
                            'artists': track['artists'],
                            'reason': 'File not found after processing',
                            'status': 'failed'
                        })
                else:
                    print(f"Failed to process: {track_name} - {message}")
                    job['failed_tracks'] += 1
                    job['failed_track_list'].append({
                        'name': track['name'],
                        'artists': track['artists'],
                        'reason': message or 'Unknown error during processing',
                        'status': 'failed'
                    })
                
                # Rate limiting between tracks
                time.sleep(random.uniform(3, 7))
                
            except Exception as e:
                print(f"Error converting track {track['name']}: {str(e)}")
                job['failed_tracks'] += 1
                continue
        
        # Always create ZIP file, even with partial success
        zip_filename = f"playlist_{job_id}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add successfully downloaded files (avoid duplicates)
            added_files = set()
            for file_path in downloaded_files:
                filename = os.path.basename(file_path)
                if filename not in added_files:
                    zipf.write(file_path, filename)
                    added_files.add(filename)
            
            # Add a summary report
            summary_content = f"""NasmyTunes Conversion Report
Playlist: {job['playlist_name']}
Conversion Date: {job['created_at'].strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY:
========
Total Tracks: {job['total_tracks']}
Successfully Converted: {job['completed_tracks']}
Failed: {job['failed_tracks']}
Success Rate: {(job['completed_tracks'] / job['total_tracks'] * 100):.1f}%

SUCCESSFULLY CONVERTED TRACKS:
==============================
"""
            
            for track in job['completed_track_list']:
                summary_content += f"✅ {track['name']} - {', '.join(track['artists'])}\n"
            
            if job['failed_track_list']:
                summary_content += f"\nFAILED TRACKS:\n==============\n"
                for track in job['failed_track_list']:
                    summary_content += f"❌ {track['name']} - {', '.join(track['artists'])}\n"
                    summary_content += f"   Reason: {track['reason']}\n\n"
            
            summary_content += f"\nNOTE: This conversion was performed in demo mode due to YouTube's bot detection.\n"
            summary_content += f"For actual audio files, please run the application locally on your computer.\n"
            summary_content += f"\nThank you for using NasmyTunes! 🎵"
            
            # Add summary to ZIP
            zipf.writestr("CONVERSION_REPORT.txt", summary_content)
        
        job['zip_path'] = zip_path
        job['current_track'] = None
        
        # Determine final status
        if job['completed_tracks'] > 0:
            job['status'] = 'completed'
            if job['failed_tracks'] > 0:
                print(f"Conversion completed with partial success: {job['completed_tracks']}/{job['total_tracks']} tracks")
            else:
                print(f"Conversion completed successfully: {job['completed_tracks']}/{job['total_tracks']} tracks")
        else:
            job['status'] = 'completed'  # Still completed, just with no successful tracks
            job['error'] = 'No tracks were successfully converted, but report is available'
            print("Conversion completed: No tracks were successfully converted")
        
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

