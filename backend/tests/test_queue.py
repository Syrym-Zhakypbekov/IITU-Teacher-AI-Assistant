
import requests
import time
import threading
import sys

BASE_URL = "http://localhost:8000"
COURSE_ID = "queue_stress_test"

def simulate_user(user_id, delay=0):
    time.sleep(delay)
    print(f"[{user_id}] 🟢 Starting request...")
    
    # 1. Join Queue / Try Request
    req_body = {
        "message": f"Hello from {user_id}",
        "course_id": COURSE_ID
    }
    
    ticket_id = None
    attempts = 0
    
    while attempts < 30:
        if ticket_id:
            req_body['ticket_id'] = ticket_id
            
        try:
            resp = requests.post(f"{BASE_URL}/api/chat", json=req_body)
            data = resp.json()
            
            if resp.status_code == 200:
                print(f"[{user_id}] ✅ SUCCESS: {data['response'][:50]}...")
                return
            elif data.get('status') == 'queued':
                ticket_id = data['ticket_id']
                pos = data['position']
                wait = data['wait_time']
                print(f"[{user_id}] ⏳ QUEUED: Ticket={ticket_id[:5]}, Pos={pos}, Wait={wait}s")
                time.sleep(2) # Poll delay
            else:
                print(f"[{user_id}] ❌ ERROR: {resp.status_code} - {resp.text}")
                return
        except Exception as e:
            print(f"[{user_id}] 💥 EXCEPTION: {e}")
            return
        
        attempts += 1
        
    print(f"[{user_id}] 💀 TIMEOUT after {attempts} attempts")

def test_queue_system():
    print("🚦 TESTING QUEUE SYSTEM & CONCURRENCY 🚦")
    
    # Authenticate first (reuse auth logic or simplify if open, but auth is on)
    # We'll use the 'student' flow or just register one test user
    # Actually, main.py doesn't strictly enforce auth on /api/chat yet? 
    # Let's check main.py... /api/chat usually requires auth? 
    # Looking at main.py lines...
    # @app.post("/api/chat")
    # async def chat(request: ChatRequest, ...):
    # It does NOT seems to have Depends(get_current_user) in the signature I viewed previously.
    # Let's assume it's public for now based on recent edits not showing Depends. 
    # If it fails with 401, I'll add auth.

    users = []
    # Launch 5 concurrent users
    # Processing time is simulated or RAG takes time.
    # If RAG is fast, queue might not trigger.
    # We rely on ResourceGuard(max_concurrent=50). 
    # To Trigger Queue, we need > 50 users OR we need to artificially lower max_concurrent for test.
    # Since I cannot restart server with different args easily, I will hammer it.
    # But 50 threads is a lot for a test script. 
    # Maybe I'll just check if the logic holds for a single user "joining queue" if I can force it?
    # No, I should try to fill the slots.
    
    # Actually, ResourceGuard in `main.py` is initialized with `max_concurrent=50`.
    # To test queue with only a few users, I would need to modify the limit.
    # However, I can test the PROTOCOL by manually sending a 'ticket_id' that doesn't exist?
    # Or I can just verify the endpoint responds correctly.
    
    # Real stress test: 60 users.
    print("🚀 Launching 60 concurrent users to trigger Queue (Limit=50)...")
    
    threads = []
    for i in range(60):
        t = threading.Thread(target=simulate_user, args=(f"u{i}", i*0.05))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()

if __name__ == "__main__":
    test_queue_system()
