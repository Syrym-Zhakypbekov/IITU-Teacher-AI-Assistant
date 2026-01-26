import lancedb
import pandas as pd
import os
from typing import List

class VectorStore:
    def __init__(self, path="./teacher_assistant/data/lancedb_index"):
        self.path = path
        self.db = lancedb.connect(self.path)
        self.table_name = "tutors_v3"

    def index_data(self, data: List[dict]):
        df = pd.DataFrame(data)
        # Ensure 'vector' column exists if you are providing pre-computed embeddings
        # but LanceDB can also handle embeddings via its API. 
        # For simplicity in this clean arch, we'll assume the df has a 'vector' column.
        
        # Create table with FTS (Full Text Search) index
        tbl = self.db.create_table(self.table_name, data=df, mode="overwrite")
        tbl.create_fts_index("content", replace=True) # Essential for name precision
        print(f"Indexed {len(data)} items into {self.table_name}")

    def search(self, query_vec: List[float], query_text: str, limit=5):
        if self.table_name not in self.db.table_names():
            return pd.DataFrame()
            
        tbl = self.db.open_table(self.table_name)
        
        # Hybrid Search: Vector (Semantic) + Metadata Filtering via SQL-like 'where'
        # We also boost exact keyword matches by using FTS in the search
        results = (
            tbl.search(query_vec)
            .where(f"content LIKE '%{query_text}%'", prefilter=False)
            .limit(limit)
            .to_pandas()
        )
        return results
