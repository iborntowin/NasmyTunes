"""
Deployment configuration for Spotify to MP3 Converter
"""
import os

# Environment variables for deployment
DEPLOYMENT_ENV = {
    'SPOTIFY_CLIENT_ID': 'c10a2cbeea0e4b558ee1aef44463f936',
    'SPOTIFY_CLIENT_SECRET': '97c90533b4b246cf9c7799d6cf49056f',
    'GENIUS_ACCESS_TOKEN': 'JUrrHKWrKxHAJTu3b8yY2-c4ZV7xKhHHBrduFOyE4gOMAAhXN7BCMwec2CXqArAx',
    'MUSIXMATCH_API_KEY': 'placeholder_musixmatch_api_key_here',
    'FLASK_ENV': 'production',
    'SECRET_KEY': 'spotify-mp3-converter-secret-key-2024'
}

def configure_environment():
    """Configure environment variables for deployment"""
    for key, value in DEPLOYMENT_ENV.items():
        os.environ[key] = value

# Call configuration on import
configure_environment()

