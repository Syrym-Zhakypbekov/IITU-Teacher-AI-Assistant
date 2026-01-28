import os
import sys
import time
import json
from teacher_assistant.src.infrastructure.database import VectorDatabase
from teacher_assistant.src.infrastructure.ollama_client import OllamaClient
from teacher_assistant.src.infrastructure.smart_cache import SmartCache
from teacher_assistant.src.use_cases.rag_engine import RAGService
from teacher_assistant.src.infrastructure.workspace import WorkspaceManager

def run_qa():
    # Set stdout to use utf-8 if possible, but writing to file is safer
    print("Starting QA Test Session with Gemma 3 4B...")
    
    llm = OllamaClient()
    workspace_manager = WorkspaceManager(base_dir="./storage")
    legacy_db_path = os.path.abspath("super_precise_db")
    
    workspace_manager.mount_database(
        course_id="legacy_qa",
        db_path=legacy_db_path,
        metadata={"subject": "Software Engineering & Reengineering"}
    )
    
    db = workspace_manager.get_database("legacy_qa")
    cache = SmartCache(db_path="./storage/cache_qa.db")
    rag = RAGService(db, llm, cache)
    
    test_questions = [
        "What are the recommended tools for project management in this course?",
        "Что такое ожидаемый и фактический результат в контексте отчетов о дефектах?",
        "Explain the impact of changes on the project and the end user.",
        "Из-за каких внешних условий могут возникать отказы в системе?",
        "What is the point rating system for laboratory work?"
    ]
    
    results = []
    
    for q in test_questions:
        print(f"Processing: {q[:50]}...")
        response = rag.answer_question(q)
        
        results.append({
            "question": q,
            "answer": response.response,
            "references": response.references,
            "status": response.status
        })
        
    # Write to UTF-8 file
    with open("qa_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\nQA Test Complete. Results saved to qa_report.json")

if __name__ == "__main__":
    run_qa()
