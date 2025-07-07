import sqlite3

conn = sqlite3.connect("health_data.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM patients")
rows = cursor.fetchall()
for row in rows:
    print(f"{row[0]}: {row[1]}")
