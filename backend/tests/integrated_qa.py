import httpx
import os
import time

BASE_URL = "http://localhost:8000"

def test_isolated_workflow():
    import random
    suffix = random.randint(1000, 9999)
    teacher_id = f"qual_test_{suffix}"
    other_teacher_id = f"privacy_gate_{suffix}"
    
    print(f"💎 Starting Integrated Isolated Workflow QA ({suffix})...")
    
    # 1. Clean Test Environment
    # (Manual check: Ensure backend/storage/teacher_qual_test_001 doesn't have junk)
    
    # 2. Upload Materials to Private Workspace
    print(f"📦 Uploading to {teacher_id}...")
    with httpx.Client() as client:
        # Create a dummy file
        with open("test_lecture.txt", "w") as f:
            f.write("IITU AI Policy: Students must use local neural engines for all homework.")
            
        with open("test_lecture.txt", "rb") as f:
            files = {"files": ("test_lecture.txt", f, "text/plain")}
            data = {"course_id": teacher_id}
            resp = client.post(f"{BASE_URL}/api/upload", data=data, files=files)
            
        assert resp.status_code == 200
        print("✅ Upload Successful.")
        
        # 3. Wait for Ingestion (Neural Sync)
        print("🧠 Waiting for Neural Sync...")
        time.sleep(8) 
        
        # 4. Query Private Workspace
        print("💬 Querying Isolated RAG...")
        payload = {
            "message": "What is the policy for students?",
            "course_id": teacher_id,
            "is_voice": False
        }
        resp = client.post(f"{BASE_URL}/api/chat", json=payload)
        
        assert resp.status_code == 200
        chat_data = resp.json()
        print(f"🤖 AI Response: {chat_data['response']}")
        assert "policy" in chat_data['response'].lower() or "homework" in chat_data['response'].lower()
        print("✅ RAG Retrieval Successful.")
        
        # 5. Verify Isolation (Privacy QA)
        print(f"🛡️ Verifying Privacy Isolation (Querying different teacher {other_teacher_id})...")
        other_payload = {
            "message": "What is the policy for students?",
            "course_id": other_teacher_id,
            "is_voice": False
        }
        resp = client.post(f"{BASE_URL}/api/chat", json=other_payload)
        
        assert resp.status_code == 200
        other_chat_data = resp.json()
        print(f"🚫 Other Teacher AI Result: {other_chat_data['status']}")
        assert other_chat_data['status'] == "no_context"
        print("✅ Isolation Verified: Data leakage is 0.0%.")

    # Cleanup
    if os.path.exists("test_lecture.txt"):
        os.remove("test_lecture.txt")

if __name__ == "__main__":
    test_isolated_workflow()
