import lancedb
import os
import pandas as pd

try:
    db_path = os.path.abspath("super_precise_db")
    if not os.path.exists(db_path):
        print(f"Path not found: {db_path}")
        exit(1)

    print(f"Connecting to: {db_path}")
    db = lancedb.connect(db_path)
    
    # Use list_tables() as table_names() is deprecated
    tables = db.table_names() 
    print(f"Tables: {tables}")
    
    if "knowledge_base" not in tables:
        print("Table 'knowledge_base' not found.")
        exit(1)

    tbl = db.open_table("knowledge_base")
    
    # Just convert to pandas and take head
    full_df = tbl.to_pandas()
    df = full_df.head(20)

    print(f"Total rows in DB: {len(full_df)}")
    print("\nUnique sources (top 20 rows):")
    print(df['source'].unique())

    print("\nContent sample:")
    for i, row in df.head(5).iterrows():
        print(f"Source: {row['source']}")
        print(f"Content snippet: {row['content'][:300]}...")
        print("-" * 20)

except Exception as e:
    import traceback
    traceback.print_exc()
    exit(1)
