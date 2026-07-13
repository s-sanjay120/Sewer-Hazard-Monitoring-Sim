import sqlite3

conn = sqlite3.connect("sewer_data.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    methane REAL,
    air_quality REAL,
    temperature REAL,
    humidity REAL,
    risk TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")