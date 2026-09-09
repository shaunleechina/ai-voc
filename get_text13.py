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

# Query each code individually
for code in ["D202609005", "D202609006"]:
    print(f"\nQuerying for {code}...")
    cursor.execute("SELECT data_code, text_content FROM txt_data WHERE data_code = %s", (code,))
    rows = cursor.fetchall()
    print(f'Rows returned: {len(rows)}')
    for r in rows:
        text = r[1]
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        print(f'  {r[0]}: {len(text)} chars')
        print(f'    {text[:300]}...')

# Also try with a subquery
print("\nTrying with subquery...")
cursor.execute("""
    SELECT data_code, text_content 
    FROM txt_data 
    WHERE data_code IN (
        SELECT data_code FROM txt_data WHERE data_code LIKE 'D20260900%'
    )
""")
rows = cursor.fetchall()
print(f'Rows returned: {len(rows)}')
for r in rows:
    text = r[1]
    if isinstance(text, bytes):
        text = text.decode('utf-8')
    print(f'  {r[0]}: {len(text)} chars')

cursor.close()
conn.close()
print("Done")