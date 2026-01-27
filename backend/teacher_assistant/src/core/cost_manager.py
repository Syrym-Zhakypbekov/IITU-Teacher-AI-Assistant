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
            r"^(hi|hello|hey|greetings|hola)\s*[\.!]*$",
            r"^(who are you\??|what are you\??)$",
            r"^test$",
            r"^ping$"
        ]
        
    def should_skip_rag(self, query: str) -> bool:
        """Check if RAG can be completely skipped (Cost = ~0)."""
        q = query.lower().strip()
        for pattern in self.skip_patterns:
            if re.match(pattern, q):
                return True
        return False
        
    def allocate_budget(self, results) -> Dict:
        """
        Adapts resource usage based on search confidence.
        Returns: { 'max_context': int, 'mode': str }
        """
        if results.empty:
            return {'max_context': 0, 'mode': 'no_results'}
            
        # Get score of the best chunk
        best_score = results.iloc[0].get('smart_score', 0)
        
        # Scenario 1: PRECISE MATCH (e.g., Filename match or exact distinct phrase)
        # We found exactly what we need. Don't waste tokens on noise.
        if best_score >= 20: 
            return {
                'max_context': 2000, # Small context window (fast cpu)
                'mode': 'precision_sniper',
                'description': 'High confidence match - using focused context'
            }
            
        # Scenario 2: GOOD MATCH (Standard keyword hit)
        elif best_score >= 8:
            return {
                'max_context': 4500, # Medium context
                'mode': 'standard_balanced',
                'description': 'Good matches found - using balanced context'
            }
            
        # Scenario 3: WEAK/SCATTERED (Need to read more to find valid info)
        else:
            return {
                'max_context': 8000, # Max context
                'mode': 'deep_dive',
                'description': 'Low confidence - engaging Deep Reading mode'
            }
