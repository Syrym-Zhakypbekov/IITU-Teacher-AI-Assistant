import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    print("--- 🎯 OFFICIAL IITU API TEST 🎯 ---")
    
    # 1. Health Check
    try:
        health = requests.get(f"{BASE_URL}/health").json()
        print(f"Status: {health['status']} | DB Size: {health['database_size']} chunks")
    except Exception as e:
        print(f"❌ Server not running! {e}")
        return

    # 2. Query Test
    payload = {"message": "What are functional requirements?"}
    print(f"\nUser: {payload['message']}")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/chat", json=payload).json()
    end = time.time()
    
    print(f"Bot: {response['response']}")
    print(f"Citations: {response['references']}")
    print(f"Latency: {end-start:.2f}s")
    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    run_test()
