import ollama
from typing import List
import os
import re

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        # USER REQUESTED CPU OPTIMIZATION (2026-01-28)
        self.chat_model = "gemma3:4b"
        self.embed_model = "embeddinggemma:300m"
        self.timeout = 120.0 # Relaxed for CPU

    def get_embedding(self, text: str) -> List[float]:
        # BLAZING FAST: Using GPU for single embedding
        response = ollama.embed(
            model=self.embed_model,
            input=text,
            options={'num_gpu': -1}
        )
        return response.embeddings[0]

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        # ADVANCED COMPUTING: Batch processing on GPU
        response = ollama.embed(
            model=self.embed_model,
            input=texts,
            options={'num_gpu': -1}
        )
        return response.embeddings

    def chat(self, system_prompt: str, user_message: str) -> str:
        # BUDGET MODE: Keeping the LLM on CPU to save resources
        response = ollama.chat(
            model=self.chat_model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            options={
                'num_gpu': -1,       # Enable GPU for BLAZING FAST speed
                'num_ctx': 4096,     # Goldilocks zone: Fits all usage without memory overflow
                'num_predict': 2048, # Fixes "cut in middle" - allow HUGE answers
                'temperature': 0.7,  # Balanced creativity
                'num_thread': 8      # CPU fallback optimization
            }
        )
        content = response.message.content
        # SUPER RULE: Strip any Chinese/Japanese/Korean characters from the output
        clean_content = re.sub(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\uff00-\uffef]+', '', content)
        return clean_content.strip()
