import ollama
from typing import List, Dict

class OllamaProvider:
    def __init__(self):
        self.embed_model = "qwen3-embedding:latest"
        self.chat_model = "ministral-3:3b"
        self.rerank_model = "dengcao/Qwen3-Reranker-8B:Q4_K_M"
        self.guard_model = "llama3.2:1b"

    def get_embedding(self, text: str) -> List[float]:
        # CPU/GPU Mix: We offload some work to prevent GPU bottleneck
        # Instruct: 2026 standard for Qwen3-Embedding
        instructional_text = f"Instruct: Retrieve academic lecture material for: {text}"
        response = ollama.embed(
            model=self.embed_model, 
            input=instructional_text,
            options={'num_gpu': 15} # Partial offload to keep VRAM free
        )
        return response.embeddings[0]

    def rerank_score(self, query: str, doc: str) -> str:
        # GPU Priority: Reranking is math-heavy and needs speed
        prompt = (
            f"<Instruct>: Compare query and doc relevance. Respond with 'YES' if the document "
            f"precisely matches the specific person/topic in the query, otherwise 'NO'.\n"
            f"<Query>: {query}\n"
            f"<Document>: {doc}\n"
            f"Relevance Verdict:"
        )
        response = ollama.chat(
            model=self.rerank_model, 
            messages=[{'role': 'user', 'content': prompt}],
            options={'num_gpu': 40} # Force GPU
        )
        return response.message.content

    def check_intent(self, query: str) -> str:
        # CPU Only: The 1B guard is small and fast on CPU, freeing up GPU for the chat
        prompt = (
            f"Analyze the following user query for ambiguity regarding tutor names. "
            f"If multiple tutors could match (e.g., 'Syrym'), ask for clarification. "
            f"Otherwise, return 'CLEAR'.\n"
            f"Query: {query}"
        )
        response = ollama.chat(
            model=self.guard_model, 
            messages=[{'role': 'user', 'content': prompt}],
            options={'num_gpu': 0} # CPU Force
        )
        return response.message.content

    def chat(self, query: str, context: str) -> str:
        # GPU Priority: This is the user-facing part, needs to be 'blazing'
        system_prompt = (
            "You are the IITU Teacher AI Assistant. Use the provided context to answer questions. "
            "If the context doesn't match the specific name or topic, explicitly state that you don't have information on that specific entity. "
            "Do not hallucinate or mix up similar names."
        )
        full_prompt = f"Context:\n{context}\n\nQuestion: {query}"
        response = ollama.chat(
            model=self.chat_model, 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': full_prompt}
            ],
            options={'num_gpu': 40} # Force GPU
        )
        return response.message.content
