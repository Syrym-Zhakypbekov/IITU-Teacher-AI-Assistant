import re
from typing import Tuple, Dict

class SmartCostManager:
    """
    Manages computational costs by dynamically routing queries and budgeting context.
    Goal: "Lowest cost, highest quality".
    """
    
    def __init__(self):
        # Queries that don't need RAG
        self.skip_patterns = [
            r"^(hi|hello|hey|greetings|hola|welcome|привет|здравствуйте).*", 
            r"^(who are you|what are you|кто ты|что ты).*",
            r"^test.*",
            r"^ping.*"
        ]
        
    def should_skip_rag(self, query: str) -> bool:
        """Check if RAG can be completely skipped (Cost = ~0)."""
        q = query.lower().strip()
        
        # 0. COST SAVER: Empty or meaningless symbol queries (e.g. "&", "?")
        # Blocks queries with no alphanumeric content or just 1 char
        if len(re.sub(r'[^a-z0-9а-я]', '', q)) < 2:
            return True

        for pattern in self.skip_patterns:
            if re.match(pattern, q):
                return True
        return False
        
    def determine_output_budget(self, is_voice: bool = False) -> Dict:
        """Determines the output length based on the medium (Voice vs Text)."""
        if is_voice:
            return {
                "max_sentences": 2,
                "complexity": "simple",
                "mode": "voice_optimized",
                "cost_weight": 0.4 # Voice is expensive in TTS compute, keep it short
            }
        return {
            "max_sentences": 5,
            "complexity": "detailed",
            "mode": "reading_optimized",
            "cost_weight": 1.0
        }

    def allocate_budget(self, results, is_voice: bool = False) -> Dict:
        """
        Adapts resource usage based on search confidence and input medium.
        Returns: { 'max_context': int, 'mode': str }
        """
        output_budget = self.determine_output_budget(is_voice)
        
        if results.empty:
            return {'max_context': 0, 'mode': 'no_results', 'output': output_budget}
            
        # Get score of the best chunk
        best_score = results.iloc[0].get('smart_score', 0)
        
        # Base budget logic
        if best_score >= 20: 
            config = {'max_context': 2000, 'mode': 'precision_sniper'}
        elif best_score >= 8:
            config = {'max_context': 4500, 'mode': 'standard_balanced'}
        else:
            config = {'max_context': 8000, 'mode': 'deep_dive'}
            
        return {**config, 'output': output_budget}
