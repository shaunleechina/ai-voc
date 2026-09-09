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

target_codes = ['D202609005', 'D202609006']
for r in rows:
    text = r[1]
    code = r[0]
    print(f'Record: data_code={repr(code)}, len={len(text) if text else 0}')
    print(f'  code in target_codes: {code in target_codes}')
    print(f'  code == "D202609005": {code == "D202609005"}')
    print(f'  code == "D202609006": {code == "D202609006"}')
    if text is not None:
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        if code in target_codes:
            print(f'=== {code} ===')
            print(f'Length: {len(text)} chars')
            print(text)
            print()

cursor.close()
conn.close()
print("Done")