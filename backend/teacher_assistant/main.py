import json
import os
from teacher_assistant.src.infrastructure.database import VectorStore
from teacher_assistant.src.infrastructure.ollama_client import OllamaProvider
from teacher_assistant.src.use_cases.rag_engine import RAGEngine

def setup_demo():
    print("🚀 Initializing Pro-Grade RAG System (2026 Edition)...")
    
    db = VectorStore()
    ai = OllamaProvider()
    engine = RAGEngine(db, ai)

    # 1. Load Dummy Data
    data_path = "./teacher_assistant/data/raw/tutor_test.json"
    with open(data_path, "r") as f:
        raw_data = json.load(f)

    # 2. Add Embeddings to Data
    print("🧠 Generating embeddings for dummy data...")
    for item in raw_data:
        item["vector"] = ai.get_embedding(item["content"])

    # 3. Index Data
    print("📂 Indexing data into LanceDB with FTS...")
    db.index_data(raw_data)
    
    return engine

def run_test(engine, query):
    print(f"\n🔍 Querying: '{query}'")
    result = engine.process_query(query)
    print(f"🤖 Response: {result['response']}")
    if result['references']:
        print(f"📚 References: {', '.join(result['references'])}")
    print("-" * 50)

if __name__ == "__main__":
    # Ensure folder context
    os.makedirs("./teacher_assistant/data/lancedb_index", exist_ok=True)
    
    engine = setup_demo()

    # TEST CASES
    # Test 1: Exact Name Match
    run_test(engine, "Tell me about Dr. Syrym Zhakypbekov's lecture on Blockchain")

    # Test 2: Similar Name Match (Should be distinguished by Reranker)
    run_test(engine, "What is Dr. Syrym Zhakypov's topic?")

    # Test 3: Ambiguity Check
    run_test(engine, "What does Syrym teach?")
