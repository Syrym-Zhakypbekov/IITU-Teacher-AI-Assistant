
import time
import requests
import json
import statistics

# CONFIG
API_URL = "http://localhost:8000/api/chat"
LOGIN_URL = "http://localhost:8000/api/auth/login"
COURSE_ID = "legacy_reengineering" 

def get_token():
    try:
        # Fix: Use JSON and 'email' field
        resp = requests.post(LOGIN_URL, json={"email": "admin@iitu.kz", "password": "admin123"})
        if resp.status_code == 200:
            # Fix: Response key is 'token'
            return resp.json().get("token")
        print(f"⚠️ Login Failed: {resp.text}")
    except Exception as e:
        print(f"⚠️ Login Error: {e}")
    return None

def run_test(name, payload, token):
    print(f"\n🧪 TEST: {name}")
    print(f"   Input: {payload['message']}")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    start = time.time()
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=120)
        end = time.time()
        
        elapsed = end - start
        data = response.json()
        
        print(f"   ⏱️ Time: {elapsed:.2f}s")
        print(f"   📝 Status: {data.get('status', 'unknown')}")
        
        # Calculate Speed (Approx)
        content = data.get('response', '')
        word_count = len(content.split())
        tps = word_count / elapsed if elapsed > 0 else 0
        
        print(f"   🚀 Speed: ~{tps:.2f} words/sec")
        print(f"   📄 Length: {len(content)} chars")
        print(f"   💡 Response Snippet: {content[:100]}...")
        
        return {
            "name": name,
            "elapsed": elapsed,
            "status": data.get('status'),
            "response": content
        }
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return None

def main():
    print("💎 SMART COST MANAGEMENT & CPU BENCHMARK 💎")
    print("---------------------------------------------")
    
    token = get_token()
    if not token:
        print("❌ CRITICAL: Could not authenticate. Tests will likely fail.")
    else:
        print("✅ Authenticated as Admin.")

    # 1. CHEAP QUERY (Should be skipped by RAG)
    res1 = run_test("Smart Cost Check (Cheap)", {
        "message": "hi",
        "course_id": COURSE_ID 
    }, token)
    
    # 2. COMPLEX QUERY (Full RAG + Gemma 3 4B)
    res2 = run_test("CPU Performance (Heavy)", {
        "message": "What are requirements validation techniques?", 
        "course_id": COURSE_ID
    }, token)

    print("\n📊 RESULTS ANALYSIS")
    print("-------------------")
    
    if res1:
        is_cheap = res1['elapsed'] < 1.0 or res1['status'] == "chat_simple"
        print(f"✅ Cost Management: {'PASS' if is_cheap else 'FAIL'} (Time: {res1['elapsed']:.2f}s)")
        if is_cheap:
            print("   -> System correctly identified 'hi' as low-cost and skipped heavy processing.")
    
    if res2:
        is_responsive = res2['elapsed'] < 30.0 
        print(f"✅ CPU Performance: {'ACCEPTABLE' if is_responsive else 'SLOW'} (Time: {res2['elapsed']:.2f}s)")
        print(f"   -> Model: gemma3:4b")

if __name__ == "__main__":
    main()
