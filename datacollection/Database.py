import logging
import sqlite3

class Database:

    def __init__(self, link):
        self._connection = None
        self._cursor = None
        self.link = link
        self.logger = logging.getLogger("Database")

    def connect(self):
        # Connect to database and initialize cursor.
        self._connection = sqlite3.connect(self.link)
        self._cursor = self._connection.cursor()

    def close(self) -> None:
        # Close database connection and cursor connection.
        self._cursor.close()
        self._connection.close()

    def insert_new_row(self, row : list) -> None:
        # Insert new playercount.
        self.connect()
        
        try:
            self._cursor.execute("INSERT INTO playersOnline VALUES (?, ?);", row)
            self._connection.commit()
        except Exception as e:
            self.logger.info("Insertion error at time {}: {}".format(row[0], e))
            
        self.close()

    def get_nonnull_rows(self, start, end = None):
        # Return rows with start <= timestamp < end with non null playercount
        # If only start, return 1 row.
        self.connect()
        rows = []
        
        if end == None:
            self._cursor.execute("SELECT * FROM playersOnline WHERE timestamp = {} AND players NOT NULL;".format(start))
            rows = self._cursor.fetchone()
        else:
            self._cursor.execute("SELECT * FROM playersOnline WHERE timestamp >= {} AND timestamp < {} AND players NOT NULL;".format(start, end))
            rows = self._cursor.fetchall()

        self.close()
        return rows

    def fill_null(self, start, end):
        # Replace rows with start <= timestamp < end with NULL.
        rows =  self.get_nonnull_rows(start, end)
        rows = [{"players": None, "timestamp": i[0]} for i in rows]

        self.connect()

        try:
            self._cursor.executemany("UPDATE playersOnline SET players = :players WHERE timestamp = :timestamp;", rows)
            self._connection.commit()
        except Exception as e:
            self.logger.info("Update operation failed")

        self.close()
        
    def fill_missing_times(self) -> None:
        # Fill in missing time intervals over 2 minutes with NA.
        self.connect()
        # get starting time of gap and total missing seconds
        self._cursor.execute("""
        SELECT timestamp,
            row_num,
            next_time - timestamp AS difference
            FROM 
                (SELECT *, 
                    ROW_NUMBER() OVER () as row_num,
                    LEAD(timestamp, 1) OVER (ORDER BY timestamp ASC) as next_time
                    FROM playersOnline)
            WHERE difference > 120;""")
        missing = self._cursor.fetchall()
        
        for row in missing:
            start = row[0]
            width = row[2]
            new_rows = []
            for add in range(60, width, 60):
                new_rows.append((start + add, None))
            try:
                self._cursor.executemany("INSERT INTO playersOnline VALUES (?,?);", new_rows)
                self._connection.commit()
                self.logger.info("Inserted {} rows after {}".format(len(new_rows), start))
            except Exception as e:
                self.logger.info("Missing time insertion failed for {}".format(start))

        self.close()