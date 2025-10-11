import sqlite3
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "filemeta.db"
MIGRATION = ROOT / "migrations" / "001_create_files_table.sql"

def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        sql = MIGRATION.read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.commit()
        print(f"Applied migration to {DB_PATH}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
