import mysql.connector
db_config = {
    'host': '47.95.169.233',
    'port': 3306,
    'user': 'root',
    'password': 'lxy_2000',
    'database': 'aivoc',
    'autocommit': True,
}
print("Connecting...")
conn = mysql.connector.connect(**db_config)
print("Connected")
cursor = conn.cursor()

# Get all D20260900% records and filter in Python
print("\nFetching all D20260900% records...")
cursor.execute("SELECT data_code, text_content FROM txt_data WHERE data_code LIKE 'D20260900%'")
rows = cursor.fetchall()
print(f'Rows returned: {len(rows)}')

for r in rows:
    text = r[1]
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    if r[0] in ['D202609005', 'D202609006']:
        print(f'=== {r[0]} ===')
        print(f'Length: {len(text)} chars')
        print(text)
        print()

cursor.close()
conn.close()
print("Done")