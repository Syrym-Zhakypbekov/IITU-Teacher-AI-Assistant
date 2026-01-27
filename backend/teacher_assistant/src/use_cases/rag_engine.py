from ..infrastructure.ollama_client import OllamaClient
from ..infrastructure.database import VectorDatabase
from ..infrastructure.smart_cache import SmartCache
from ..core.models import ChatResponse
from ..core.cost_manager import SmartCostManager
import re

class RAGService:
    def __init__(self, db: VectorDatabase, llm: OllamaClient):
        self.db = db
        self.llm = llm
        self.cache = SmartCache()  # SQLite persistent cache
        self.cost_manager = SmartCostManager() # Brain for efficiency

    def answer_question(self, query: str, force_cache_only: bool = False) -> ChatResponse:
        # 0. COST CHECK: Skip RAG for simple greetings
        if self.cost_manager.should_skip_rag(query):
            simple_response = self.llm.chat("You are a helpful assistant.", query)
            return ChatResponse(
                response=simple_response,
                references=[],
                status="chat_simple"
            )

        # 1. Embed query (GPU - fast) - DO THIS FIRST for semantic cache
        vector = self.llm.get_embedding(query)

        # 2. CHECK SQLITE CACHE (Semantic & Exact)
        # Try exact first (fastest)
        cached = self.cache.get(query)
        if not cached:
            # Try semantic (smarter)
            cached = self.cache.get_semantic(vector, threshold=0.82) # Tuned threshold
            
        if cached:
            msg_prefix = "\n\n_[Cached response]_" if cached.get('type') == 'exact' else f"\n\n_[Cached (Semantic {cached.get('score', 0):.2f})]_"
            return ChatResponse(
                response=cached['response'] + msg_prefix,
                references=cached['references'],
                status="cached"
            )
        
        # GUARD: If Overheating, REFUSE to generate new answer
        if force_cache_only:
             return ChatResponse(
                response="⚠️ System Overload Protection Active. I am cooling down. Please ask a simpler question or try again in 10 seconds.",
                references=[],
                status="throttled_cpu_hot"
            )
        
        # 3. SMART RETRIEVE with multi-signal scoring
        results = self.db.smart_search(vector, query, limit=12)
        
        if results.empty:
            return ChatResponse(
                response="I couldn't find relevant information in the materials.",
                references=[],
                status="no_context"
            )

        # 4. SMART CONTEXT: Dynamic budget allocation
        budget = self.cost_manager.allocate_budget(results)
        MAX_CONTEXT = budget['max_context']
        
        context_blocks = []
        references = []
        total_chars = 0
        
        for _, row in results.iterrows():
            chunk_text = row['content']
            score = row.get('smart_score', 0)
            # Give more space to high-scoring chunks
            max_chunk_len = 800 if score >= 10 else 400
            chunk_text = chunk_text[:max_chunk_len]
            
            if total_chars + len(chunk_text) > MAX_CONTEXT:
                break
            
            ref = f"{row['source']} | {row['location']}"
            context_blocks.append(f"[{ref}]: {chunk_text}")
            references.append(ref)
            total_chars += len(chunk_text)

        context = "\n".join(context_blocks)
        
        # 5. ULTRA-STRICT PROMPT
        system_prompt = (
            "You are IITU Academic Assistant.\n"
            "ABSOLUTE RULES:\n"
            "1. Answer ONLY from context\n"
            "2. CITE [Source | Location] for every fact\n"
            "3. If NOT in context: 'Not found in materials'\n"
            "4. Be concise (2-4 sentences)\n"
            "5. NO Chinese/Japanese/Korean"
        )
        
        user_msg = f"{context}\n\nQ: {query}"
        answer = self.llm.chat(system_prompt, user_msg)
        
        # 6. SAVE TO SQLITE CACHE with Embedding
        unique_refs = list(dict.fromkeys(references))
        self.cache.set(query, answer, unique_refs, embedding=vector)
        
        return ChatResponse(
            response=answer,
            references=unique_refs,
            status=f"generated_{budget['mode']}" # Log efficient mode
        )
    
    def get_cache_stats(self):
        """Get cache statistics for monitoring."""
        return self.cache.get_stats()
