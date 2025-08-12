#!/usr/bin/env python3
"""
Test all YouTube bypass methods
"""
import tempfile
import os
from src.utils.simple_bypass import SimpleBypass
from src.utils.authenticated_bypass import AuthenticatedBypass

def test_all_bypasses():
    """Test all bypass methods"""
    print("🚀 Testing All YouTube Bypass Methods")
    print("=" * 60)
    
    # Test track
    track_name = "Never Gonna Give You Up"
    artists = ["Rick Astley"]
    
    bypasses = [
        ("Simple Bypass", SimpleBypass()),
        ("Authenticated Bypass", AuthenticatedBypass()),
    ]
    
    results = {}
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for bypass_name, bypass_obj in bypasses:
            print(f"\n🔧 Testing {bypass_name}")
            print("-" * 40)
            
            try:
                if hasattr(bypass_obj, 'download_simple'):
                    success, message = bypass_obj.download_simple(track_name, artists, temp_dir)
                elif hasattr(bypass_obj, 'download_with_authentication'):
                    success, message = bypass_obj.download_with_authentication(track_name, artists, temp_dir)
                else:
                    success, message = False, "Unknown method"
                
                results[bypass_name] = {
                    'success': success,
                    'message': message
                }
                
                if success:
                    print(f"✅ {bypass_name}: SUCCESS")
                    print(f"   Message: {message}")
                    
                    # Check files
                    files = [f for f in os.listdir(temp_dir) if f.endswith('.mp3')]
                    print(f"   Files: {files}")
                else:
                    print(f"❌ {bypass_name}: FAILED")
                    print(f"   Reason: {message}")
                
                # Cleanup
                if hasattr(bypass_obj, 'cleanup'):
                    bypass_obj.cleanup()
                    
            except Exception as e:
                print(f"❌ {bypass_name}: EXCEPTION")
                print(f"   Error: {str(e)}")
                results[bypass_name] = {
                    'success': False,
                    'message': f"Exception: {str(e)}"
                }
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 BYPASS TEST SUMMARY")
    print("=" * 60)
    
    for bypass_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{bypass_name:20} | {status} | {result['message'][:40]}...")
    
    # Overall result
    successful_bypasses = sum(1 for r in results.values() if r['success'])
    total_bypasses = len(results)
    
    print(f"\n🎯 Overall: {successful_bypasses}/{total_bypasses} bypasses successful")
    
    if successful_bypasses > 0:
        print("🎉 At least one bypass method is working!")
        print("   This means the system can potentially work on Render.")
    else:
        print("⚠️  All bypasses failed locally.")
        print("   This suggests YouTube's detection is very aggressive.")

if __name__ == "__main__":
    test_all_bypasses()