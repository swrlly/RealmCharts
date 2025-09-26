from .interface import ETLJob

# modifies maintenance
# basic cleaning: filling missing time indices

class Maintenance(ETLJob):

    def __init__(self, db_connection, logger):
        super().__init__(db_connection, logger)
        self.insert_one = self.log_exceptions(self.insert_one)

    def insert_one(self, row : list) -> list:
        """Insert one new maintenance status"""
        with self.db_connection.connect() as (conn, cursor):
            cursor.execute("INSERT INTO maintenance VALUES (?, ?, ?);", row)
            conn.commit()

    def insert_missing_times(self) -> None:
        """
        Fill maintenance table with missing times from playersOnline
        # 9/10 1757494200 1757500200
        # 9/2 1756803300 1756816200
        """
        add = []
        with self.db_connection.connect() as (conn, cursor):
            cursor.execute("""SELECT playersOnline.timestamp
            FROM playersOnline
            LEFT JOIN maintenance
            ON playersOnline.timestamp = maintenance.timestamp
            WHERE maintenance.timestamp IS NULL;""")
            missing = cursor.fetchall()
            for time in missing:
                if 1757494200 <= time[0] <= 1757500200 or 1756803300 <= time[0] <= 1756816200:
                    add.append((time[0], 0, None))
                else:
                    add.append((time[0], 1, None))
            try:
                cursor.executemany("INSERT INTO maintenance VALUES (?,?,?);", add)
                conn.commit()
                self.logger.info(f"Inserted {len(add)} rows into maintenance.")
            except Exception as e:
                self.logger.error(f"Failed to insert missing rows in maintenance: {e}")
    
    def get_maintenance_now(self) -> list:

        with self.db_connection.connect() as (conn, cursor):
            cursor.execute("SELECT timestamp, online, estimated_time FROM maintenance WHERE timestamp = (SELECT max(timestamp) FROM maintenance);")
            results = cursor.fetchone()
            return results