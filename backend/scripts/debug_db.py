import lancedb
import pandas as pd
import ollama
import sys

# Path from database.py
DB_PATH = "./super_precise_db"
TABLE_NAME = "knowledge_base"

def log(msg, f):
    f.write(msg + "\n")
    print(msg) # Still print for status, might fail but file should write

def check_db():
    with open("debug_log.txt", "w", encoding="utf-8") as f:
        log(f"Connecting to {DB_PATH}...", f)
        try:
            db = lancedb.connect(DB_PATH)
        except Exception as e:
            log(f"Error connecting to DB: {e}", f)
            return

        if TABLE_NAME not in db.table_names():
            log(f"Table {TABLE_NAME} not found!", f)
            return

        tbl = db.open_table(TABLE_NAME)
        log(f"Total rows: {len(tbl)}", f)

        # Check distinct sources
        df = tbl.to_pandas()
        sources = df['source'].unique()
        log(f"\nTotal unique files: {len(sources)}", f)
        
        target_file_1 = "Практическая работа 4"
        target_file_2 = "Practical work 5"
        
        log(f"\n--- Checking for '{target_file_1}' ---", f)
        matches = [str(s) for s in sources if target_file_1.lower() in str(s).lower()]
        log(f"Found filenames: {matches}", f)

        log(f"\n--- Checking for '{target_file_2}' ---", f)
        matches = [str(s) for s in sources if target_file_2.lower() in str(s).lower()]
        log(f"Found filenames: {matches}", f)
        
        # Test Search
        log("\n--- Testing Search Retrieval ---", f)
        query = "What is Практическая работа 4 - иллюстр.сцен.прецедентов?"
        log(f"Query: {query}", f)
        
        try:
            embedding = ollama.embed(model="nomic-embed-text", input=query)['embeddings'][0]
            
            # Standard search
            results = tbl.search(embedding).limit(50).to_pandas()
            log("\nTop 50 Search Results (Source | Content Snippet):", f)
            for i, row in results.iterrows():
                log(f"{i+1}. [{row['source']}] {row['content'][:50]}... (Dist: {row['_distance']:.4f})", f)
                
        except Exception as e:
            log(f"Search failed: {e}", f)

if __name__ == "__main__":
    check_db()
