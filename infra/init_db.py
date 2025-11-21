import sqlite3
from infra.config import settings

conn = sqlite3.connect(settings.DATABASE_URL)

try:
    with open("schema.sql", "r") as f:
        sql_script = f.read()

    conn.executescript(sql_script)

    print("Schema executed successfully!")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    conn.close()
