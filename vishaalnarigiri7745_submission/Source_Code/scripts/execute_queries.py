import sqlite3

db_path = "/Users/vaishnavnarigiri/Desktop/bluestock/db/bluestock_mf.db"
queries_path = "/Users/vaishnavnarigiri/Desktop/bluestock/sql/queries.sql"

# Load SQL file
with open(queries_path, 'r') as f:
    sql_text = f.read()

# Split by double newline or query comments
queries = sql_text.split("\n\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

for q in queries:
    q = q.strip()
    if not q:
        continue
    
    # Extract query description from comments
    lines = q.split('\n')
    comments = [line.replace('--', '').strip() for line in lines if line.startswith('--')]
    query_body = '\n'.join([line for line in lines if not line.startswith('--')]).strip()
    
    if not query_body:
        continue
        
    print("=" * 80)
    if comments:
        print(f"Description: {comments[0]}")
    print(f"Running SQL:\n{query_body}\n")
    
    try:
        cursor.execute(query_body)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
        # Format as table
        print(f"Results: {len(rows)} row(s) returned")
        # Print header
        header = " | ".join(columns)
        print(header)
        print("-" * len(header))
        for row in rows[:10]: # Print first 10 rows
            print(" | ".join(str(val) for val in row))
        if len(rows) > 10:
            print("...")
        print()
    except Exception as e:
        print(f"Error running query: {e}\n")

conn.close()
