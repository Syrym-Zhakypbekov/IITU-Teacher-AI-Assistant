from ..infrastructure.ollama_client import OllamaClient
from ..infrastructure.database import VectorDatabase
from ..infrastructure.smart_cache import SmartCache
from ..core.models import ChatResponse
from ..core.cost_manager import SmartCostManager
import re

class RAGService:
    def __init__(self, db: VectorDatabase, llm: OllamaClient, cache: SmartCache):
        self.db = db
        self.llm = llm
        self.cache = cache  # Injected persistent cache
        self.cost_manager = SmartCostManager() # Brain for efficiency

    def answer_question(self, query: str, force_cache_only: bool = False, is_voice: bool = False) -> ChatResponse:
        # 0. ALLOCATE BUDGET (Dynamic Resource Management)
        # We need this early to determine if we skip RAG or optimize for voice
        output_budget = self.cost_manager.determine_output_budget(is_voice)

        # 1. OPTIMIZED SKIP: Simple greetings/tests (Cost = ~0)
        if self.cost_manager.should_skip_rag(query):
            simple_system = f"You are a helpful academic assistant. Answer briefly in the SAME language as the user. CONSTRANT: Max {output_budget['max_sentences']} sentences."
            simple_response = self.llm.chat(simple_system, query)
            return ChatResponse(
                response=simple_response,
                references=[],
                status="chat_simple"
            )

        # 2. Embed query (GPU - fast)
        vector = self.llm.get_embedding(query)

        # 3. CHECK SMART CACHE (Semantic & Exact)
        cached = self.cache.get(query) or self.cache.get_semantic(vector, threshold=0.82)
            
        if cached:
            msg_prefix = "\n\n_[Cached response]_" if cached.get('type') == 'exact' else f"\n\n_[Cached (Semantic)]_"
            return ChatResponse(
                response=cached['response'] + msg_prefix,
                references=cached['references'],
                status="cached"
            )
        
        # GUARD: Overheat Protection
        if force_cache_only:
             return ChatResponse(
                response="⚠️ System cooling active. Please try again in 10s.",
                references=[],
                status="throttled_cpu_hot"
            )
        
        # 4. SMART RETRIEVE
        results = self.db.smart_search(vector, query, limit=12)
        
        if results.empty:
            return ChatResponse(response="Context not found.", references=[], status="no_context")

        # 5. DYNAMIC BUDGET ALLOCATION
        budget = self.cost_manager.allocate_budget(results, is_voice=is_voice)
        MAX_CONTEXT = budget['max_context']
        
        context_blocks = []
        references = []
        total_chars = 0
        
        for _, row in results.iterrows():
            chunk_text = row['content']
            score = row.get('smart_score', 0)
            max_chunk_len = 800 if score >= 10 else 400
            chunk_text = chunk_text[:max_chunk_len]
            
            if total_chars + len(chunk_text) > MAX_CONTEXT:
                break
            
            ref = f"{row['source']} | {row['location']}"
            context_blocks.append(f"[{ref}]: {chunk_text}")
            references.append(ref)
            total_chars += len(chunk_text)

        context = "\n".join(context_blocks)
        
        # 6. VOICE-AWARE PROMPT
        system_prompt = (
            f"You are IITU Academic Assistant. Mode: {budget['output']['mode']}.\n"
            "ABSOLUTE RULES:\n"
            "1. Answer ONLY from context\n"
            "2. CITE [Source | Location]\n"
            f"3. LENGTH: MAX {budget['output']['max_sentences']} sentences.\n"
            f"4. COMPLEXITY: {budget['output']['complexity']}.\n"
            "5. NO Chinese/Japanese/Korean."
        )
        
        if is_voice:
             system_prompt += (
                 "\nAUDIO MODE ENABLED: "
                 "- Avoid all markdown (NO **bolding**, NO bullet points).\n"
                 "- Use conversational word-based transitions.\n"
                 "- Ensure punctuation is smooth for professional text-to-speech rhythm."
             )
        
        user_msg = f"{context}\n\nQ: {query}"
        answer = self.llm.chat(system_prompt, user_msg)
        
        # 7. SAVE TO CACHE
        unique_refs = list(dict.fromkeys(references))
        self.cache.set(query, answer, unique_refs, embedding=vector)
        
        return ChatResponse(
            response=answer,
            references=unique_refs,
            status=f"generated_{budget['mode']}"
        )
    
    def get_cache_stats(self):
        """Get cache statistics for monitoring."""
        return self.cache.get_stats()
