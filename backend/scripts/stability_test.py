import requests
import time
import concurrent.futures
import json
import random

BASE_URL = "http://127.0.0.1:8000"

def test_scenario(name, queries, parallel=False):
    print(f"\n🔹 SCENARIO: {name}")
    print("-" * 50)
    
    start_all = time.time()
    
    def send_query(q):
        t0 = time.time()
        try:
            res = requests.post(f"{BASE_URL}/api/chat", json={"message": q})
            data = res.json()
            latency = time.time() - t0
            status = data.get('status', 'unknown') if res.status_code == 200 else f"HTTP {res.status_code}"
            print(f"   [{latency:.2f}s] Q: '{q[:30]}...' -> {status}")
            return True
        except Exception as e:
            print(f"   [ERROR] {e}")
            return False

    if parallel:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            list(executor.map(send_query, queries))
    else:
        for q in queries:
            send_query(q)
            
    print(f"   Total Duration: {time.time() - start_all:.2f}s")


def run_complete_test():
    print("🚀 STARTING LIVE STABILITY TEST")
    
    # 0. Health Check
    try:
        h = requests.get(f"{BASE_URL}/health").json()
        print(f"✅ Server Online: {h['status']} (v{h.get('version')})")
    except:
        print("❌ Server OFFLINE. Aborting.")
        return

    # Scenario 1: Mixed Bag (Cold & Simple)
    test_scenario("Normal Usage (Mixed)", [
        "Hello there!",                      # Cheap (Chat)
        "Who created you?",                  # Cheap (Chat)
        "What are non-functional requirements?" # Expensive (RAG) or Cached
    ])
    
    # Scenario 2: Cache Validation (Warm & Semantic)
    test_scenario("Caching & Prediction", [
        "What are non-functional requirements?",   # Exact Match (Warm)
        "tell me about non-functional requirements", # Semantic Match (Prediction)
        "explain non functional reqs"              # Semantic Match (Prediction)
    ])
    
    # Scenario 3: Concurrency / Rate Limit Check
    # ResourceGuard allows 60/min. We send 5 fast. Should pass.
    # ResourceGuard allows 50 slots. We send 5 parallel. Should pass.
    print(f"\n🔹 SCENARIO: Concurrency Burst (5 Requests)")
    qs = ["What is a stakeholder?"] * 5
    test_scenario("Parallel Burst", qs, parallel=True)
    
    # Scenario 4: Error Handling
    print(f"\n🔹 SCENARIO: Robustness (Invalid Input)")
    try:
        res = requests.post(f"{BASE_URL}/api/chat", json={"wrong_key": "test"})
        print(f"   Malformed JSON -> HTTP {res.status_code} (Expected 422)")
    except:
        pass

    # Final Health
    h = requests.get(f"{BASE_URL}/health").json()
    print(f"\n✅ Final Health Check: {h['status']}")

if __name__ == "__main__":
    run_complete_test()
