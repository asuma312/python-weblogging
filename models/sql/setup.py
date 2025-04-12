import os.path

from models.sql.user import User
from utils.path import get_user_path
from datetime import datetime
import sqlite3


def setup_database(user:User):
    db_path = get_user_path(user)
    db_name = 'log_1.sqlite'
    full_db_path = os.path.join(db_path, db_name)
    conn = sqlite3.connect(full_db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATETIME NOT NULL,
            type TEXT NOT NULL,
            function TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    cursor.close()
    conn.commit()
    return conn
