import ollama
import lancedb
import json
import os
import pandas as pd

# --- CONFIGURATION ---
DB_PATH = "./simple_lancedb"
COLLECTION_NAME = "tutors"
EMBED_MODEL = "nomic-embed-text" # Small, fast, standard
CHAT_MODEL = "ministral-3:3b"

# --- DATABASE SETUP ---
db = lancedb.connect(DB_PATH)

def ingest_data(json_file):
    print(f"📥 Loading data from {json_file}...")
    with open(json_file, "r") as f:
        data = json.load(f)
    
    # Generate embeddings and prepare data
    records = []
    for item in data:
        print(f"  Encoding: {item['tutor']}...")
        item['vector'] = ollama.embed(model=EMBED_MODEL, input=item['content']).embeddings[0]
        records.append(item)
    
    # Create table with FTS
    tbl = db.create_table(COLLECTION_NAME, data=records, mode="overwrite")
    tbl.create_fts_index("content")
    print("✅ Indexing Complete!")

def ask_question(query):
    # 1. Get Embedding (Single call)
    query_vec = ollama.embed(model=EMBED_MODEL, input=query).embeddings[0]
    
    # 2. Hybrid Search (Database logic, very fast)
    tbl = db.open_table(COLLECTION_NAME)
    results = tbl.search(query_vec).limit(3).to_pandas()
    
    if results.empty:
        return "Sorry, I don't know about that."

    # 3. Format Context
    context = "\n\n".join([f"Teacher: {r['tutor']}\nTopic: {r['topic']}\nInfo: {r['content']}" for _, r in results.iterrows()])
    
    # 4. Final Chat (Single call)
    system_prompt = (
        "You are a helpful Teacher Assistant. Use only the provided context. "
        "If multiple teachers have similar names, list them and ask for clarification. "
        "Be concise."
    )
    
    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"Context:\n{context}\n\nQuestion: {query}"}
        ]
    )
    return response.message.content

# --- TEST RUN ---
if __name__ == "__main__":
    # 1. Create dummy data if not exists
    test_data = [
        {"tutor": "Dr. Syrym Zhakypbekov", "topic": "Blockchain", "content": "Advanced lecture on Ethereum and Java EE integration."},
        {"tutor": "Dr. Syrym Zhakypov", "topic": "Blockchain", "content": "Introductory guide to basic crypto-wallets."},
        {"tutor": "S. Zhakypbekov", "topic": "Math", "content": "Linear algebra and its application in circuits."}
    ]
    with open("dummy.json", "w") as f:
        json.dump(test_data, f)
    
    # 2. Ingest
    ingest_data("dummy.json")
    
    # 3. Test
    print("\n🔍 Query: 'Tell me about Syrym'")
    print(f"🤖 Response: {ask_question('Tell me about Syrym')}")
