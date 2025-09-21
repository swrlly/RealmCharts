import logging
import sqlite3

class Database:

    def __init__(self, link, logger):
        self._connection = None
        self._cursor = None
        self.link = link
        self.logger = logger

    def connect(self) -> None:
        # Connect to database and initialize cursor.
        self._connection = sqlite3.connect(self.link)
        self._cursor = self._connection.cursor()

    def close(self) -> None:
        # Close database connection and cursor connection.
        self._cursor.close()
        self._connection.close()

    def group_cleaned_data(self):
        # automates data cleaning/transforming -> ready for forecasting
        # group cleaned data into 5 min intervals, standardizes timestamp into beginning of 5 min interval
        # for modeling, need to decide how to deal with untrustworthy data, especially in an automated setting
        query = """SELECT unixepoch(year || "-" || month || "-" || day || " " || hour || ":" || substr("00"||minute,-2,2) || ":00") as ts_start_of_minute_group,
        AVG(players) as players, 
        MIN(online) as online,
        AVG(trustworthiness) as trustworthiness,
        CASE
            WHEN 0 <= minute AND minute < 5 THEN "00-04"
            WHEN 5 <= minute AND minute < 10 THEN "05-09"
            WHEN 10 <= minute AND minute < 15 THEN "10-14"
            WHEN 15 <= minute AND minute < 20 THEN "15-19"
            WHEN 20 <= minute AND minute < 25 THEN "20-24"
            WHEN 25 <= minute AND minute < 30 THEN "25-29"
            WHEN 30 <= minute AND minute < 35 THEN "30-34"
            WHEN 35 <= minute AND minute < 40 THEN "35-39"
            WHEN 40 <= minute AND minute < 45 THEN "40-44"
            WHEN 45 <= minute AND minute < 50 THEN "45-49"
            WHEN 50 <= minute AND minute < 55 THEN "50-54"
            ELSE "55-59"
        END AS minute_group
        FROM
        (SELECT 
        playersCleaned.timestamp, 
        playersCleaned.players,
        playersCleaned.trustworthiness,
        maintenance.online AS online,
        strftime("%Y", DATETIME(playersCleaned.timestamp, "unixepoch")) AS year,
        strftime("%m", DATETIME(playersCleaned.timestamp, "unixepoch")) AS month,
        strftime("%d", DATETIME(playersCleaned.timestamp, "unixepoch")) AS day,
        strftime("%H", DATETIME(playersCleaned.timestamp, "unixepoch")) as hour,
        strftime("%M", DATETIME(playersCleaned.timestamp, "unixepoch"))*1 AS minute
        from playersCleaned
        LEFT JOIN maintenance
        ON playersCleaned.timestamp = maintenance.timestamp)
        GROUP BY year, month, day, hour, minute_group;"""
        self._cursor.execute(query)
        rows = self._cursor.fetchall()
        try:
            self._cursor.executemany("INSERT OR REPLACE INTO playersGrouped VALUES (?,?,?,?);", [(i[0], i[1], i[2], i[3]) for i in rows])
            self._connection.commit()
        except Exception as e:
            self.logger.info(f"Failed to insert grouped data: {e}")

    def clean_all_playercount_data(self, window = None):
        # set player counts during maintenance to 0 (for maintenances before 9/20/2025)
        # set untrustworthy identical playercounts 10 minutes or greater to null
        # saw a 5 minute contiguous block that was not an error
        self.connect()

        self.update_players_cleaned_with_new_data()
        # start with untrustworthy times
        # query gets all untrustworthy groups from unclean raw data
        get_sequential_identical_pc = """SELECT 
        timestamp,
        prev_ts_4,
        LEAD(row_num, 1) OVER () - row_num AS row_num_lag_diff
        FROM 
            (SELECT *, 
            ROW_NUMBER() OVER () as row_num,
            LAG(players, 1) OVER (ORDER BY timestamp ASC) AS prev_pc_1,
            LAG(players, 2) OVER (ORDER BY timestamp ASC) AS prev_pc_2,
            LAG(players, 3) OVER (ORDER BY timestamp ASC) AS prev_pc_3,
            LAG(players, 4) OVER (ORDER BY timestamp ASC) AS prev_pc_4,
            LAG(players, 5) OVER (ORDER BY timestamp ASC) AS prev_pc_5,
            LAG(players, 6) OVER (ORDER BY timestamp ASC) AS prev_pc_6,
            LAG(players, 7) OVER (ORDER BY timestamp ASC) AS prev_pc_7,
            LAG(players, 8) OVER (ORDER BY timestamp ASC) AS prev_pc_8,
            LAG(players, 9) OVER (ORDER BY timestamp ASC) AS prev_pc_9,
            LAG(timestamp, 4) OVER (ORDER BY timestamp ASC) AS prev_ts_4
            FROM playersOnline """
        if window != None:  get_sequential_identical_pc += "WHERE timestamp >= {}".format(window)
        get_sequential_identical_pc += """) 
        WHERE players = prev_pc_1 
            AND players = prev_pc_2 AND players = prev_pc_3 AND players = prev_pc_4
            AND players = prev_pc_5 AND players = prev_pc_6 AND players = prev_pc_7
	        AND players = prev_pc_8 AND players = prev_pc_9;"""
        self._cursor.execute(get_sequential_identical_pc)
        rows = self._cursor.fetchall()

        left, right = [], []
        idx = 0
        while idx < len(rows):
            left.append(rows[idx][1])
            right.append(rows[idx][0])
            # new sequential group, none captures the final group since row_num is LEAD
            if rows[idx][2] == None or rows[idx][2] > 1:
                start, end = min(left), max(right)
                self._cursor.execute("SELECT * FROM playersOnline WHERE timestamp >= ? AND timestamp <= ?;", (start, end))
                res = self._cursor.fetchall()
                res = [{"timestamp": i[0], "players": None, "trustworthiness": 0} for i in res]
                try:
                    self._cursor.executemany("INSERT OR REPLACE INTO playersCleaned VALUES (:timestamp, :players, :trustworthiness);", res)
                    self._connection.commit()
                except Exception as e:
                    self.logger.info(f"Failed to set sequential player counts to null: {e}")
                # now, assign in the future of this group +60 minutes to also be untrustworthy, due to data collector's data being unique seen last 60 min
                self._cursor.execute(f"SELECT * FROM playersOnline WHERE timestamp > {end} AND timestamp <= {end + 60 * 60};")
                res = self._cursor.fetchall()
                res = [{"timestamp": i[0], "players": i[1], "trustworthiness": 0} for i in res]
                try:
                    self._cursor.executemany("INSERT OR REPLACE INTO playersCleaned VALUES (:timestamp, :players, :trustworthiness);", res)
                    self._connection.commit()
                except Exception as e:
                    self.logger.info(f"Failed to set post-sequential player count trustworthiness to 0: {e}")
                left, right = [], []
            idx += 1

        # now set maintenance playercounts to 0
        # do this 2nd since untrustworthy times are definitely during maintenance, and maintenance really should be 0 for downstream modeling
        get_maintenance_times = """SELECT playersOnline.timestamp
        FROM playersOnline
        LEFT JOIN maintenance
        ON playersOnline.timestamp = maintenance.timestamp
        WHERE maintenance.online = 0;"""
        self._cursor.execute(get_maintenance_times)
        rows = self._cursor.fetchall()
        try: 
            self._cursor.executemany("INSERT OR REPLACE INTO playersCleaned VALUES (?,?,?);", [(i[0], 0, 1) for i in rows])
            self._connection.commit()
        except Exception as e:
            self.logger.info(f"Failed to set maintenance player counts to 0: {e}")

        # finally, deal with trustworthiness for times I manually removed with my one-off script / random null values
        get_one_off_missed_trustworthiness = """SELECT *
        FROM playersCleaned
        WHERE (1756816226 <= timestamp AND timestamp <= 1756820786) OR (1757500219 <= timestamp AND timestamp <= 1757504179) OR players IS NULL;"""
        self._cursor.execute(get_one_off_missed_trustworthiness)
        rows = self._cursor.fetchall()
        try:
            self._cursor.executemany("INSERT OR REPLACE INTO playersCleaned VALUES (?,?,?);", [(i[0], i[1], 0) for i in rows])
            self._connection.commit()
        except Exception as e:
            self.logger.info(f"Failed to set one-off player counts post-maintenance / null value trustworthiness to 0: {e}")

    def copy_into_players_cleaned(self):
        # copy all data from playersOnline into playersCleaned, if missing
        # run once on startup
        self.connect()
        self._cursor.execute("SELECT * FROM playersOnline;")
        rows = self._cursor.fetchall()
        # default trustworthiness
        try:
            self._cursor.executemany("INSERT OR IGNORE INTO playersCleaned VALUES (?,?,?);", [i + (1,) for i in rows])
            self._connection.commit()
            self.logger.info(f"Copied {self._cursor.rowcount} rows from playersOnline into playersCleaned")
        except Exception as e:
            self.logger.info(f"Copying data from playersOnline into playersCleaned failed: {e}")
        self.close()

    def update_players_cleaned_with_new_data(self):
        # update playersCleaned with new data from playersOnline
        query = """SELECT playersOnline.timestamp, playersOnline.players
        FROM playersOnline
        LEFT JOIN playersCleaned
        ON playersOnline.timestamp = playersCleaned.timestamp
        where playersCleaned.timestamp IS NULL;"""
        self._cursor.execute(query)
        rows = self._cursor.fetchall() # should only be one row.
        try:
            self._cursor.executemany("INSERT INTO playersCleaned VALUES (?,?,?);", [(i[0], i[1], 1) for i in rows])
            self._connection.commit()
        except:
            self.logger.info(f"Updating playersCleaned with new data from playersOnline failed: {e}")

        
    def insert_new_playercount(self, row : list) -> None:
        # Insert new playercount.
        self.connect()
        
        try:
            self._cursor.execute("INSERT INTO playersOnline VALUES (?, ?);", row)
            self._connection.commit()
        except Exception as e:
            self.logger.info("Player insertion error at time {}: {}".format(row[0], e))
            
        self.close()

    def get_nonnull_rows(self, start, end = None) -> list:
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

    def fill_null(self, start, end) -> None:
        # Replace existing rows with start <= timestamp < end with NULL.
        rows = self.get_nonnull_rows(start, end)
        rows = [{"players": None, "timestamp": i[0]} for i in rows]

        self.connect()

        try:
            self._cursor.executemany("UPDATE playersOnline SET players = :players WHERE timestamp = :timestamp;", rows)
            self._connection.commit()
        except Exception as e:
            self.logger.info(f"Update null rows operation failed: {e}")

        self.close()
        
    def fill_missing_times(self) -> int:
        # Fill in missing time intervals over 2 minutes with NA.
        # used to ensure time series index has at least one observation per minute
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
        ctr = 0
        for row in missing:
            start = row[0]
            width = row[2]
            new_rows = []
            for add in range(60, width, 60):
                new_rows.append((start + add, None))
            try:
                self._cursor.executemany("INSERT INTO playersOnline VALUES (?,?);", new_rows)
                self._connection.commit()
                ctr += self._cursor.rowcount
                self.logger.info("Inserted {} rows after {}".format(len(new_rows), start))
            except Exception as e:
                self.logger.info("Missing time insertion failed for {}".format(start))

        self.close()

        return ctr

    def insert_new_maintenance(self, row : list) -> list:
        # Insert maintenance status.
        self.connect()

        try:
            self._cursor.execute("INSERT INTO maintenance VALUES (?, ?, ?);", row)
            self._connection.commit()
        except Exception as e:
            self.logger.info("Maintenance insertion error at time {}: {}".format(row[0], e))

        self.close()

    def fill_maintenance_missing_times(self):
        # fill maintenance table with missing times from playersOnline
        # 9/10 1757494200 1757500200
        # 9/2 1756803300 1756816200
        add = []
        self.connect()
        self._cursor.execute("""SELECT playersOnline.timestamp
        FROM playersOnline
        LEFT JOIN maintenance
        ON playersOnline.timestamp = maintenance.timestamp
        WHERE maintenance.timestamp IS NULL;""")
        missing = self._cursor.fetchall()
        for time in missing:
            if 1757494200 <= time[0] <= 1757500200 or 1756803300 <= time[0] <=  1756816200:
                add.append((time[0], 0, None))
            else:
                add.append((time[0], 1, None))
        try:
            self._cursor.executemany("INSERT INTO maintenance VALUES (?,?,?);", add)
            self._connection.commit()
            self.logger.info(f"Inserted {len(add)} rows into maintenance.")
        except Exception as e:
            self.logger.info(f"Failed to insert missing rows in maintenance: {e}")
        self.close()

    def insert_reviews(self, results: list):
        # insert all steam reviews. overwrite old ones with new info (ex. updated review, new upvotes, etc.)

        self.connect()

        try:
            self._cursor.executemany(
                """INSERT OR REPLACE INTO steamReviews VALUES (:recommendation_id, :author_id, :playtime_forever,
                :playtime_last_two_weeks, :playtime_at_review, :last_played, :language, :review, :timestamp_created,
                :timestamp_updated, :voted_up, :votes_up, :votes_funny, :comment_count, :cursor)  ;""", results
                )
            self._connection.commit()
        except Exception as e:
            self.logger.info(f"Updating steam review operation failed: {e}")

        self.close()
        
    def count_reviews(self):
        self.connect()
        self._cursor.execute("SELECT COUNT(*) FROM steamReviews;")
        result = self._cursor.fetchone()
        self.close()
        return result