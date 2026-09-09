import mysql.connector
db_config = {
    'host': '47.95.169.233',
    'port': 3306,
    'user': 'root',
    'password': 'lxy_2000',
    'database': 'aivoc',
    'autocommit': True,
}
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()
codes = [f'D202609{str(i).zfill(3)}' for i in range(7,13)]
print(codes)
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
    print(text[:500])
    print('...')
    print()
cursor.close()
conn.close()