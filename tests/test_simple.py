#!/usr/bin/env python3
"""
Simple test to verify the Spotify to MP3 converter application works
"""
import requests
import time
import sys

def test_server_health():
    """Test if the server is responding"""
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        print(f"✅ Server is responding with status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Server health check failed: {str(e)}")
        return False

def test_spotify_api():
    """Test Spotify API integration"""
    try:
        # Use a known public playlist
        test_data = {
            "playlist_url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
        }
        
        response = requests.post(
            'http://localhost:5001/api/spotify/playlist',
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Spotify API working! Found playlist: {data.get('name', 'Unknown')}")
            print(f"   Total tracks: {data.get('total_tracks', 0)}")
            return True, data
        else:
            print(f"❌ Spotify API failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Spotify API test failed: {str(e)}")
        return False, None

def test_youtube_search():
    """Test YouTube search functionality"""
    try:
        test_data = {
            "query": "Never Gonna Give You Up Rick Astley"
        }
        
        response = requests.post(
            'http://localhost:5001/api/youtube/search',
            json=test_data,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            videos = data.get('videos', [])
            print(f"✅ YouTube search working! Found {len(videos)} videos")
            if videos:
                print(f"   First result: {videos[0]['title']}")
            return True
        else:
            print(f"❌ YouTube search failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ YouTube search test failed: {str(e)}")
        return False

def main():
    print("🚀 Testing Spotify to MP3 Converter Application\n")
    
    # Wait for server to be ready
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Test 1: Server Health
    print("\n1️⃣ Testing server health...")
    if not test_server_health():
        print("❌ Server is not responding. Exiting.")
        sys.exit(1)
    
    # Test 2: Spotify API
    print("\n2️⃣ Testing Spotify API integration...")
    spotify_ok, playlist_data = test_spotify_api()
    
    # Test 3: YouTube Search
    print("\n3️⃣ Testing YouTube search...")
    youtube_ok = test_youtube_search()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print(f"   Server Health: ✅ PASS")
    print(f"   Spotify API: {'✅ PASS' if spotify_ok else '❌ FAIL'}")
    print(f"   YouTube Search: {'✅ PASS' if youtube_ok else '❌ FAIL'}")
    
    if spotify_ok and youtube_ok:
        print("\n🎉 All core functionality tests passed!")
        print("   The application is ready for use.")
        
        if playlist_data:
            print(f"\n📋 Sample playlist data:")
            print(f"   Name: {playlist_data.get('name', 'Unknown')}")
            print(f"   Tracks: {playlist_data.get('total_tracks', 0)}")
            if playlist_data.get('tracks'):
                first_track = playlist_data['tracks'][0]
                print(f"   First track: {first_track['name']} by {', '.join(first_track['artists'])}")
        
        return True
    else:
        print("\n⚠️  Some tests failed. The application may not work correctly.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

