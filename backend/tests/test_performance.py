import pytest
import time
import statistics
from teacher_assistant.src.infrastructure.workspace import WorkspaceManager
from teacher_assistant.src.infrastructure.ollama_client import OllamaClient
from teacher_assistant.src.use_cases.rag_engine import RAGService

@pytest.mark.performance
def test_rag_throughput_and_latency():
    """
    Performance QA: Measure latency and proving efficiency of SmartCache.
    Goal: High throughput, cost-effective caching.
    """
    manager = WorkspaceManager(base_dir="./test_perf_storage")
    llm = OllamaClient()
    db = manager.get_database("perf_test")
    rag = RAGService(db, llm)
    
    # 1. First Run (Cold Start - GPU Inferred)
    start_time = time.time()
    query = "What is the policy?"
    rag.answer_question(query)
    cold_latency = time.time() - start_time
    
    # 2. Second Run (Warm Start - Semantic Cache)
    latencies = []
    for _ in range(10):
        start_time = time.time()
        rag.answer_question(query)
        latencies.append(time.time() - start_time)
    
    avg_warm_latency = sum(latencies) / len(latencies)
    
    # Proof of Cost Efficiency: Cache should be at least 10x faster than GPU inference
    print(f"\nCold Latency: {cold_latency:.4f}s")
    print(f"Avg Warm Latency: {avg_warm_latency:.4f}s")
    
    assert avg_warm_latency < cold_latency / 10
    
@pytest.mark.performance
def test_smart_budgeting_context_load():
    """
    QA: Verify that SmartCostManager correctly reduces context window 
    to save CPU/Tokens for high-confidence matches.
    """
    from teacher_assistant.src.core.cost_manager import SmartCostManager
    import pandas as pd
    
    cm = SmartCostManager()
    
    # Mock search results with high score
    precise_results = pd.DataFrame([{ 'smart_score': 25, 'content': 'Direct Answer', 'source': 'a.pdf', 'location': 'p1' }])
    budget = cm.allocate_budget(precise_results)
    assert budget['mode'] == 'precision_sniper'
    assert budget['max_context'] == 2000
    
    # Mock weak results
    weak_results = pd.DataFrame([{ 'smart_score': 2, 'content': 'Noise', 'source': 'b.pdf', 'location': 'p1' }])
    budget = cm.allocate_budget(weak_results)
    assert budget['mode'] == 'deep_dive'
    assert budget['max_context'] == 8000
