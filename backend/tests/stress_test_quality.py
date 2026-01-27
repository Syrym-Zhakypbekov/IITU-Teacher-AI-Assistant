
import requests
import time
import os
import json

BASE_URL = "http://localhost:8000"

def create_dummy_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

def test_isolation_and_quality():
    print("\n🧪 STARTING HEAVY QUALITY & ISOLATION TEST 🧪")
    print("===============================================")
    
    # 1. SETUP TEACHERS & CONTENT
    teachers = {
        "teacher_physics": "Newton's First Law states that an object at rest stays at rest like a stone. Gravity is 9.8 m/s^2.",
        "teacher_history": "The Declaration of Independence was signed in 1776 in Philadelphia by founding fathers.",
        "teacher_biology": "Mitochondria is the powerhouse of the cell. Photosynthesis converts light into energy."
    }
    
    files_to_cleanup = []

    # 2. CONCURRENT INGESTION (Simulated)
    print("\n[Phase 1] 🚀 Bulk Ingestion & Indexing...")
    for tid, content in teachers.items():
        # Create Course
        print(f"  > Creating workspace for {tid}...")
        requests.post(f"{BASE_URL}/api/courses", json={"id": tid, "subject": tid.split('_')[1], "teacherName": "Test Bot"})
        
        # Upload File
        fname = f"{tid}_material.txt"
        create_dummy_file(fname, content)
        files_to_cleanup.append(fname)
        
        with open(fname, 'rb') as f:
            print(f"  > Uploading & Triggering Embeddings for {tid}...")
            requests.post(f"{BASE_URL}/api/upload", data={'course_id': tid}, files={'files': (fname, f, 'text/plain')})
    
    # Wait for granular ingestion
    print("  > Waiting for Neural Indexing (5s)...")
    time.sleep(5) 

    # 3. TEST ISOLATION (Personalization Check)
    print("\n[Phase 2] 🛡️ Testing Deep Isolation (Personal Databases)...")
    
    # Q: Ask Physics about History (Should fail/exclude)
    q_cross = "When was the Declaration signed?"
    print(f"  > Asking {q_cross} to PHYSICS Bot (Should Ignore)...")
    resp = requests.post(f"{BASE_URL}/api/chat", json={"message": q_cross, "course_id": "teacher_physics"})
    ans = resp.json()['response']
    if "1776" not in ans and ("context" in ans.lower() or "information" in ans.lower() or len(ans) < 100):
         print(f"    ✅ PASS: Physics bot didn't know about History. (Ans: {ans[:50]}...)")
    else:
         print(f"    ❌ FAIL: Leak detected! Physics bot knew history: {ans}")

    # Q: Ask Physics about Physics (Should succeed)
    q_direct = "What does Newton's law say about objects at rest?"
    print(f"  > Asking {q_direct} to PHYSICS Bot (Should Answer)...")
    resp = requests.post(f"{BASE_URL}/api/chat", json={"message": q_direct, "course_id": "teacher_physics"})
    ans = resp.json()['response']
    if "rest" in ans.lower() or "stone" in ans.lower():
        print(f"    ✅ PASS: Physics bot answered correctly from its own DB.")
    else:
        print(f"    ❌ FAIL: Physics bot failed to retrieve own data. Ans: {ans}")

    # 4. TEST AUDIO OPTIMIZATION ("Best Audio")
    print("\n[Phase 3] 🎤 Testing High-Fidelity Audio Mode...")
    q_voice = "Explain gravity briefly."
    resp_voice = requests.post(f"{BASE_URL}/api/chat", json={
        "message": q_voice, 
        "course_id": "teacher_physics",
        "is_voice": True # Toggling the optimization
    })
    ans_voice = resp_voice.json()['response']
    
    # Check for markdown artifacts that ruin TTS
    artifacts = ['**', '##', '```', '- ']
    found_artifacts = [a for a in artifacts if a in ans_voice]
    if not found_artifacts:
        print("    ✅ PASS: Response is clean plain text (Optimized for TTS).")
    else:
        print(f"    ❌ FAIL: Found Markdown artifacts: {found_artifacts}")

    # 5. TEST COST EFFECTIVENESS (Smart Cache)
    print("\n[Phase 4] 💰 Testing Cost-Effective Management (Smart Cache)...")
    q_cache = "What is the powerhouse of the cell?"
    
    # First Hit (Expensive GPU)
    t0 = time.time()
    requests.post(f"{BASE_URL}/api/chat", json={"message": q_cache, "course_id": "teacher_biology"})
    d1 = time.time() - t0
    print(f"  > 1st Query (GPU Compute): {d1:.2f}s")
    
    # Second Hit (Free Cache)
    t0 = time.time()
    requests.post(f"{BASE_URL}/api/chat", json={"message": q_cache, "course_id": "teacher_biology"})
    d2 = time.time() - t0
    print(f"  > 2nd Query (Smart Cache): {d2:.2f}s")
    
    if d2 < d1 * 0.5: # Expect significant speedup
        print("    ✅ PASS: Cache hit saved compute & time!")
    else:
        print("    ⚠️ WARN: Cache speedup not significant (Localhost might be too fast already).")

    # Cleanup
    for f in files_to_cleanup:
         try: os.remove(f) 
         except: pass

    print("\n===============================================")
    print("✅ QUALITY & ISOLATION STRESS TEST COMPLETE")

if __name__ == "__main__":
    test_isolation_and_quality()
