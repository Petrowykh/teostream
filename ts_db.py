import sqlite3


class Teo_DB:

    def __init__(self, db_file) -> None:
        self.connection = sqlite3.connect(database=db_file)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def get_ten(self):
        # first 10 records
        with self.connection:
            return self.cursor.execute("SELECT * FROM trip LIMIT 10").fetchall()