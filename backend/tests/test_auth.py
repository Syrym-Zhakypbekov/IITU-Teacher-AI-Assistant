
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_auth_and_roles():
    print("🔐 TEST: Authentication & Role-Based Access Control (RBAC) 🔐")
    print("==============================================================")
    
    # 1. Register Admin
    print("\n[Admin] Registering Super Admin...")
    adm_email = "admin.test@iitu.kz"
    adm_pass = "superadmin123"
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": adm_email, "password": adm_pass, "name": "Super Admin"
        })
        print(f"  > Register status: {resp.status_code} ({resp.json()})")
    except Exception as e:
        print(f"  > Failed: {e}")

    # 2. Login Admin & Get Token
    print("\n[Admin] Logging in...")
    admin_token = None
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": adm_email, "password": adm_pass})
    if resp.status_code == 200:
        admin_token = resp.json()["token"]
        print(f"  > Login SUCCESS. Token: {admin_token[:15]}...")
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
    else:
        print("  ❌ FATAL: Admin login failed.")
        return

    # 3. Register Teacher
    print("\n[Teacher] Registering...")
    teacher_email = "teacher.math@iitu.kz"
    try:
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": teacher_email, "password": "pass", "name": "Math Teacher"
        })
    except: pass
    
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": teacher_email, "password": "pass"})
    teacher_token = resp.json()["token"]
    headers_teacher = {"Authorization": f"Bearer {teacher_token}"}
    print(f"  > Teacher Token: {teacher_token[:15]}...")

    # 4. Register Student
    print("\n[Student] Registering...")
    student_email = "student.bob@iitu.kz"
    try:
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": student_email, "password": "pass", "name": "Bob Student"
        })
    except: pass

    resp = requests.post(f"{BASE_URL}/api/auth/login", json={"email": student_email, "password": "pass"})
    student_token = resp.json()["token"]
    headers_student = {"Authorization": f"Bearer {student_token}"}
    print(f"  > Student Token: {student_token[:15]}...")

    # 5. RBAC TEST: Create Course (Teacher Only)
    print("\n--------- RBAC: Create Course ---------")
    
    # Student attempts (Should Fail 403)
    resp = requests.post(f"{BASE_URL}/api/courses", json={"id": "rbac_test_1", "subject": "RBAC", "teacherName": "T", "teacherId": "t1"}, headers=headers_student)
    if resp.status_code == 403:
        print("  ✅ PASS: Student blocked from creating course.")
    else:
        print(f"  ❌ FAIL: Student allowed? Code: {resp.status_code}")

    # Teacher attempts (Should Pass 200)
    resp = requests.post(f"{BASE_URL}/api/courses", json={"id": "rbac_test_1", "subject": "RBAC", "teacherName": "T", "teacherId": "t1"}, headers=headers_teacher)
    if resp.status_code == 200:
        print("  ✅ PASS: Teacher allowed to create course.")
    else:
        print(f"  ❌ FAIL: Teacher blocked? Code: {resp.status_code} - {resp.text}")

    # 6. RBAC TEST: Delete User (Admin Only)
    print("\n--------- RBAC: Delete User (Admin) ---------")
    
    # Teacher attempts delete (Should Fail 403)
    resp = requests.delete(f"{BASE_URL}/api/admin/users/{student_email}", headers=headers_teacher)
    if resp.status_code == 403:
        print("  ✅ PASS: Teacher blocked from deleting user.")
    else:
        print(f"  ❌ FAIL: Teacher allowed to delete user? Code: {resp.status_code}")
        
    # Admin attempts delete (Should Pass)
    resp = requests.delete(f"{BASE_URL}/api/admin/users/{student_email}", headers=headers_admin)
    if resp.status_code == 200:
        print("  ✅ PASS: Admin deleted student user.")
    else:
        print(f"  ❌ FAIL: Admin failed to delete user. Code: {resp.status_code}")

    print("\n✅ AUTH & RBAC TEST COMPLETE")

if __name__ == "__main__":
    test_auth_and_roles()
