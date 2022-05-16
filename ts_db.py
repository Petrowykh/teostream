import sqlite3


class Teo_DB:

    def __init__(self, db_file) -> None:
        self.connection = sqlite3.connect(database=db_file)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()