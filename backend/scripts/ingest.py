from teacher_assistant.src.infrastructure.database import VectorDatabase
from teacher_assistant.src.infrastructure.ollama_client import OllamaClient
from teacher_assistant.src.use_cases.ingestion import IngestionService
import os
import sys
import io

# Force UTF-8 for console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def run_full_ingestion():
    print("💎 STARTING SUPER-MICRO INGESTION (150-char chunks) 💎")
    db = VectorDatabase(db_path="./super_precise_db")
    llm = OllamaClient()
    service = IngestionService(db, llm)
    
    doc_dir = r"C:\Users\syrym\Downloads\IITU-Teacher-AI-Assistant\Управление разработкой программного обеспечения и реинжиниринг"
    
    if not os.path.exists(doc_dir):
        print(f"❌ Error: Directory not found: {doc_dir}")
        return

    service.process_directory(doc_dir)
    print("\n🚀 KNOWLEDGE BASE IS READY AND LOADED!")

if __name__ == "__main__":
    run_full_ingestion()
