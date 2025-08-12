#!/usr/bin/env python3
import requests
import json
import time

def test_full_conversion():
    """Test the complete conversion workflow"""
    base_url = "http://localhost:5000"
    
    # Sample tracks for testing (shorter songs)
    test_tracks = [
        {
            "name": "Never Gonna Give You Up",
            "artists": ["Rick Astley"],
            "duration_ms": 213000
        },
        {
            "name": "Darude Sandstorm",
            "artists": ["Darude"],
            "duration_ms": 234000
        }
    ]
    
    try:
        print("🚀 Starting conversion test...\n")
        
        # Step 1: Start conversion
        print("1️⃣ Starting conversion job...")
        response = requests.post(
            f"{base_url}/api/convert/start",
            json={
                "tracks": test_tracks,
                "playlist_name": "Test Playlist"
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to start conversion: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        job_data = response.json()
        job_id = job_data['job_id']
        print(f"✅ Conversion started! Job ID: {job_id}")
        print(f"   Total tracks: {job_data['total_tracks']}")
        
        # Step 2: Monitor progress
        print("\n2️⃣ Monitoring conversion progress...")
        max_wait_time = 300  # 5 minutes max
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            response = requests.get(f"{base_url}/api/convert/status/{job_id}", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Failed to get status: {response.status_code}")
                return False
            
            status_data = response.json()
            status = status_data['status']
            progress = status_data['progress']
            current_track = status_data.get('current_track', 'None')
            
            print(f"   Status: {status} | Progress: {progress:.1f}% | Current: {current_track}")
            
            if status == 'completed':
                print("✅ Conversion completed!")
                break
            elif status == 'failed':
                print(f"❌ Conversion failed: {status_data.get('error', 'Unknown error')}")
                return False
            
            time.sleep(5)  # Check every 5 seconds
        else:
            print("❌ Conversion timed out")
            return False
        
        # Step 3: Test download
        print("\n3️⃣ Testing download...")
        response = requests.get(f"{base_url}/api/convert/download/{job_id}", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to download: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Check if we got a ZIP file
        if response.headers.get('content-type') == 'application/zip':
            file_size = len(response.content)
            print(f"✅ Download successful! ZIP file size: {file_size / 1024:.1f} KB")
        else:
            print(f"❌ Unexpected content type: {response.headers.get('content-type')}")
            return False
        
        # Step 4: Cleanup
        print("\n4️⃣ Cleaning up...")
        response = requests.delete(f"{base_url}/api/convert/cleanup/{job_id}", timeout=10)
        
        if response.status_code == 200:
            print("✅ Cleanup successful!")
        else:
            print(f"⚠️  Cleanup warning: {response.status_code}")
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎵 Testing Spotify to MP3 Conversion System\n")
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    success = test_full_conversion()
    
    print(f"\n📊 Test Result: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("\n🎉 All conversion tests passed!")
        print("   The system can successfully:")
        print("   - Start conversion jobs")
        print("   - Monitor progress")
        print("   - Download ZIP files")
        print("   - Clean up resources")
    else:
        print("\n⚠️  Conversion test failed. Check the logs above.")

