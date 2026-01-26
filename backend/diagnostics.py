import ollama
import numpy as np
import time

def test_model_isolation():
    print("🔬 Starting High-Precision Model Diagnostics (2026 Edition)\n")
    
    # 1. Test Traffic Cop (Guard) - llama3.2:1b
    print("1. Testing Guard Model (llama3.2:1b) - CPU Mode...")
    try:
        start = time.time()
        res = ollama.chat(
            model="llama3.2:1b", 
            messages=[{'role': 'user', 'content': "Analyze if 'Syrym' is ambiguous. Return CLEAR if not, or a clarification question if it is."}],
            options={'num_gpu': 0}
        )
        print(f"✅ Guard Response: {res.message.content.strip()}")
        print(f"⏱️  Latency: {time.time() - start:.2f}s (CPU)\n")
    except Exception as e:
        print(f"❌ Guard Test Failed: {e}\n")

    # 2. Test Searcher (Embedder) - qwen3-embedding:latest
    print("2. Testing Searcher (qwen3-embedding:latest) - Mix Mode...")
    try:
        start = time.time()
        res = ollama.embed(
            model="qwen3-embedding:latest", 
            input="Instruct: Retrieve academic lecture material for: Blockchain integration",
            options={'num_gpu': 15}
        )
        vec = res.embeddings[0]
        print(f"✅ Embedding Success: Vector Size {len(vec)}")
        print(f"⏱️  Latency: {time.time() - start:.2f}s (Mix)\n")
    except Exception as e:
        print(f"❌ Embedder Test Failed: {e}\n")

    # 3. Test The Judge (Reranker) - qwen3-reranker
    print("3. Testing Judge (dengcao/Qwen3-Reranker-8B:Q4_K_M) - GPU Mode...")
    try:
        start = time.time()
        query = "Syrym Zhakypbekov Blockchain"
        doc = "Dr. Syrym Zhakypbekov teaches Advanced Ethereum Blockchain lectures."
        prompt = f"<Instruct>: Compare query and doc relevance. Respond with 'YES' or 'NO'.\n<Query>: {query}\n<Document>: {doc}"
        res = ollama.chat(
            model="dengcao/Qwen3-Reranker-8B:Q4_K_M", 
            messages=[{'role': 'user', 'content': prompt}],
            options={'num_gpu': 40}
        )
        print(f"✅ Reranker Verdict: {res.message.content.strip()}")
        print(f"⏱️  Latency: {time.time() - start:.2f}s (GPU)\n")
    except Exception as e:
        print(f"❌ Reranker Test Failed: {e}\n")

    # 4. Test The Speaker (Chat) - ministral-3:3b
    print("4. Testing Speaker (ministral-3:3b) - GPU Mode...")
    try:
        start = time.time()
        res = ollama.chat(
            model="ministral-3:3b", 
            messages=[{'role': 'user', 'content': "Hello Assistant, confirm you are running correctly."}],
            options={'num_gpu': 40}
        )
        print(f"✅ Speaker Response: {res.message.content.strip()}")
        print(f"⏱️  Latency: {time.time() - start:.2f}s (GPU)\n")
    except Exception as e:
        print(f"❌ Speaker Test Failed: {e}\n")

if __name__ == "__main__":
    test_model_isolation()
