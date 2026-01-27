import lancedb
import pandas as pd
import os
import re
from typing import List, Dict, Any
from functools import lru_cache

class VectorDatabase:
    def __init__(self, db_path="./super_precise_db"):
        self.db_path = db_path
        self.table_name = "knowledge_base"
        os.makedirs(db_path, exist_ok=True)
        self.db = lancedb.connect(db_path)
        self._filename_cache = {}  # Cache for filename lookups

    def insert_chunks(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return
        tbl = self.db.create_table(self.table_name, data=chunks, mode="overwrite")
        tbl.create_fts_index("content", replace=True)
        # Build filename cache
        self._filename_cache = {}
        for c in chunks:
            fname = c['source'].lower()
            if fname not in self._filename_cache:
                self._filename_cache[fname] = []

    def search(self, vector: List[float], limit: int = 10) -> pd.DataFrame:
        if self.table_name not in self.db.table_names():
            return pd.DataFrame()
        tbl = self.db.open_table(self.table_name)
        return tbl.search(vector).limit(limit).to_pandas()

    def smart_search(self, vector: List[float], query: str, limit: int = 12) -> pd.DataFrame:
        """ULTRA-SMART: Vector search + keyword boost + filename priority."""
        if self.table_name not in self.db.table_names():
            return pd.DataFrame()
        
        tbl = self.db.open_table(self.table_name)
        
        # 1. Get more candidates for re-ranking
        results = tbl.search(vector).limit(limit * 5).to_pandas()
        
        if results.empty:
            return results
        
        # 2. SMART SCORING: Combine multiple signals
        query_lower = query.lower()
        query_words = [w for w in re.split(r'\W+', query_lower) if len(w) > 2]
        
        def smart_score(row):
            content = row['content'].lower()
            source = row['source'].lower()
            score = 0
            
            # Keyword match bonus (highest priority)
            for word in query_words:
                if word in content:
                    score += 3
                if word in source:  # Filename match = HUGE boost
                    score += 25
            
            # Exact phrase match
            if query_lower[:20] in content:
                score += 5
            
            return score
        
        results['smart_score'] = results.apply(smart_score, axis=1)
        
        # 3. Sort by smart score, then by vector distance
        results = results.sort_values(
            by=['smart_score', '_distance'],
            ascending=[False, True]
        )
        
        return results.head(limit)

    def count(self) -> int:
        if self.table_name not in self.db.table_names():
            return 0
        return len(self.db.open_table(self.table_name))

    def delete_by_source(self, filename: str):
        """Neural Wipe: Delete all chunks associated with a specific file."""
        if self.table_name not in self.db.table_names():
            return
        tbl = self.db.open_table(self.table_name)
        # Use single quotes for the filename in the SQL-like filter
        tbl.delete(f"source = '{filename}'")
