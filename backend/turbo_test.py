import ollama
import time

def turbo_check():
    print("⚡ TURBO DIAGNOSTICS: Testing the 1B pipeline...\n")
    
    models_to_test = {
        "Embed": "nomic-embed-text:latest",
        "Chat": "llama3.2:1b"
    }

    # 1. TEST EMBEDDING (FASTER THAN QWEN 8B)
    print(f"🔹 Testing {models_to_test['Embed']}...")
    s = time.time()
    res = ollama.embed(model=models_to_test['Embed'], input="Hello world")
    print(f"   ✅ Done in {time.time()-s:.2f}s (Vector size: {len(res.embeddings[0])})")

    # 2. TEST CHAT (1B IS INSTANT)
    print(f"\n🔹 Testing {models_to_test['Chat']}...")
    s = time.time()
    res = ollama.chat(model=models_to_test['Chat'], messages=[{'role': 'user', 'content': 'Say HI very short.'}])
    print(f"   🤖 Assistant: {res.message.content.strip()}")
    print(f"   ✅ Done in {time.time()-s:.2f}s")

    print("\n🚀 CONCLUSION: System is healthy and fast with 1B models.")

if __name__ == "__main__":
    turbo_check()
