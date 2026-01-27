
import requests
import time
import os
import random
import string

# DETECTED FROM USER INPUT
# If this is wrong, the user can override it in the console or script.
TAILSCALE_URL = "https://prod.ilish-cobra.ts.net"
LOCAL_URL = "http://localhost:8000"

def generate_large_file(filename, size_mb):
    """Generates a dummy file of specific size to test transfer capacity."""
    print(f"  > Generating {size_mb}MB dummy file: {filename}...")
    with open(filename, "wb") as f:
        f.write(os.urandom(size_mb * 1024 * 1024))

def test_tailscale_connection():
    print("🌍 STARTING TAILSCALE FUNNEL STRESS TEST 🌍")
    print("=============================================")
    print(f"Testing connectivity to: {TAILSCALE_URL}")
    
    # 1. SANITY CHECK (Reachability)
    try:
        start = time.time()
        # We assume forwarded port 443 -> 8000
        resp = requests.get(f"{TAILSCALE_URL}/docs", timeout=10) 
        lat = (time.time() - start) * 1000
        print(f"✅ [Connectivity] SUCCESS. Latency: {lat:.0f}ms")
        print(f"   (Status: {resp.status_code})")
    except Exception as e:
        print(f"❌ [Connectivity] FAILED. Is 'tailscale serve' running?")
        print(f"   Command hint: tailscale serve https / http://localhost:8000")
        print(f"   Error: {e}")
        return

    # 2. FILE TRANSFER STRESS (Bandwidth)
    print("\n📦 [Phase 2] Testing File Transfer (5MB)...")
    fname = "tailscale_stress_test.bin"
    course_id = "stress_connection_test"
    
    try:
        # Create workspace first (using fast local path to ensure it exists)
        requests.post(f"{LOCAL_URL}/api/courses", json={"id": course_id, "subject": "Connection Test", "teacherName": "NetAdmin"})
        
        generate_large_file(fname, 5) # 5MB file
        
        with open(fname, 'rb') as f:
            start = time.time()
            resp = requests.post(
                f"{TAILSCALE_URL}/api/upload", 
                data={'course_id': course_id}, 
                files={'files': (fname, f, 'application/octet-stream')}
            )
            duration = time.time() - start
            
        if resp.status_code == 200:
            mbps = (5 * 8) / duration # Mbps
            print(f"✅ [Upload] SUCCESS. Time: {duration:.2f}s | Speed: {mbps:.2f} Mbps")
        else:
            print(f"❌ [Upload] FAILED. Status: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ [Upload] ERROR: {e}")
    finally:
        if os.path.exists(fname):
            os.remove(fname)

    # 3. CHAT LATENCY COMPARISON
    print("\n💬 [Phase 3] Chat Latency: Local vs Remote...")
    q = "Hello, are you receiving this over the internet?"
    
    # Local Baseline
    start = time.time()
    try:
        requests.post(f"{LOCAL_URL}/api/chat", json={"message": q, "course_id": course_id})
        local_lat = time.time() - start
        print(f"  > Localhost Latency: {local_lat:.2f}s")
    except:
        local_lat = 0
        print("  > Localhost failed (unexpected).")

    # Remote Tailscale
    start_r = time.time()
    try:
        resp = requests.post(f"{TAILSCALE_URL}/api/chat", json={"message": q, "course_id": course_id})
        remote_lat = time.time() - start_r
        print(f"  > Tailscale Latency: {remote_lat:.2f}s")
        
        diff = remote_lat - local_lat
        print(f"  > Network Overhead: {diff:.2f}s")
        
        if resp.status_code == 200:
            print("✅ [Chat] Remote connection stable.")
        else:
            print(f"❌ [Chat] Remote error: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ [Chat] FAILED connecting to Tailscale: {e}")

    # 4. AUDIO HEADER CHECK (Headers Preservation)
    print("\n🎤 [Phase 4] Checking Header Preservation (Voice Mode)...")
    try:
        resp = requests.post(f"{TAILSCALE_URL}/api/chat", json={
            "message": "Testing audio headers.", 
            "course_id": course_id,
            "is_voice": True
        })
        if resp.status_code == 200:
            ans = resp.json()['response']
            if "**" not in ans:
                 print("✅ [Headers] 'is_voice' flag preserved over Funnel. (Markdown stripped)")
            else:
                 print("❌ [Headers] Flag lost? Markdown found.")
    except Exception as e:
        print(f"❌ [Headers] Failed: {e}")

    print("\n=============================================")
    print("🌍 TAILSCALE STRESS TEST COMPLETE")

if __name__ == "__main__":
    test_tailscale_connection()
