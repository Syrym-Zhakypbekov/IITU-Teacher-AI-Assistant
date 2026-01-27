from teacher_assistant.src.infrastructure.database import VectorDatabase
from teacher_assistant.src.infrastructure.ollama_client import OllamaClient
from teacher_assistant.src.use_cases.rag_engine import RAGService
import lancedb
import random
import time

def populate_synthetic_cache():
    print("Initializing Synthetic Populator...")
    db_wrapper = VectorDatabase()
    llm = OllamaClient()
    rag = RAGService(db_wrapper, llm)
    
    # 1. Read Chunks from DB
    print("Reading knowledge base...")
    arrow_table = db_wrapper.db.open_table(db_wrapper.table_name)
    df = arrow_table.to_pandas()
    
    # Group by source to avoid random noise, just pick 1 chunk per file for demo
    sources = df['source'].unique()
    print(f"Found {len(sources)} source files.")
    
    synthetic_questions = []
    
    print("\n--- PHASE 1: GENERATING QUESTIONS (The 'Thinking' Phase) ---")
    # Limit to 3 files for speed in this demo
    for source in sources[:3]: 
        print(f"Analyzing {source}...")
        # Get random chunk from this source
        source_df = df[df['source'] == source]
        if source_df.empty: continue
        
        # Pick a nice long chunk
        sample_chunk = source_df.iloc[0]['content'][:1000] # First 1000 chars
        
        prompt = (
            f"TEXT: {sample_chunk}\n\n"
            "TASK: Generate 2 short, specific student questions about the above text.\n"
            "FORMAT: Just the questions, one per line."
        )
        
        # Use LLM to dream up questions
        try:
            response = llm.chat("You are a question generator.", prompt)
            questions = [q.strip() for q in response.split('\n') if '?' in q]
            print(f"  -> Generated: {questions}")
            synthetic_questions.extend(questions)
        except Exception as e:
            print(f"  -> Error generating: {e}")

    print(f"\n--- PHASE 2: WARMING CACHE (The 'Ingestion' Phase) ---")
    print(f"Ingesting {len(synthetic_questions)} synthetic questions into SmartCache...")
    
    for i, q in enumerate(synthetic_questions):
        if len(q) < 5: continue
        print(f"[{i+1}/{len(synthetic_questions)}] answering: {q}")
        
        start = time.time()
        # This automatically saves to cache!
        rag.answer_question(q) 
        elapsed = time.time() - start
        print(f"  -> Cached in {elapsed:.2f}s")
        
    print("\nSUCCESS: Synthetic population complete. These questions are now 0.0s latency.")

if __name__ == "__main__":
    populate_synthetic_cache()
