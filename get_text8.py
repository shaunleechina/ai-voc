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

# Check collation and character set
cursor.execute('SHOW TABLE STATUS LIKE "txt_data"')
print(f"Table status: {cursor.fetchall()}")

cursor.execute('SHOW FULL COLUMNS FROM txt_data WHERE Field = "data_code"')
print(f"Column info: {cursor.fetchall()}")

# Try case-sensitive comparison
print("\nTrying binary comparison:")
cursor.execute('SELECT data_code, HEX(data_code) FROM txt_data WHERE BINARY data_code = "D202609005"')
rows = cursor.fetchall()
print(f'Rows with BINARY: {len(rows)}')
for r in rows:
    print(f'  {r}')

# Try with TRIM
print("\nTrying TRIM:")
cursor.execute('SELECT data_code, HEX(data_code) FROM txt_data WHERE TRIM(data_code) = "D202609005"')
rows = cursor.fetchall()
print(f'Rows with TRIM: {len(rows)}')
for r in rows:
    print(f'  {r}')

# Check if there are hidden characters
print("\nChecking exact bytes:")
cursor.execute('SELECT data_code, HEX(data_code), HEX("D202609005") FROM txt_data WHERE data_code LIKE "D20260900%"')
rows = cursor.fetchall()
for r in rows:
    match = "MATCH" if r[1] == r[2] else "NO MATCH"
    print(f'  db={r[1]} expected={r[2]} {match}')

cursor.close()
conn.close()
print("Done")