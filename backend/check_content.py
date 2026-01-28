import lancedb
import os
import pandas as pd

try:
    db_path = os.path.abspath("super_precise_db")
    db = lancedb.connect(db_path)
    tbl = db.open_table("knowledge_base")
    df = tbl.to_pandas()
    
    user_story_rows = df[df['source'].str.contains('User Story', case=False)]
    print(f"User Story rows: {len(user_story_rows)}")
    for i, row in user_story_rows.head(3).iterrows():
        print(f"[{row['source']}]: {row['content'][:500]}")
        print("---")

    defect_rows = df[df['source'].str.contains('Отчеты о дефектах', case=False)]
    print(f"Defect Report rows: {len(defect_rows)}")
    for i, row in defect_rows.head(2).iterrows():
        print(f"[{row['source']}]: {row['content'][:500]}")
        print("---")

except Exception as e:
    print(e)
