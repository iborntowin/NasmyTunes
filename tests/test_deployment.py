#!/usr/bin/env python3
import requests
import json
import time

def test_deployment(base_url):
    """Test the deployed application"""
    print(f"🚀 Testing deployment at: {base_url}")
    
    # Test 1: Basic health check
    print("\n1️⃣ Testing basic connectivity...")
    try:
        response = requests.get(base_url, timeout=30)
        if response.status_code == 200:
            print("✅ Website is accessible!")
        else:
            print(f"❌ Website returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
    
    # Test 2: API endpoint
    print("\n2️⃣ Testing API endpoints...")
    try:
        api_url = f"{base_url}/api/spotify/playlist"
        test_payload = {
            "playlist_url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
        }
        
        response = requests.post(
            api_url, 
            json=test_payload, 
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Spotify API working! Found playlist: {data.get('name', 'Unknown')}")
            print(f"   Total tracks: {data.get('total_tracks', 0)}")
            return True
        else:
            print(f"❌ API test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test error: {str(e)}")
        return False

if __name__ == "__main__":
    # Replace with your actual Render URL
    render_url = "https://nasmytunes.onrender.com"
    if not render_url.startswith('http'):
        render_url = f"https://{render_url}"
    
    success = test_deployment(render_url)
    
    if success:
        print("\n🎉 Deployment test PASSED!")
        print(f"Your app is live at: {render_url}")
    else:
        print("\n⚠️ Deployment test FAILED!")
        print("Check the Render logs for more details.")