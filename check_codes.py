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

# Check what codes exist in D202609 range
cursor.execute("SELECT data_code, LENGTH(text_content) FROM txt_data WHERE data_code LIKE 'D202609%' ORDER BY data_code")
rows = cursor.fetchall()
print(f'Total D202609% records: {len(rows)}')
for r in rows:
    print(f'  {r[0]}: {r[1]} chars')

cursor.close()
conn.close()