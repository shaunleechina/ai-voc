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

codes = ['D202609007', 'D202609008', 'D202609009', 'D202609010', 'D202609011', 'D202609012']
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
    print(text)
    print()
cursor.close()
conn.close()