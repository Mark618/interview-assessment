import sqlite3

DATABASE_PATH = "app/database/database.db"

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    #https://zetcode.com/python/sqlite3-cursor-row-factory/
    conn.row_factory = sqlite3.Row
    return conn