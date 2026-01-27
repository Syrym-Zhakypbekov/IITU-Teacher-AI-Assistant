import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def test_russian():
    print("🇷🇺 TESTING RUSSIAN CAPABILITIES 🇷🇺")
    
    # 1. Simple Greeting (Should be fast/skipped)
    q1 = "Привет, ты кто?" # Hello, who are you?
    print(f"\nUser: {q1}")
    t0 = time.time()
    res1 = requests.post(f"{BASE_URL}/api/chat", json={"message": q1}).json()
    dt1 = time.time() - t0
    print(f"Bot: {res1['response']}")
    print(f"Latency: {dt1:.2f}s (Target: <1s)")
    
    # 2. RAG Query (Should be Russian Answer via Deep Dive)
    # Using a generic term that likely exists in the course or general knowledge if course is empty
    q2 = "Что такое функциональные требования?" # What are functional requirements?
    print(f"\nUser: {q2}")
    t0 = time.time()
    res2 = requests.post(f"{BASE_URL}/api/chat", json={"message": q2}).json()
    dt2 = time.time() - t0
    print(f"Bot: {res2['response'][:100]}...")
    print(f"Status: {res2.get('status')} | Latency: {dt2:.2f}s")
    
    if "функциональные" in res2['response'].lower() or "requirements" in res2['response'].lower():
        print("✅ SUCCESS: Model answered in relevant context.")
    else:
        print("⚠️ WARNING: Check language.")

if __name__ == "__main__":
    test_russian()
