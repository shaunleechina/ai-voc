import mysql.connector
db_config = {
    'host': '47.95.169.233',
    'port': 3306,
    'user': 'root',
    'password': 'lxy_2000',
    'database': 'aivoc',
    'autocommit': True,
    'connection_timeout': 10
}
print("Connecting...")
conn = mysql.connector.connect(**db_config)
print("Connected")

# Create a new cursor
cursor = conn.cursor(buffered=True)
print("Cursor created")

# Execute
print("\nExecuting: SELECT data_code, text_content FROM txt_data WHERE data_code IN ('D202609005', 'D202609006')")
cursor.execute("SELECT data_code, text_content FROM txt_data WHERE data_code IN ('D202609005', 'D202609006')")

rows = cursor.fetchall()
print(f'Rows returned: {len(rows)}')
for r in rows:
    text = r[1]
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    print(f'  {r[0]}: {len(text)} chars')

cursor.close()
conn.close()
print("Done")