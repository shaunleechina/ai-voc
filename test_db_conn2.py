import mysql.connector
import time

db_config = {
    'host': '47.95.169.233',
    'port': 3306,
    'user': 'root',
    'password': 'lxy_2000',
    'database': 'aivoc',
    'autocommit': True,
    'connection_timeout': 30,
}

print("Connecting to database...")
max_retries = 3
conn = None
for attempt in range(max_retries):
    try:
        conn = mysql.connector.connect(**db_config)
        print(f"Connected successfully (attempt {attempt+1})")
        break
    except mysql.connector.Error as e:
        print(f"Connection attempt {attempt+1} failed: {e}")
        if attempt < max_retries - 1:
            time.sleep(5)
        else:
            raise

# Use buffered cursor to avoid "unread result" issues
cursor = conn.cursor(buffered=True)

# Test connection
cursor.execute("SELECT 1")
cursor.fetchall()
print("Connection test OK")

# Now fetch the 6 texts
codes = ['D2026090007', 'D2026090008', 'D2026090009', 'D2026090010', 'D2026090011', 'D2026090012']
placeholders = ','.join(['%s']*len(codes))
query = f"SELECT data_code, text_content FROM txt_data WHERE data_code IN ({placeholders})"
cursor.execute(query, tuple(codes))
rows = cursor.fetchall()
print(f'Rows returned: {len(rows)}')
for r in rows:
    text = r[1]
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    print(f'=== {r[0]} === ({len(text)} chars)')
    print(text[:200])
    print('...')
    print()

cursor.close()
conn.close()
print("Done")