import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

load_dotenv()

spotify_bp = Blueprint('spotify', __name__)

# Initialize Spotify client with error handling
try:
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("Warning: Spotify credentials not found in environment variables")
        sp = None
    else:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
except Exception as e:
    print(f"Error initializing Spotify client: {str(e)}")
    sp = None

@spotify_bp.route('/playlist', methods=['POST'])
def get_playlist():
    """Extract playlist information from Spotify URL"""
    try:
        if sp is None:
            return jsonify({'error': 'Spotify API not configured. Please check environment variables.'}), 500
        
        data = request.get_json()
        playlist_url = data.get('playlist_url')
        
        if not playlist_url:
            return jsonify({'error': 'Playlist URL is required'}), 400
        
        # Extract playlist ID from URL
        playlist_id = extract_playlist_id(playlist_url)
        if not playlist_id:
            return jsonify({'error': 'Invalid Spotify playlist URL'}), 400
        
        print(f"Attempting to fetch playlist: {playlist_id}")
        
        # Get playlist information with better error handling
        try:
            playlist = sp.playlist(playlist_id)
        except Exception as playlist_error:
            print(f"Playlist fetch error: {str(playlist_error)}")
            return jsonify({
                'error': f'Could not access playlist. Please ensure the playlist is public and the URL is correct. Error: {str(playlist_error)}'
            }), 404
        
        tracks = []
        
        # Get all tracks from the playlist
        try:
            results = sp.playlist_tracks(playlist_id)
            while results:
                for item in results['items']:
                    if item['track'] and item['track']['type'] == 'track':
                        track = item['track']
                        tracks.append({
                            'id': track['id'],
                            'name': track['name'],
                            'artists': [artist['name'] for artist in track['artists']],
                            'duration_ms': track['duration_ms'],
                            'preview_url': track['preview_url']
                        })
                
                # Check if there are more tracks
                if results['next']:
                    results = sp.next(results)
                else:
                    results = None
        except Exception as tracks_error:
            print(f"Tracks fetch error: {str(tracks_error)}")
            return jsonify({
                'error': f'Could not fetch playlist tracks: {str(tracks_error)}'
            }), 500
        
        return jsonify({
            'playlist_id': playlist_id,
            'name': playlist['name'],
            'description': playlist['description'],
            'total_tracks': len(tracks),
            'tracks': tracks
        })
        
    except Exception as e:
        print(f"General error in get_playlist: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

def extract_playlist_id(url):
    """Extract playlist ID from Spotify URL"""
    try:
        # Handle different Spotify URL formats
        if 'open.spotify.com/playlist/' in url:
            return url.split('playlist/')[1].split('?')[0]
        elif 'spotify:playlist:' in url:
            return url.split('playlist:')[1]
        else:
            return None
    except:
        return None

@spotify_bp.route('/track/<track_id>', methods=['GET'])
def get_track(track_id):
    """Get detailed information about a specific track"""
    try:
        if sp is None:
            return jsonify({'error': 'Spotify API not configured. Please check environment variables.'}), 500
            
        track = sp.track(track_id)
        return jsonify({
            'id': track['id'],
            'name': track['name'],
            'artists': [artist['name'] for artist in track['artists']],
            'album': track['album']['name'],
            'duration_ms': track['duration_ms'],
            'preview_url': track['preview_url'],
            'external_urls': track['external_urls']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

