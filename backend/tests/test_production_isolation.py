import httpx
import time
import os
import concurrent.futures

BASE_URL = "http://localhost:8000"

def test_teacher_lifecycle_stress():
    print("💎 STARTING PRODUCTION ISOLATION & STRESS QA...")
    
    t1_id = "teacher_physics_001"
    t2_id = "teacher_lit_002"
    
    with httpx.Client(timeout=30.0) as client:
        # 1. Create Isolated Workspaces
        print("🏗️ Creating Physics Workspace...")
        client.post(f"{BASE_URL}/api/courses", json={
            "id": t1_id, "subject": "Quantum Physics", "teacherName": "Dr. Bohr", "teacherId": "t1"
        })
        
        print("🏗️ Creating Literature Workspace...")
        client.post(f"{BASE_URL}/api/courses", json={
            "id": t2_id, "subject": "Modern Poetry", "teacherName": "Prof. Yeats", "teacherId": "t2"
        })

        # 2. Parallel Uploads & Indexing
        def upload_and_wait(teacher_id, content):
            file_path = f"{teacher_id}_syllabus.txt"
            with open(file_path, "w") as f:
                f.write(content)
            
            print(f"📦 [{teacher_id}] Uploading content...")
            with open(file_path, "rb") as f:
                client.post(f"{BASE_URL}/api/upload", 
                            data={"course_id": teacher_id},
                            files={"files": (f"{teacher_id}.txt", f)})
            
            os.remove(file_path)
            
            # Start Ingest
            client.post(f"{BASE_URL}/api/ingest/{teacher_id}")
            
            # 3. Poll Progress
            print(f"🧠 [{teacher_id}] Monitoring Neural Progress...")
            for _ in range(20):
                resp = client.get(f"{BASE_URL}/api/ingest/status/{teacher_id}")
                data = resp.json()
                print(f"📊 [{teacher_id}] Progress: {data['progress']}% | Status: {data['status']}")
                if data['status'] == "ready":
                    break
                time.sleep(2)
            return True

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(upload_and_wait, t1_id, "PHYSICS_SECRET: The cat is both dead and alive."),
                executor.submit(upload_and_wait, t2_id, "POETRY_SECRET: The rose is the symbol of love.")
            ]
            concurrent.futures.wait(futures)

        # 4. CROSS-TEANANT LEAKAGE TEST (The 'No Broke Shit' Proof)
        print("🔍 [QA] Verifying Content Isolation...")
        
        # Physics teacher should NOT see Poetry
        resp = client.post(f"{BASE_URL}/api/chat", json={
            "course_id": t1_id, "message": "What is the symbol of love?"
        })
        print(f"🤖 Physics AI Response: {resp.json()['response']}")
        assert "rose" not in resp.json()['response'].lower()
        
        # Poetry teacher should NOT see Physics
        resp = client.post(f"{BASE_URL}/api/chat", json={
            "course_id": t2_id, "message": "What is the status of the cat?"
        })
        print(f"🤖 Poetry AI Response: {resp.json()['response']}")
        assert "dead" not in resp.json()['response'].lower()
        
        print("✅ PRODUCTION ISOLATION QA PASSED.")

if __name__ == "__main__":
    test_teacher_lifecycle_stress()
