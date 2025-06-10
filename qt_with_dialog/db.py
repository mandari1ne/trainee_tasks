import sqlite3 as sql

class DB:
    def __init__(self, db: str):
        self.db = db
        self.connection = sql.connect(self.db)

    def get_name_of_tables(self):
        with self.connection:
            cur = self.connection.execute('''
                SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ''')

            self.tables = [row[0] for row in cur.fetchall()]

            return self.tables