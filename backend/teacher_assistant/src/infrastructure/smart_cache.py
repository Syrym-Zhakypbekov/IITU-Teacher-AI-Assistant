"""
ULTRA-SMART CACHE: SQLite-based persistent Q&A storage
Saves CPU by returning cached answers instantly for repeated/similar questions.
"""
import sqlite3
import os
import hashlib
import re
import math
import json
import numpy as np
from typing import Optional, Dict, List

class SmartCache:
    def __init__(self, db_path="./smart_cache.db"):
        self.db_path = db_path
        self._l1_cache = {} # L1 Memory Cache (Ram)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for persistent caching."""
        conn = sqlite3.connect(self.db_path)
        
        # WAL Mode for Concurrency (10+ users)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('PRAGMA synchronous=NORMAL;')
        
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS qa_cache (
                query_hash TEXT PRIMARY KEY,
                query_text TEXT,
                normalized_query TEXT,
                response TEXT,
                references_json TEXT,
                embedding_blob BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1
            )
        ''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_normalized ON qa_cache(normalized_query)')
        conn.commit()
        conn.close()

    def predict(self, vector: List[float], threshold: float = 0.82) -> Optional[Dict]:
        """
        PREDICTION ENGINE: Predicts answer based on similar past questions.
        Alias for get_semantic to emphasize predictive capability.
        """
        return self.get_semantic(vector, threshold)
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for fuzzy matching."""
        q = query.lower().strip()
        # Remove common question words
        q = re.sub(r'^(what is|what are|explain|describe|tell me about|как|что такое)\s*', '', q)
        # Remove punctuation
        q = re.sub(r'[^\w\s]', '', q)
        # Remove extra whitespace
        q = re.sub(r'\s+', ' ', q).strip()
        return q
    
    def _hash_query(self, normalized: str) -> str:
        """Create hash of normalized query."""
        return hashlib.md5(normalized.encode()).hexdigest()

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        # Convert to numpy for speed if lists are large, but for 768 dim standard python is ok-ish
        # using numpy is safer
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(np.dot(v1, v2) / (norm1 * norm2))
    
    def get(self, query: str) -> Optional[Dict]:
        """Try to get cached response by EXACT match. L1 Ram -> L2 Disk."""
        normalized = self._normalize_query(query)
        query_hash = self._hash_query(normalized)
        
        # 1. CHECK L1 RAM (Nanosecond speed)
        if query_hash in self._l1_cache:
            return self._l1_cache[query_hash]
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Exact match
        c.execute('SELECT response, references_json FROM qa_cache WHERE query_hash = ?', (query_hash,))
        row = c.fetchone()
        
        if row:
            # Update access count
            c.execute('UPDATE qa_cache SET access_count = access_count + 1 WHERE query_hash = ?', (query_hash,))
            conn.commit()
            conn.close()
            
            result = {
                'response': row[0],
                'references': json.loads(row[1]),
                'cached': True,
                'type': 'exact'
            }
            # Populate L1
            self._l1_cache[query_hash] = result
            return result
        
        conn.close()
        return None

    def get_semantic(self, query_embedding: List[float], threshold: float = 0.92) -> Optional[Dict]:
        """
        Try to find a semantically similar question in the cache.
        Returns the best match if similarity > threshold.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get all embeddings
        # Optimization: Fetch ONLY what we need for the calc
        c.execute('SELECT rowid, embedding_blob FROM qa_cache WHERE embedding_blob IS NOT NULL')
        rows = c.fetchall()
        
        if not rows:
            conn.close()
            return None

        # 1. Build Matrix (Vectorization)
        # This is where passing "list of lists" to numpy is 100x faster than python loops
        ids = []
        vectors = []
        for rid, blob in rows:
            ids.append(rid)
            vectors.append(json.loads(blob))
            
        if not vectors:
            conn.close()
            return None
            
        matrix = np.array(vectors) # Shape: (N, 768)
        query_vec = np.array(query_embedding) # Shape: (768,)
        
        # Normalize Matrix (if not already) & Query
        norm_matrix = np.linalg.norm(matrix, axis=1, keepdims=True)
        norm_query = np.linalg.norm(query_vec)
        
        # Avoid divide by zero
        matrix_normalized = matrix / (norm_matrix + 1e-10)
        query_normalized = query_vec / (norm_query + 1e-10)
        
        # 2. Matrix Dot Product (The "Single Handed" Magic)
        # Calculates similarity for ALL questions in one CPU instruction set
        scores = np.dot(matrix_normalized, query_normalized) # Shape: (N,)
        
        # 3. Find Best Match
        best_idx = np.argmax(scores)
        best_score = float(scores[best_idx])
        
        if best_score >= threshold:
            # Fetch full details only for the winner
            winner_id = ids[best_idx]
            c.execute('SELECT response, references_json FROM qa_cache WHERE rowid = ?', (winner_id,))
            res_row = c.fetchone()
            conn.close()
            
            if res_row:
                return {
                    'response': res_row[0],
                    'references': json.loads(res_row[1]),
                    'cached': True,
                    'type': 'semantic',
                    'score': best_score
                }
        
        conn.close()
        return None
            
        return None
    
    def set(self, query: str, response: str, references: list, embedding: Optional[List[float]] = None):
        """Store Q&A pair in cache."""
        normalized = self._normalize_query(query)
        query_hash = self._hash_query(normalized)
        
        # Update L1
        self._l1_cache[query_hash] = {
            'response': response,
            'references': references,
            'cached': True,
            'type': 'exact' # Newly set is effectively exact for itself
        }
        
        embed_json = json.dumps(embedding) if embedding else None
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO qa_cache (query_hash, query_text, normalized_query, response, references_json, embedding_blob)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (query_hash, query, normalized, response, json.dumps(references), embed_json))
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*), SUM(access_count) FROM qa_cache')
        row = c.fetchone()
        conn.close()
        return {
            'total_cached': row[0] or 0,
            'total_hits': row[1] or 0
        }

    def clear(self):
        """Clear all cache."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM qa_cache')
        conn.commit()
        conn.close()
