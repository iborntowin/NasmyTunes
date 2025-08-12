"""
Deployment entry point for Spotify to MP3 Converter
"""
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import deployment configuration
try:
    import deployment_config
except ImportError:
    pass

# Import the Flask app
from main import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)

