#!/usr/bin/env python3
"""
Production startup script for NasmyTunes
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check required environment variables"""
    required_vars = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set these variables in your Render dashboard")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def main():
    """Main startup function"""
    logger.info("🚀 Starting NasmyTunes...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Import and run the app
    try:
        from app import app
        port = int(os.environ.get('PORT', 5001))
        logger.info(f"Starting server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()