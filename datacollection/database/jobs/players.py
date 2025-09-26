from .interface import ETLJob

# modifies playersOnline, raw player data
# basic cleaning: filling missing time indices

class Players(ETLJob):

    def __init__(self, db_connection, logger):
        super().__init__(db_connection, logger)
        self.insert_one = self.log_exceptions(self.insert_one)
        self.get_nonnull_rows = self.log_exceptions(self.get_nonnull_rows)
        self.insert_nulls = self.log_exceptions(self.insert_nulls)

    def insert_one(self, row : list) -> None:
        """Inserts one new player count observation"""

        with self.db_connection.connect() as (conn, cursor):
            cursor.execute("INSERT INTO playersOnline VALUES (?, ?);", row)
            conn.commit()

    def get_nonnull_rows(self, start, end = None):
        """
        Return rows with start <= timestamp < end with non null playercount
        If only start, return 1 row.
        """

        rows = []
        
        with self.db_connection.connect() as (conn, cursor):
            if end == None:
                cursor.execute("SELECT * FROM playersOnline WHERE timestamp = {} AND players NOT NULL;".format(start))
                rows = cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM playersOnline WHERE timestamp >= {} AND timestamp < {} AND players NOT NULL;".format(start, end))
                rows = cursor.fetchall()

        return rows

    def insert_nulls(self, start, end) -> None:
        """Replace existing rows having start <= timestamp < end with NULL."""
        
        rows = self.get_nonnull_rows(start, end)
        rows = [{"players": None, "timestamp": i[0]} for i in rows]
        
        with self.db_connection.connect() as (conn, cursor):
            cursor.executemany("UPDATE playersOnline SET players = :players WHERE timestamp = :timestamp;", rows)
            conn.commit()
    
    def insert_missing_times(self) -> int:
        """
        Fill in missing time intervals over 2 minutes with NA.
        Used to ensure time series index has at least one observation per minute
        """

        ctr = 0

        with self.db_connection.connect() as (conn, cursor):
            # get starting time of gap and total missing seconds
            cursor.execute("""
            SELECT timestamp,
            row_num,
            next_time - timestamp AS difference
            FROM 
            (SELECT *, 
                ROW_NUMBER() OVER () as row_num,
                LEAD(timestamp, 1) OVER (ORDER BY timestamp ASC) as next_time
                FROM playersOnline)
            WHERE difference > 120;""")
            missing = cursor.fetchall()
            
            for row in missing:
                start = row[0]
                width = row[2]
                new_rows = []
                for add in range(60, width, 60):
                    new_rows.append((start + add, None))
                try:
                    cursor.executemany("INSERT INTO playersOnline VALUES (?,?);", new_rows)
                    conn.commit()
                    ctr += cursor.rowcount
                    self.logger.info("Inserted {} rows after {}".format(len(new_rows), start))
                except Exception as e:
                    self.logger.error("Missing time insertion failed for {}".format(start))

        return ctr