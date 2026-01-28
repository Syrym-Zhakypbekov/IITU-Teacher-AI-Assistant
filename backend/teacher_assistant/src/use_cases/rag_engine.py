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

    def answer_question(self, query: str, history: list = [], force_cache_only: bool = False, is_voice: bool = False) -> ChatResponse:
        # 0. ALLOCATE BUDGET
        # ... (rest of logic) ...
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
        
        # 4.1 NOISE FILTER (Anti-Hallucination)
        # If the best result is too distinct (distance > threshold) or score is low, ignore it.
        # This prevents "Translate it" from grabbing random slides.
        if not results.empty:
             # Assuming smart_search returns 'distance' (lower is better) or we rely on 'smart_score' (higher is better)
             # Let's use a strict check. If the best 'smart_score' is < 15 (arbitrary, based on exploration), drop it.
             best_score = results.iloc[0].get('smart_score', 0)
             if best_score < 40: # STRICTER THRESHOLD
                 results = pd.DataFrame() # Drop all
        
        if results.empty:
            # Fallback to pure chat if no relevant docs found
            # But we still want to pass history for context!
            pass 

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
        
        # 6. ADVANCED SYSTEM PROMPT (User requested "Super Smart Flexible Brain")
        # We define a "Hybrid Mode" where it prioritizes context but falls back to general knowledge gracefully.
        
        system_prompt = (
            "You are an expert Academic Mentor at IITU. Your goal is to help students learn efficiently.\n\n"
            
            "### INSTRUCTIONS:\n"
            "1. **Synthesize & Explain**: You are a teacher, not a search engine.\n"
            "   - **DO NOT** just say 'The answer is in Slide X'.\n"
            "   - **Explain the concept fully** in your own words based on the context.\n"
            "   - Use the materials to form a comprehensive answer.\n"
            
            "2. **Citations**: Support your explanation with evidence.\n"
            "   - After explaining a point, add the citation `[Source | Slide X]`.\n"
            "   - Example: 'Requirements engineering is the process of defining, documenting, and maintaining software requirements. It ensures the final product meets stakeholder needs [Lecture 1, Slide 5].'\n"
            
            "3. **General Knowledge & Chat**:\n"
            "   - IF the question is general (e.g., 'What is 2+2?') AND context is missing -> Answer generally WITHOUT citations.\n"
            "   - IF the user asks to **translate** the previous message -> Translate the conversation history, ignore the document context.\n"
            "   - **CRITICAL**: Never fake a citation.\n"
            
            "4. **Tone & Style**:\n"
            "   - Be helpful, encouraging, and professional.\n"
            "   - Use Markdown lists and bold text for readability.\n"
            
            f"5. **CONSTRAINTS**:\n"
            f"   - Max Complexity: {budget['output']['complexity']}.\n"
            "   - Language: Same as User.\n"
        )
        
        if is_voice:
             system_prompt += (
                 "\n### VOICE MODE OVERRIDE:\n"
                 "- Do NOT use markdown formatting (no bold, no lists).\n"
                 "- Write in a conversational script format suitable for TTS reading.\n"
                 "- Keep sentences short and rhythmic."
             )
        
        
        # 6.5 INJECT CONVERSATION MEMORY (Smart Sliding Window)
        # We only take the last 4 messages to keep it CPU/Memory efficient.
        memory_block = ""
        if history:
            recent_history = history[-4:] 
            memory_block = "PREVIOUS CONVERSATION (Use for context, but prioritize [CONTEXT] above):\n"
            for msg in recent_history:
                role = "User" if msg['role'] == 'user' else "AI"
                memory_block += f"{role}: {msg['content']}\n"
            memory_block += "\n"

        user_msg = f"{memory_block}{context}\n\nQ: {query}"
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
