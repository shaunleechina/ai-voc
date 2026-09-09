import mysql.connector
db_config = {
    'host': '47.95.169.233',
    'port': 3306,
    'user': 'root',
    'password': 'lxy_2000',
    'database': 'aivoc',
    'autocommit': True
}
print("Connecting with autocommit=True...")
conn = mysql.connector.connect(**db_config)
print("Connected, autocommit:", conn.autocommit)
cursor = conn.cursor()

# First verify we can see the records
print("\nAll D202609% records:")
cursor.execute('SELECT data_code, HEX(data_code), text_content IS NULL, LENGTH(text_content) FROM txt_data WHERE data_code LIKE "D202609%"')
rows = cursor.fetchall()
for r in rows:
    print(f'  {r}')

# Now try the IN clause
print("\nTrying IN clause with autocommit:")
cursor.execute('SELECT data_code, text_content FROM txt_data WHERE data_code IN ("D202609005", "D202609006")')
rows = cursor.fetchall()
print(f'Rows returned: {len(rows)}')
for r in rows:
    text = r[1]
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    print(f'  {r[0]}: {len(text)} chars')
    print(f'    {text[:200]}...')

cursor.close()
conn.close()
print("Done")