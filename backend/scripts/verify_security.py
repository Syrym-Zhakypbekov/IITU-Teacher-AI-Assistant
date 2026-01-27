from teacher_assistant.src.core.resource_guard import ResourceGuard
import time
import threading

def verify_security():
    print("Initializing ResourceGuard...")
    # Set strict limits for testing
    guard = ResourceGuard(max_concurrent=10, max_cpu_percent=50.0) 
    # Force max_requests_per_min to 5 for quick test
    guard.max_requests_per_min = 5
    
    ip = "192.168.1.100"
    
    print("\n--- TEST 1: Rate Limiting (DDoS Shield) ---")
    print(f"Sending 10 requests (Limit is 5)...")
    
    allowed = 0
    blocked = 0
    
    for i in range(10):
        if guard.check_rate_limit(ip):
            print(f"Req {i+1}: Allowed")
            allowed += 1
        else:
            print(f"Req {i+1}: BLOCKED (429)")
            blocked += 1
            
    if blocked > 0:
        print(f"SUCCESS: Blocked {blocked} requests. DDoS Shield Active.")
    else:
        print("FAILURE: Did not block requests.")

    print("\n--- TEST 2: Resource Slot Acquisition ---")
    slots = []
    for i in range(12):
        if guard.acquire_slot():
            slots.append(i)
        else:
            print(f"Slot {i+1}: Server Busy (503)")
            
    print(f"Acquired {len(slots)} slots. Releasing...")
    for _ in slots:
        guard.release_slot()
        
    print("\n--- TEST 3: CPU Health Check ---")
    is_healthy, msg = guard.check_health()
    print(f"Status: {msg}")
    
    # Simulate Overheat
    guard.cool_down_until = time.time() + 10
    is_healthy, msg = guard.check_health()
    print(f"Simulate Overheat: {msg}")
    if not is_healthy:
        print("SUCCESS: System detected overheat condition.")

if __name__ == "__main__":
    verify_security()
