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

# First verify we can see the records
print("\nAll D202609% records:")
cursor.execute('SELECT data_code, HEX(data_code), text_content IS NULL, LENGTH(text_content) FROM txt_data WHERE data_code LIKE "D202609%"')
rows = cursor.fetchall()
for r in rows:
    print(f'  {r}')

# Now try the IN clause with the exact same query structure
print("\nTrying IN clause:")
cursor.execute('SELECT data_code, text_content FROM txt_data WHERE data_code IN ("D202609005", "D202609006")')
rows = cursor.fetchall()
print(f'Rows returned: {len(rows)}')
for r in rows:
    print(f'  {r[0]}: {r[1] is not None}')

# Check if autocommit is needed
print("\nConnection autocommit:", conn.autocommit)
print("Connection in_transaction:", conn.in_transaction)

cursor.close()
conn.close()
print("Done")