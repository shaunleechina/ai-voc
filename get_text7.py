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

# Get all D2026% codes with exact bytes
print("\nAll D2026% codes with HEX:")
cursor.execute('SELECT data_code, HEX(data_code), CHAR_LENGTH(data_code), OCTET_LENGTH(data_code) FROM txt_data WHERE data_code LIKE "D2026%"')
rows = cursor.fetchall()
for r in rows:
    print(f'  data_code={repr(r[0])} hex={r[1]} char_len={r[2]} octet_len={r[3]}')

cursor.close()
conn.close()
print("Done")