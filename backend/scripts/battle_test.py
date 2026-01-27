import os
import requests
import time
import sys
import io
import re

# Force UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://127.0.0.1:8000"
DOC_DIR = r"C:\Users\syrym\Downloads\IITU-Teacher-AI-Assistant\Управление разработкой программного обеспечения и реинжиниринг"

def normalize_filename(name):
    """Normalize filename for comparison (removes -eng, numbers, etc.)"""
    name = name.lower()
    for ext in [".pptx", ".docx", ".pdf"]:
        name = name.replace(ext, "")
    # Remove common suffixes
    name = re.sub(r'\s*-\s*(eng|rus|summary|план|иллюстр\.сцен\.прецедентов)', '', name)
    # Remove leading numbers
    name = re.sub(r'^\d+\s*[-–]\s*', '', name)
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def generate_question_from_filename(fname):
    """Generate a question based on the filename topic."""
    topic = fname
    for ext in [".pptx", ".docx", ".pdf"]:
        topic = topic.replace(ext, "")
    topic = re.sub(r'^\d+\s*[-–]\s*', '', topic)
    # Remove -eng suffix for cleaner question
    topic = re.sub(r'\s*-\s*eng$', '', topic).strip()
    if len(topic) < 3:
        topic = fname
    return f"What is {topic}?"

def run_battle_test():
    print("⚔️ BATTLE TEST (Fuzzy Matching) ⚔️\n")

    files = []
    for root, _, filenames in os.walk(DOC_DIR):
        for fname in filenames:
            if fname.lower().endswith(('.pdf', '.pptx', '.docx')):
                files.append(os.path.join(root, fname))

    results = []
    
    for i, fpath in enumerate(files):
        fname = os.path.basename(fpath)
        question = generate_question_from_filename(fname)
        normalized_target = normalize_filename(fname)
        
        print(f"[{i+1}/{len(files)}] {fname}")
        print(f"   Q: {question}")
        
        start = time.time()
        try:
            r = requests.post(f"{BASE_URL}/api/chat", json={"message": question}, timeout=60)
            latency = time.time() - start
            
            if r.status_code == 200:
                resp = r.json()
                # FUZZY MATCH: Check if any cited file matches normalized target
                cited = False
                for ref in resp['references']:
                    ref_file = ref.split(" | ")[0]
                    normalized_ref = normalize_filename(ref_file)
                    # Check if normalized names match OR one contains the other
                    if normalized_target in normalized_ref or normalized_ref in normalized_target:
                        cited = True
                        break
                
                status = "✅ PASS" if cited else "❌ MISS"
                cited_files = [ref.split(" | ")[0] for ref in resp['references'][:3]]
                print(f"   {status} | {latency:.1f}s | Cited: {cited_files}")
                results.append((fname, cited, latency))
            else:
                print(f"   ❌ API Error: {r.status_code}")
                results.append((fname, False, 0))
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append((fname, False, 0))
        
        print("-" * 50)

    # Final Summary
    passed = sum(1 for r in results if r[1])
    total = len(results)
    avg_lat = sum(r[2] for r in results) / total if total else 0
    
    print("\n" + "=" * 50)
    print(f"🏆 FINAL SCORE: {passed}/{total} ({100*passed/total:.0f}%)")
    print(f"⏱️ Average Latency: {avg_lat:.2f}s")
    print("=" * 50)

if __name__ == "__main__":
    run_battle_test()
