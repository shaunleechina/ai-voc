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

# Test with literal string in query
print("\nQuerying with literal D202609005...")
cursor.execute('SELECT data_code, HEX(data_code), text_content IS NULL as is_null, LENGTH(text_content) as len FROM txt_data WHERE data_code = "D202609005"')
rows = cursor.fetchall()
print(f'Rows returned: {len(rows)}')
for r in rows:
    print(f'  {r}')

print("\nQuerying with literal D202609006...")
cursor.execute('SELECT data_code, HEX(data_code), text_content IS NULL as is_null, LENGTH(text_content) as len FROM txt_data WHERE data_code = "D202609006"')
rows = cursor.fetchall()
print(f'Rows returned: {len(rows)}')
for r in rows:
    print(f'  {r}')

print("\nQuerying with parameterized D202609005...")
cursor.execute('SELECT data_code, HEX(data_code), text_content IS NULL as is_null, LENGTH(text_content) as len FROM txt_data WHERE data_code = %s', ("D202609005",))
rows = cursor.fetchall()
print(f'Rows returned: {len(rows)}')
for r in rows:
    print(f'  {r}')

cursor.close()
conn.close()
print("Done")