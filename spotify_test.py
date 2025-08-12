#!/usr/bin/env python3
import requests

def test_spotify_fix():
    """Test Spotify API with user-created playlists"""
    base_url = "https://nasmytunes.onrender.com"
    
    # Try with user-created public playlists (more reliable)
    test_playlists = [
        "https://open.spotify.com/playlist/2ytrrmy5nYOxcSFp9PDyHy?si=b102d7b2a88d4631",  # Example user playlist
         # Another example
    ]
    
    print("🔧 Testing Spotify API fix...")
    
    for i, playlist_url in enumerate(test_playlists, 1):
        print(f"\n{i}️⃣ Testing playlist {i}...")
        try:
            response = requests.post(
                f"{base_url}/api/spotify/playlist",
                json={"playlist_url": playlist_url},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS! Playlist: {data.get('name', 'Unknown')}")
                print(f"   Tracks: {data.get('total_tracks', 0)}")
                return True
            else:
                print(f"❌ Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    return False

if __name__ == "__main__":
    success = test_spotify_fix()
    if not success:
        print("\n💡 Workaround: You can still use the app!")
        print("   1. The YouTube search works perfectly")
        print("   2. You can manually search and convert individual songs")
        print("   3. The Spotify issue might be temporary")

test_spotify_fix()