import logging
import sqlite3

class Database:

    def __init__(self):
        self.connection = sqlite3.connect("data/players.db")
        self.cursor = self.connection.cursor()
        self.logger = logging.getLogger("Database")

    def insert(self, row : list) -> None:

        try:
            self.cursor.execute("INSERT INTO playersOnline VALUES (?, ?)", row)
            self.connection.commit()
            self.close()
        except Exception as e:
            self.logger.info("SQL insertion error at time {}: {}".format(row[0], e))

    def close(self) -> None:
        self.cursor.close()
        self.connection.close()