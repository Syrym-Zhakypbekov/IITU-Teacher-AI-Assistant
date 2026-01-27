from teacher_assistant.src.use_cases.rag_engine import RAGService
from teacher_assistant.src.infrastructure.database import VectorDatabase
from teacher_assistant.src.infrastructure.ollama_client import OllamaClient
from teacher_assistant.src.infrastructure.smart_cache import SmartCache
import time

def benchmark():
    print("Initializing components...")
    db = VectorDatabase()
    llm = OllamaClient()
    rag = RAGService(db, llm)
    
    # Cache clear to ensure clean test? 
    # No, user wants to see "save it and then recall it". 
    # But for a benchmark, we should probably start clean or known state.
    # We will manually clean just for this test run logic if needed, but let's assume persistent is fine.
    
    questions = [
        ("What are the key concepts of software requirements?", "requirements concepts"),
        ("How do you identify software requirements?", "identifying requirements"),
        ("Explain Use Case Specification.", "use case spec"),
        ("What is a User Story?", "define user story"),
        ("Describe the deployment diagram purpose.", "deployment diagram"),
        ("What is involved in interface design?", "interface design"),
        ("Explain defect reports in testing.", "defect reporting"),
        ("What are the main project management activities?", "project management"),
        ("Difference between functional and non-functional requirements?", "func vs non-func"),
        ("What is the role of stakeholders?", "stakeholders role"),
    ]
    
    print(f"\n=== ROUND 1: COLD GENERATION (CPU/GPU Heavy) ===")
    print("Generating answers for 10 new questions...")
    
    cold_times = []
    
    for i, (q, topic) in enumerate(questions):
        print(f"\n{i+1}. {topic}...", end="", flush=True)
        start = time.time()
        res = rag.answer_question(q)
        elapsed = time.time() - start
        cold_times.append(elapsed)
        print(f" DONE ({elapsed:.2f}s) | Status: {res.status}")

    avg_cold = sum(cold_times) / len(cold_times)
    print(f"\n>>> Avg Cold Time: {avg_cold:.2f}s")
    print(f">>> Total Cold Time: {sum(cold_times):.2f}s")

    print(f"\n=== ROUND 2: PREDICTION (Semantic Cache) ===")
    print("Asking similar/rephrased questions to test Prediction Engine...")
    
    # Rephrased versions to test semantic math
    rephrased_questions = [
        "Tell me about the main concepts of requirements.",
        "Methods for identifying requirements in software.",
        "Details of Use Case Specs.",
        "Define User Stories.",
        "Purpose of deployment diagrams?",
        "Designing user interfaces.",
        "How to report defects?",
        "Project management main tasks.",
        "Functional vs Non-functional requirements differences.",
        "Who are stakeholders?"
    ]
    
    warm_times = []
    
    for i, q_rephrased in enumerate(rephrased_questions):
        print(f"\n{i+1}. {q_rephrased[:30]}...", end="", flush=True)
        start = time.time()
        res = rag.answer_question(q_rephrased)
        elapsed = time.time() - start
        warm_times.append(elapsed)
        
        status_tag = "PREDICTED" if "cached" in res.status or "Cached" in res.response else "GENERATED (Miss)"
        print(f" DONE ({elapsed:.2f}s) | Status: {res.status} -> {status_tag}")

    avg_warm = sum(warm_times) / len(warm_times)
    print(f"\n>>> Avg Predicted Time: {avg_warm:.2f}s")
    print(f">>> Total Predicted Time: {sum(warm_times):.2f}s")
    
    speedup = avg_cold / avg_warm if avg_warm > 0 else 999
    print(f"\n=== RESULTS ===")
    print(f"Speedup Factor: {speedup:.1f}x Faster")

if __name__ == "__main__":
    benchmark()
