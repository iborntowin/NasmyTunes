#!/usr/bin/env python3
import requests
import json
import time

def test_spotify_api():
    """Test the Spotify API endpoint"""
    url = "http://localhost:5000/api/spotify/playlist"
    
    # Test with a public Spotify playlist
    payload = {
        "playlist_url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing Spotify playlist endpoint...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Playlist: {data.get('name', 'Unknown')}")
            print(f"   Total tracks: {data.get('total_tracks', 0)}")
            if data.get('tracks'):
                print(f"   First track: {data['tracks'][0]['name']} by {', '.join(data['tracks'][0]['artists'])}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_youtube_search():
    """Test the YouTube search endpoint"""
    url = "http://localhost:5000/api/youtube/search"
    
    payload = {
        "query": "Bohemian Rhapsody Queen"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("\nTesting YouTube search endpoint...")
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            videos = data.get('videos', [])
            print(f"✅ Success! Found {len(videos)} videos")
            if videos:
                print(f"   First result: {videos[0]['title']}")
                print(f"   Channel: {videos[0]['channel']}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API tests...\n")
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    spotify_ok = test_spotify_api()
    youtube_ok = test_youtube_search()
    
    print(f"\n📊 Test Results:")
    print(f"   Spotify API: {'✅ PASS' if spotify_ok else '❌ FAIL'}")
    print(f"   YouTube API: {'✅ PASS' if youtube_ok else '❌ FAIL'}")
    
    if spotify_ok and youtube_ok:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the logs above.")

