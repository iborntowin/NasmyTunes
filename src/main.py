import os
import sys
import subprocess
from dotenv import load_dotenv

# Environment variables loaded via .env file

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.spotify import spotify_bp
from src.routes.youtube import youtube_bp
from src.routes.conversion import conversion_bp

# Load environment variables
load_dotenv()

# Check FFmpeg availability
def check_ffmpeg():
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, text=True)
        print("✅ FFmpeg is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ FFmpeg not found: {e}")
        print("Audio conversion may fail without FFmpeg")
        return False

# Check on startup (non-blocking)
try:
    ffmpeg_available = check_ffmpeg()
except Exception as e:
    print(f"FFmpeg check failed: {e}")
    ffmpeg_available = False

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(spotify_bp, url_prefix='/api/spotify')
app.register_blueprint(youtube_bp, url_prefix='/api/youtube')
app.register_blueprint(conversion_bp, url_prefix='/api/convert')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return {
        'status': 'healthy',
        'service': 'nasmytunes',
        'version': '1.0.0'
    }

@app.route('/test-conversion')
def test_conversion():
    """Test endpoint with guaranteed working songs"""
    test_tracks = [
        {
            "name": "Shape of You",
            "artists": ["Ed Sheeran"],
            "duration_ms": 233713
        },
        {
            "name": "Blinding Lights",
            "artists": ["The Weeknd"],
            "duration_ms": 200040
        },
        {
            "name": "Levitating",
            "artists": ["Dua Lipa"],
            "duration_ms": 203064
        }
    ]
    
    return {
        "message": "Test playlist with guaranteed working songs",
        "playlist_name": "Test Conversion",
        "total_tracks": len(test_tracks),
        "tracks": test_tracks,
        "instructions": "Use the /api/convert/start endpoint with this data"
    }

@app.route('/debug')
def debug_info():
    """Debug endpoint to check system status"""
    import shutil
    debug_data = {
        'ffmpeg_available': shutil.which('ffmpeg') is not None,
        'ffmpeg_path': shutil.which('ffmpeg'),
        'python_version': sys.version,
        'environment': os.environ.get('FLASK_ENV', 'unknown'),
        'spotify_configured': bool(os.getenv('SPOTIFY_CLIENT_ID')),
        'port': os.environ.get('PORT', '5001'),
        'demo_mode': os.getenv('DEMO_MODE', 'false').lower() == 'true',
        'app_status': 'running'
    }
    return debug_data

@app.route('/demo-info')
def demo_info():
    """Show demo mode information page"""
    return send_from_directory(app.static_folder, 'demo-notice.html')

@app.route('/toggle-demo')
def toggle_demo():
    """Toggle demo mode for testing"""
    current_mode = os.getenv('DEMO_MODE', 'false').lower() == 'true'
    new_mode = not current_mode
    os.environ['DEMO_MODE'] = 'true' if new_mode else 'false'
    
    return {
        'demo_mode': new_mode,
        'message': f"Demo mode {'enabled' if new_mode else 'disabled'}",
        'note': 'Demo mode creates placeholder files instead of downloading from YouTube'
    }

@app.route('/test-bypass')
def test_bypass():
    """Test the advanced YouTube bypass"""
    import tempfile
    from src.utils.advanced_youtube_bypass import AdvancedYouTubeBypass
    
    bypass = AdvancedYouTubeBypass()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        success, message = bypass.download_with_advanced_bypass(
            "Never Gonna Give You Up", 
            ["Rick Astley"], 
            temp_dir,
            max_attempts=1
        )
        
        files_created = []
        if os.path.exists(temp_dir):
            files_created = os.listdir(temp_dir)
        
        return {
            'bypass_test': 'completed',
            'success': success,
            'message': message,
            'files_created': files_created,
            'advanced_bypass_active': os.getenv('FORCE_ADVANCED_BYPASS', 'false').lower() == 'true'
        }

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
