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
print("Executing query...")
cursor.execute('SELECT data_code, text_content FROM txt_data WHERE data_code IN ("D202609005", "D202609006")')
rows = cursor.fetchall()
print(f'Rows returned: {len(rows)}')
for r in rows:
    print(f'{r[0]}: {repr(r[1][:100]) if r[1] else "NULL"}')
cursor.close()
conn.close()
print("Done")