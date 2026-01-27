from teacher_assistant.src.use_cases.rag_engine import RAGService
from teacher_assistant.src.infrastructure.database import VectorDatabase
from teacher_assistant.src.infrastructure.ollama_client import OllamaClient
import time

def verify_cost():
    print("Initializing components...")
    db = VectorDatabase()
    llm = OllamaClient()
    rag = RAGService(db, llm)
    
    # Test 1: Simple Greeting (Should skip RAG)
    print("\n--- Test 1: Simple Greeting ---")
    q1 = "Hi"
    start = time.time()
    res1 = rag.answer_question(q1)
    elapsed = time.time() - start
    print(f"Query: {q1}")
    print(f"Status: {res1.status}") # Expected: chat_simple
    print(f"Time: {elapsed:.2f}s")
    
    # Test 2: Precise Query (Should use precision mode)
    print("\n--- Test 2: Precise Query ---")
    q2 = "What is Практическая работа 4 - иллюстр.сцен.прецедентов?"
    start = time.time()
    res2 = rag.answer_question(q2)
    elapsed = time.time() - start
    print(f"Query: {q2}")
    print(f"Status: {res2.status}") # Expected: generated_precision_sniper (or cached/semantic if run before)
    print(f"Time: {elapsed:.2f}s")
    
    # Test 3: Complex Query (Should use deep dive)
    print("\n--- Test 3: Complex/Vague Query ---")
    q3 = "Explain the difference between functional and non-functional requirements"
    start = time.time()
    res3 = rag.answer_question(q3)
    elapsed = time.time() - start
    print(f"Query: {q3}")
    print(f"Status: {res3.status}") # Expected: generated_deep_dive
    print(f"Time: {elapsed:.2f}s")

if __name__ == "__main__":
    verify_cost()
