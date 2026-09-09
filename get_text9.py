import mysql.connector
db_config = {
    'host': '47.95.169.233',
    'port': 3306,
    'user': 'root',
    'password': 'lxy_2000',
    'database': 'aivoc',
}
print("Connecting...")
conn = mysql.connector.connect(**db_config)
print("Connected")
cursor = conn.cursor()

# Get the text content for the two records
print("\nFetching text content...")
cursor.execute('SELECT data_code, text_content FROM txt_data WHERE data_code IN ("D202609005", "D202609006")')
rows = cursor.fetchall()
print(f'Rows returned: {len(rows)}')
for r in rows:
    text = r[1]
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    print(f'=== {r[0]} ===')
    print(text[:500])
    print(f'... (total {len(text)} chars)')
    print()

# Also try a different approach - use the exact hex values
print("\nTrying with exact matching...")
for code in ["D202609005", "D202609006"]:
    cursor.execute('SELECT text_content FROM txt_data WHERE HEX(data_code) = HEX(%s)', (code,))
    rows = cursor.fetchall()
    print(f'{code}: {len(rows)} rows')
    if rows:
        text = rows[0][0]
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        print(f'  {text[:500]}')

cursor.close()
conn.close()
print("Done")