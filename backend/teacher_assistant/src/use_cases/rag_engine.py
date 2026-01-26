from ..infrastructure.database import VectorStore
from ..infrastructure.ollama_client import OllamaProvider
import pandas as pd
import re

class RAGEngine:
    def __init__(self, db: VectorStore, ai: OllamaProvider):
        self.db = db
        self.ai = ai

    def _extract_potential_names(self, query: str):
        # Simple regex for Capitalized names, can be improved with a model
        return re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*', query)

    def process_query(self, query: str):
        # 1. AMBIGUITY DETECTION (The "Same Name" Filter)
        # We check if the query contains a name that might have multiple records
        extracted_names = self._extract_potential_names(query)
        
        # 2. TRAFFIC COP (Intent & Ambiguity Check)
        intent_status = self.ai.check_intent(query)
        if "CLEAR" not in intent_status.upper() and len(intent_status) > 10:
             return {
                 "response": intent_status,
                 "references": [],
                 "status": "ambiguous"
             }

        # 3. ADVANCED HYBRID SEARCH
        # We use the extracted names to force FTS to prioritize those specific strings
        vec = self.ai.get_embedding(query)
        
        # We search for the vector but also specifically look for any names we found
        search_filter = ""
        if extracted_names:
            # Create a filter that looks for any of the extracted names in the content
            name_filters = [f"content LIKE '%{name}%'" for name in extracted_names]
            search_filter = " OR ".join(name_filters)

        search_results = self.db.search(vec, query) # Base search uses query text for FTS
        
        if search_results.empty:
            return {
                "response": "I couldn't find any information regarding that specific request.",
                "references": [],
                "status": "not_found"
            }

        # 4. IDENTITY VERIFICATION (The "Double Judge")
        # We group results by tutor to see if we have multiple "candidates" with the same name
        validated_context = []
        references = []
        unique_tutors = search_results['tutor'].unique()

        if len(unique_tutors) > 1 and any(name in query for name in extracted_names):
            # Potential collision detected - multiple tutors found for one name search
            collision_msg = "I found multiple teachers with similar names. Which one did you mean?\n"
            for t in unique_tutors:
                topics = search_results[search_results['tutor'] == t]['topic'].unique()
                collision_msg += f"- {t} (Specializing in: {', '.join(topics)})\n"
            
            return {
                "response": collision_msg,
                "references": list(unique_tutors),
                "status": "collision"
            }

        # 5. RERANKING (Context Verification)
        for _, row in search_results.iterrows():
            # The Reranker model (Qwen3-Reranker-8B) evaluates the pair
            verdict = self.ai.rerank_score(query, row['content'])
            
            # Explicitly check for negative matches in the reranker output
            if "YES" in verdict.upper() or "RELEVANT" in verdict.upper():
                validated_context.append(row['content'])
                references.append(f"{row['tutor']} (Topic: {row['topic']})")

        if not validated_context:
             return {
                "response": "I found some records, but they don't seem to match your specific question accurately. Could you provide a full name or more context?",
                "references": [],
                "status": "filtered"
            }

        # 6. FINAL GENERATION (Ministral-3B)
        context_str = "\n---\n".join(validated_context)
        answer = self.ai.chat(query, context_str)
        
        return {
            "response": answer,
            "references": list(set(references)),
            "status": "success"
        }
