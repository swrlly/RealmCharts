import logging
import sqlite3

class Database:

    def __init__(self):
        self.connection = sqlite3.connect("data/players.db")
        self.executionPointer = self.connection.cursor()
        self.logger = logging.getLogger("Database")

    def Write(self, row : list) -> None:
        try:
            self.executionPointer.execute("INSERT INTO playersOnline VALUES (?, ?)", row)
            self.connection.commit()
            self.connection.close()
            self.logger.info("Inserted {} players.".format(row[1]))
        except Exception as e:
            self.logger.info("Failed to insert players: {}".format(e))