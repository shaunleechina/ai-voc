import mysql.connector
db_config = {
    'host': '47.95.169.233',
    'port': 3306,
    'user': 'root',
    'password': 'lxy_2000',
    'database': 'aivoc',
}
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()
cursor.execute('SELECT data_code, text_content FROM txt_data WHERE data_code IN ("D202609005", "D202609006")')
rows = cursor.fetchall()
for r in rows:
    print('=== {} ==='.format(r[0]))
    print(repr(r[1][:200]) if r[1] else 'NULL')
    print()
cursor.close()
conn.close()