
import requests
import json
import time

OLLAMA_URL = "http://localhost:11434/api"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "qwen2.5-coder:0.5b-instruct-fp16"

def check_models():
    print("🤖 DIAGNOSTIC: AI Model Health Check")
    print("=====================================")
    
    # 1. Check Ollama Service
    try:
        resp = requests.get("http://localhost:11434/")
        if resp.status_code == 200:
            print("✅ Ollama Service: ONLINE")
        else:
            print(f"❌ Ollama Service: Error {resp.status_code}")
            return
    except Exception as e:
        print(f"❌ Ollama Service: DOWN ({e})")
        print("   -> Please run 'ollama serve' in a separate terminal.")
        return

    # 2. Check Loaded Models
    print("\n📦 Checking Available Models...")
    try:
        resp = requests.get(f"{OLLAMA_URL}/tags")
        models = [m['name'] for m in resp.json()['models']]
        print(f"   Found: {models}")
        
        missing = []
        if not any(EMBED_MODEL in m for m in models): missing.append(EMBED_MODEL)
        if not any(CHAT_MODEL in m for m in models): missing.append(CHAT_MODEL)
        
        if missing:
            print(f"❌ MISSING MODELS: {missing}")
            print("   -> Run: ollama pull nomic-embed-text")
            print("   -> Run: ollama pull llama3.2")
        else:
            print("✅ Required Models: PRESENT")
    except Exception as e:
        print(f"❌ Model List Failed: {e}")

    # 3. Test Embedding (Latency Check)
    print(f"\n🧠 Testing Embeddings ({EMBED_MODEL})...")
    start = time.time()
    try:
        payload = {"model": EMBED_MODEL, "prompt": "The quick brown fox jumps over the lazy dog."}
        resp = requests.post(f"{OLLAMA_URL}/embeddings", json=payload)
        if resp.status_code == 200:
            vec = resp.json().get('embedding', [])
            elapsed = (time.time() - start) * 1000
            if len(vec) > 0:
                print(f"✅ Embedding: SUCCESS (Dim: {len(vec)}, Time: {elapsed:.2f}ms)")
                if elapsed > 500:
                    print("   ⚠️  WARNING: Embedding is slow (>500ms). Is GPU active?")
            else:
                print("❌ Embedding: Returned empty vector.")
        else:
            print(f"❌ Embedding: API Error {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Embedding: Request Failed ({e})")

    # 4. Test Chat Generation
    print(f"\n💬 Testing Chat Generation ({CHAT_MODEL})...")
    start = time.time()
    try:
        payload = {
            "model": CHAT_MODEL, 
            "messages": [{"role": "user", "content": "Say 'System Operational' in one word."}], 
            "stream": False
        }
        resp = requests.post(f"{OLLAMA_URL}/chat", json=payload)
        if resp.status_code == 200:
            ans = resp.json()['message']['content']
            elapsed = (time.time() - start)
            print(f"✅ Chat: SUCCESS in {elapsed:.2f}s")
            print(f"   Response: {ans.strip()}")
        else:
            print(f"❌ Chat: API Error {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Chat: Request Failed ({e})")

if __name__ == "__main__":
    check_models()
