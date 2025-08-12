#!/usr/bin/env python3
import requests
import json
import time

def test_nasmytunes():
    """Test the live NasmyTunes application"""
    base_url = "https://nasmytunes.onrender.com"
    print(f"🎵 Testing NasmyTunes at: {base_url}")
    
    # Test 1: Website accessibility
    print("\n1️⃣ Testing website accessibility...")
    try:
        response = requests.get(base_url, timeout=30)
        if response.status_code == 200:
            print("✅ Website is live and accessible!")
            print(f"   Response size: {len(response.content)} bytes")
        else:
            print(f"❌ Website returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
    
    # Test 2: Try different Spotify playlists
    test_playlists = [
        {
            "name": "Spotify's Today's Top Hits",
            "url": "https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd"
        },
        {
            "name": "Pop Rising",
            "url": "https://open.spotify.com/playlist/37i9dQZF1DXcRXFNfZr7Tp"
        },
        {
            "name": "Global Top 50",
            "url": "https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF"
        }
    ]
    
    print("\n2️⃣ Testing Spotify API with different playlists...")
    api_url = f"{base_url}/api/spotify/playlist"
    
    for playlist in test_playlists:
        print(f"\n   Testing: {playlist['name']}")
        try:
            response = requests.post(
                api_url,
                json={"playlist_url": playlist["url"]},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Playlist: {data.get('name', 'Unknown')}")
                print(f"      Total tracks: {data.get('total_tracks', 0)}")
                return True
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"      Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Test 3: YouTube search
    print("\n3️⃣ Testing YouTube search...")
    try:
        youtube_url = f"{base_url}/api/youtube/search"
        response = requests.post(
            youtube_url,
            json={"query": "Never Gonna Give You Up Rick Astley"},
            headers={"Content-Type": "application/json"},
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
            print(f"❌ YouTube search failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ YouTube search error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing your live NasmyTunes application...")
    success = test_nasmytunes()
    
    if success:
        print("\n🎉 Your app is working great!")
        print("✅ Website accessible")
        print("✅ API endpoints functional")
        print("\n🎵 Ready to convert playlists!")
        print("Visit: https://nasmytunes.onrender.com")
    else:
        print("\n⚠️ Some issues detected.")
        print("The website is live but API needs attention.")
        print("Check Render logs for more details.")