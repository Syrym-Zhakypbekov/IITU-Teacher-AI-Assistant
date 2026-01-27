from teacher_assistant.src.use_cases.rag_engine import RAGService
from teacher_assistant.src.infrastructure.database import VectorDatabase
from teacher_assistant.src.infrastructure.ollama_client import OllamaClient
import time

def verify():
    print("Initializing components...")
    db = VectorDatabase()
    llm = OllamaClient()
    rag = RAGService(db, llm)
    
    # Test 1: Cold start (should perform search)
    question = "What is Практическая работа 4 - иллюстр.сцен.прецедентов?"
    print(f"\n--- Test 1: Cold Query ---\nQ: {question}")
    
    start = time.time()
    response = rag.answer_question(question)
    elapsed = time.time() - start
    
    print(f"Time: {elapsed:.2f}s")
    print(f"Status: {response.status}")
    print(f"Response snippet: {response.response[:100]}...")
    print(f"References: {len(response.references)}")
    
    # Test 2: Semantic Cache Hit
    question_sem = "Tell me about Practical Work 4 Use Case Scenarios" # English, slightly different
    print(f"\n--- Test 2: Semantic Cache Query ---\nQ: {question_sem}")
    
    start = time.time()
    response_sem = rag.answer_question(question_sem)
    elapsed_sem = time.time() - start
    
    print(f"Time: {elapsed_sem:.2f}s")
    print(f"Status: {response_sem.status}") # Should be 'cached'
    print(f"Response snippet: {response_sem.response[:100]}...")
    
    if "Cached (Semantic" in response_sem.response or  "Cached (Semantic" in str(response_sem):
        print("SUCCESS: Semantic cache hit!")
    else:
        print("NOTE: Might not be similar enough or semantic threshold too high. Check logs.")

if __name__ == "__main__":
    verify()
