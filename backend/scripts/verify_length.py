from teacher_assistant.src.infrastructure.ollama_client import OllamaClient
import time

def verify_length():
    print("Initializing Ollama Client...")
    llm = OllamaClient()
    
    # Ask a question that requires a long answer
    system_prompt = "You are a helpful assistant. Answer in detail."
    question = "Explain the history of the internet from 1960 to 2000 in comprehensive detail, covering ARPANET, TCP/IP, and the WWW."
    
    print(f"\n--- Testing Response Length ---\nQ: {question}")
    
    start = time.time()
    response = llm.chat(system_prompt, question)
    elapsed = time.time() - start
    
    print(f"\nTime: {elapsed:.2f}s")
    print(f"Response Length: {len(response)} chars")
    print(f"Ends with punctuation? {response.strip()[-1] in '.!?\"'}")
    print(f"\nLast 100 chars:\n{response[-100:]}")
    
    if len(response) > 500 and response.strip()[-1] in '.!?"':
        print("\nSUCCESS: Response is long and properly terminated.")
    else:
        print("\nWARNING: Response might be short or cut off.")

if __name__ == "__main__":
    verify_length()
