import sqlite3
from infra.config import settings


def init_db():
    conn = sqlite3.connect(settings.DATABASE_URL)

    try:
        with open(settings.BASE_PATH + "/infra/schema.sql", "r") as f:
            sql_script = f.read()

        conn.executescript(sql_script)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        conn.close()
