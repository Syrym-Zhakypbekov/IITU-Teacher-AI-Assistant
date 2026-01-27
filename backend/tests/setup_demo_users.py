
from teacher_assistant.src.infrastructure.relational_db import RelationalDatabase
import hashlib
import binascii
import os

# Helper to match the pbkdf2_sha256 logic if needed, 
# but better to use the auth_service functions if possible.
# However, to be standalone, I'll replicate the hash or just import.

# Let's try to import from auth_service to ensure consistency
try:
    from auth_service import get_password_hash, create_user, get_user_by_email
except ImportError:
    # If not in path, we manually setup path or mock
    import sys
    sys.path.append(".")
    from auth_service import get_password_hash, create_user, get_user_by_email

def setup_users():
    print("👤 Setting up Demo Users...")
    
    users = [
        {"email": "admin@iitu.kz", "password": "admin123", "name": "System Admin", "role": "admin"},
        {"email": "teacher.demo@iitu.kz", "password": "teacher123", "name": "Professor AI", "role": "teacher"},
        {"email": "student.demo@iitu.kz", "password": "student123", "name": "Student A", "role": "student"}
    ]
    
    for u in users:
        existing = get_user_by_email(u["email"])
        if existing:
            print(f"   ✅ Found existing: {u['role'].upper()} ({u['email']})")
            # In a real scenario we might reset password, but here we assume it's stable or just re-create
            # For demo, let's keep it. 
        else:
            print(f"   ✨ Creating new: {u['role'].upper()}...")
            create_user(u["email"], u["password"], u["name"], u["role"])
            print(f"      Use Password: {u['password']}")

    print("\n🎉 DEMO CREDENTIALS READY:")
    print("=============================================")
    for u in users:
        print(f"ROLE: {u['role'].ljust(8)} | EMAIL: {u['email'].ljust(25)} | PASS: {u['password']}")
    print("=============================================")

if __name__ == "__main__":
    setup_users()
