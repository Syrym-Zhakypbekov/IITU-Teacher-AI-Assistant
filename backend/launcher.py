import os
import subprocess
import time

def set_ollama_envs():
    print("🛠️  Configuring 2026 Parallelism Optimized Environment...")
    
    # Enable Quantized KV Cache for 10 users (4x memory compression)
    os.environ["OLLAMA_KV_CACHE_TYPE"] = "q4_0"
    
    # Enable Flash Attention for fast context processing
    os.environ["OLLAMA_FLASH_ATTENTION"] = "1"
    
    # Set Parallel requests to handle interleaving
    os.environ["OLLAMA_NUM_PARALLEL"] = "4"
    
    print("✅ OLLAMA_KV_CACHE_TYPE=q4_0")
    print("✅ OLLAMA_FLASH_ATTENTION=1")
    print("✅ OLLAMA_NUM_PARALLEL=4")

def launch_server():
    set_ollama_envs()
    
    print("\n🚀 Starting Teacher Assistant RAG Launcher...")
    print("--------------------------------------------------")
    print("Device Mix Strategy:")
    print("  - Guard (1B): CPU [0 GPU Layers]")
    print("  - Search (8B): MIX [15 GPU Layers]")
    print("  - Judge (8B):  GPU [40 GPU Layers]")
    print("  - Speaker (3B): GPU [40 GPU Layers]")
    print("--------------------------------------------------")
    
    try:
        # Run the test main script
        import teacher_assistant.main as main_app
        main_app.setup_demo()
        
        # Test queries
        queries = [
            "Tell me about Dr. Syrym Zhakypbekov's lecture on Blockchain",
            "What does Syrym teach?" # This will trigger the collision check
        ]
        
        for q in queries:
            engine = main_app.setup_demo() # Reload for clean test
            main_app.run_test(engine, q)
            
    except Exception as e:
        print(f"❌ Error during launch: {e}")

if __name__ == "__main__":
    launch_server()
