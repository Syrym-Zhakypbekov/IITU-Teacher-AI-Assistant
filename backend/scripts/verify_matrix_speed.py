import numpy as np
import time

def benchmark_matrix_speed():
    print("Generating dummy data (10,000 vectors)...")
    N = 10000
    D = 768
    
    # Random library of questions
    matrix = np.random.rand(N, D).astype(np.float32)
    query = np.random.rand(D).astype(np.float32)
    
    # 1. Python Loop Simulation
    print(f"Simulating Python Loop for {N} items...")
    start = time.time()
    best_score_loop = -1
    for i in range(N):
        vec = matrix[i]
        # Cosine sim calculation
        dot = np.dot(vec, query)
        norm1 = np.linalg.norm(vec)
        norm2 = np.linalg.norm(query)
        score = dot / (norm1 * norm2)
        if score > best_score_loop:
            best_score_loop = score
    loop_time = time.time() - start
    print(f"Loop Time: {loop_time:.4f}s")
    
    # 2. Matrix Operation
    print(f"Running Matrix Math for {N} items...")
    start = time.time()
    
    # Normalize
    norm_matrix = np.linalg.norm(matrix, axis=1, keepdims=True)
    norm_query = np.linalg.norm(query)
    
    mat_norm = matrix / norm_matrix
    q_norm = query / norm_query
    
    # Dot
    scores = np.dot(mat_norm, q_norm)
    best_idx = np.argmax(scores)
    best_score_matrix = scores[best_idx]
    
    matrix_time = time.time() - start
    print(f"Matrix Time: {matrix_time:.4f}s")
    
    speedup = loop_time / matrix_time
    print(f"\nSpeedup: {speedup:.1f}x Faster")
    print(f"Scores Match: {abs(best_score_loop - best_score_matrix) < 1e-5}")

if __name__ == "__main__":
    benchmark_matrix_speed()
