#!/usr/bin/env python3
"""
Test the advanced YouTube bypass system
"""
import tempfile
import os
from src.utils.advanced_youtube_bypass import AdvancedYouTubeBypass

def test_advanced_bypass():
    """Test the advanced bypass system"""
    print("🚀 Testing Advanced YouTube Bypass System")
    print("=" * 50)
    
    bypass = AdvancedYouTubeBypass()
    
    # Test tracks
    test_tracks = [
        ("Shape of You", ["Ed Sheeran"]),
        ("Blinding Lights", ["The Weeknd"]),
        ("Never Gonna Give You Up", ["Rick Astley"]),
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for track_name, artists in test_tracks:
            print(f"\n🎵 Testing: {track_name} by {', '.join(artists)}")
            print("-" * 40)
            
            try:
                success, message = bypass.download_with_advanced_bypass(
                    track_name, artists, temp_dir, max_attempts=1
                )
            except Exception as e:
                success = False
                message = f"Exception: {str(e)}"
            
            if success:
                print(f"✅ SUCCESS: {message}")
                # Check files
                files = os.listdir(temp_dir)
                audio_files = [f for f in files if any(ext in f.lower() for ext in ['.mp3', '.m4a', '.txt'])]
                print(f"   Files created: {audio_files}")
            else:
                print(f"❌ FAILED: {message}")
                # Create demo file as fallback
                demo_success, demo_message = bypass.create_enhanced_demo_file(
                    track_name, artists, temp_dir
                )
                if demo_success:
                    print(f"📝 Demo created: {demo_message}")
    
    print("\n" + "=" * 50)
    print("🏁 Advanced bypass test completed!")

if __name__ == "__main__":
    test_advanced_bypass()