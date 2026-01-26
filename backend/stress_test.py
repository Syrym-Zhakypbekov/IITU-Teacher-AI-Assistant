import ollama
import lancedb
import json
import time
import concurrent.futures
from statistics import mean

# --- CONFIG ---
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "ministral-3:3b"
DB_PATH = "./performance_test_db"

def init_test_db():
    db = lancedb.connect(DB_PATH)
    # Stress data: 50 records with overlapping names and topics
    data = []
    for i in range(50):
        name = "Dr. Syrym" if i % 2 == 0 else "Dr. Zhakypbekov"
        topic = "Blockchain" if i % 3 == 0 else "Advanced Math"
        data.append({
            "tutor": f"{name} {i}",
            "topic": topic,
            "content": f"This is lecture {i} about {topic} by {name}. Precise details: {i*7} encrypted blocks for student {i}."
        })
    
    # Pre-embed to avoid timing the initial load
    print("📊 Pre-embedding 50 records for stress test...")
    for item in data:
        item['vector'] = ollama.embed(model=EMBED_MODEL, input=item['content']).embeddings[0]
    
    tbl = db.create_table("stress_test", data=data, mode="overwrite")
    tbl.create_fts_index("content")
    return tbl

def single_query_worker(query_id):
    start_time = time.time()
    try:
        db = lancedb.connect(DB_PATH)
        tbl = db.open_table("stress_test")
        
        # 1. Embed Query
        q_vec = ollama.embed(model=EMBED_MODEL, input="Syrym Blockchain info").embeddings[0]
        
        # 2. Hybrid Search
        results = tbl.search(q_vec).limit(5).to_pandas()
        context = results.to_string()
        
        # 3. LLM Generation
        res = ollama.chat(
            model=CHAT_MODEL,
            messages=[{'role': 'user', 'content': f"Context: {context}\nQuestion: Give me a short summary."}]
        )
        
        latency = time.time() - start_time
        return {"id": query_id, "latency": latency, "status": "SUCCESS"}
    except Exception as e:
        return {"id": query_id, "error": str(e), "status": "FAILED"}

def run_performance_test(concurrency=5):
    print(f"\n🔥 STARTING STRESS TEST: Concurrency={concurrency}")
    print(f"Targeting: {EMBED_MODEL} & {CHAT_MODEL}")
    
    tbl = init_test_db()
    
    latencies = []
    failures = 0
    
    start_test = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(single_query_worker, i) for i in range(concurrency)]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result["status"] == "SUCCESS":
                latencies.append(result["latency"])
                print(f"  Query {result['id']} Finished: {result['latency']:.2f}s")
            else:
                failures += 1
                print(f"  Query {result['id']} FAILED: {result['error']}")

    total_time = time.time() - start_test
    
    print("\n📈 TEST RESULTS:")
    print(f"Total Time: {total_time:.2f}s")
    if latencies:
        print(f"Avg Latency: {mean(latencies):.2f}s")
        print(f"Min Latency: {min(latencies):.2f}s")
        print(f"Max Latency: {max(latencies):.2f}s")
    print(f"Failure Rate: {failures}/{concurrency}")
    print("-" * 30)

if __name__ == "__main__":
    # Test 1: Single User Baseline
    run_performance_test(concurrency=1)
    
    # Test 2: Multitasking (5 Users hitting at once)
    # This checks VRAM management and Ollama's ability to interleave tokens
    run_performance_test(concurrency=5)
