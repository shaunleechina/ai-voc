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

# The actual codes in the database have 3 zeros: D2026090005, D2026090006
# User mentioned: D202609005, D202609006 (2 zeros)
# Let's fetch the actual codes
print("\nFetching actual codes D2026090005 and D2026090006...")
for code in ['D2026090005', 'D2026090006']:
    cursor.execute("SELECT data_code, text_content FROM txt_data WHERE data_code = %s", (code,))
    rows = cursor.fetchall()
    print(f'Rows returned for {code}: {len(rows)}')
    for r in rows:
        text = r[1]
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        print(f'=== {r[0]} ===')
        print(f'Length: {len(text)} chars')
        print(text)
        print()

cursor.close()
conn.close()
print("Done")