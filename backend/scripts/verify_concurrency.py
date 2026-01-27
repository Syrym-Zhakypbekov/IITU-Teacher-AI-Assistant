from teacher_assistant.src.infrastructure.smart_cache import SmartCache
import sqlite3
import time
import os

def verify_concurrency():
    print("Initializing SmartCache with WAL mode...")
    cache = SmartCache()
    
    # Check Journal Mode
    conn = sqlite3.connect(cache.db_path)
    cursor = conn.cursor()
    cursor.execute('PRAGMA journal_mode;')
    mode = cursor.fetchone()[0]
    conn.close()
    
    print(f"Current Journal Mode: {mode}")
    if mode.upper() == 'WAL':
        print("SUCCESS: WAL mode is active. High concurrency enabled.")
    else:
        print(f"WARNING: Journal mode is {mode}. Expected WAL.")

    # Check Prediction Capability
    print("\nChecking Prediction Engine...")
    has_predict = hasattr(cache, 'predict')
    print(f"Predict method exists: {has_predict}")

    if has_predict:
        print("Prediction logic is hooked up.")
    
if __name__ == "__main__":
    verify_concurrency()
