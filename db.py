from contextlib import contextmanager
import sqlite3
from config import settings


@contextmanager
def transaction():
    conn = sqlite3.connect(settings.DATABASE_URL)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
