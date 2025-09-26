from .interface import ETLJob

# modifies playersCleaned, cleans playersOnline
# auto sets bugged data to null + untrustworthy
# sets maintenance to 0 + trustworthy
#  - 1 hr after maintenance = untrustworthy
#  - 1 hr after bugged data = untrustworthy

class Cleaner(ETLJob):

    def __init__(self, db_connection, logger):
        super().__init__(db_connection, logger)
        self.update_players_cleaned_with_new_data = self.log_exceptions(self.update_players_cleaned_with_new_data)
        self.copy_into_players_cleaned = self.log_exceptions(self.copy_into_players_cleaned)

    def clean_all_playercount_data(self, window = None) -> None:
        # set player counts during maintenance to 0 (for maintenances before 9/20/2025)
        # set untrustworthy identical playercounts 10 minutes or greater to null
        # saw a 5 minute contiguous block that was not an error

        with self.db_connection.connect() as (conn, cursor):
            self.update_players_cleaned_with_new_data()
            # start with untrustworthy times
            # query gets all untrustworthy groups from unclean raw data
            get_sequential_identical_pc = """SELECT 
            timestamp,
            prev_ts_9,
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
                LAG(timestamp, 9) OVER (ORDER BY timestamp ASC) AS prev_ts_9
                FROM playersOnline """
            if window != None:  get_sequential_identical_pc += "WHERE timestamp >= {}".format(window)
            get_sequential_identical_pc += """) 
            WHERE players = prev_pc_1 
                AND players = prev_pc_2 AND players = prev_pc_3 AND players = prev_pc_4
                AND players = prev_pc_5 AND players = prev_pc_6 AND players = prev_pc_7
                AND players = prev_pc_8 AND players = prev_pc_9;"""
            cursor.execute(get_sequential_identical_pc)
            rows = cursor.fetchall()

            left, right = [], []
            idx = 0
            while idx < len(rows):
                left.append(rows[idx][1])
                right.append(rows[idx][0])
                # new sequential group, none captures the final group since row_num is LEAD
                if rows[idx][2] == None or rows[idx][2] > 1:
                    start, end = min(left), max(right)
                    cursor.execute("SELECT * FROM playersOnline WHERE timestamp >= ? AND timestamp <= ?;", (start, end))
                    res = cursor.fetchall()
                    # set players to None since playersCleaned is used in frontend visualization. don't show bugged data.
                    res = [{"timestamp": i[0], "players": None, "trustworthiness": 0} for i in res]
                    try:
                        cursor.executemany("INSERT OR REPLACE INTO playersCleaned VALUES (:timestamp, :players, :trustworthiness);", res)
                        conn.commit()
                    except Exception as e:
                        self.logger.error(f"Failed to set sequential player counts to null: {e}")
                    # now, assign in the future of this group +60 minutes to also be untrustworthy, due to data collector's data being unique seen last 60 min
                    # effect: +60 post maintenance is automatically untrustworthy
                    cursor.execute(f"SELECT * FROM playersOnline WHERE timestamp > {end} AND timestamp <= {end + 60 * 60};")
                    res = cursor.fetchall()
                    res = [{"timestamp": i[0], "players": i[1], "trustworthiness": 0} for i in res]
                    try:
                        cursor.executemany("INSERT OR REPLACE INTO playersCleaned VALUES (:timestamp, :players, :trustworthiness);", res)
                        conn.commit()
                    except Exception as e:
                        self.logger.error(f"Failed to set post-sequential player count trustworthiness to 0: {e}")
                    left, right = [], []
                idx += 1

            # now set maintenance playercounts to 0 and trustworthiness back to 1
            # do this 2nd since untrustworthy times are definitely during maintenance
            get_maintenance_times = """SELECT playersOnline.timestamp
            FROM playersOnline
            LEFT JOIN maintenance
            ON playersOnline.timestamp = maintenance.timestamp
            WHERE maintenance.online = 0;"""
            cursor.execute(get_maintenance_times)
            rows = cursor.fetchall()
            try: 
                cursor.executemany("INSERT OR REPLACE INTO playersCleaned VALUES (?,?,?);", [(i[0], 0, 1) for i in rows])
                conn.commit()
            except Exception as e:
                self.logger.error(f"Failed to set maintenance player counts to 0: {e}")

            # finally, deal with trustworthiness for times I manually removed with my one-off script / random null values
            get_one_off_missed_trustworthiness = """SELECT *
            FROM playersCleaned
            WHERE (1756816226 <= timestamp AND timestamp <= 1756820786) OR (1757500219 <= timestamp AND timestamp <= 1757504179) OR players IS NULL;"""
            cursor.execute(get_one_off_missed_trustworthiness)
            rows = cursor.fetchall()
            try:
                cursor.executemany("INSERT OR REPLACE INTO playersCleaned VALUES (?,?,?);", [(i[0], i[1], 0) for i in rows])
                conn.commit()
            except Exception as e:
                self.logger.error(f"Failed to set one-off player counts post-maintenance / null value trustworthiness to 0: {e}")

    def copy_into_players_cleaned(self) -> None:
        """
        Copy all data from playersOnline into playersCleaned, if missing
        Run once on startup
        """
        with self.db_connection.connect() as (conn, cursor):
            cursor.execute("SELECT * FROM playersOnline;")
            rows = cursor.fetchall()
            # default trustworthiness
            cursor.executemany("INSERT OR IGNORE INTO playersCleaned VALUES (?,?,?);", [i + (1,) for i in rows])
            conn.commit()
            self.logger.info(f"Copied {cursor.rowcount} rows from playersOnline into playersCleaned")

    def update_players_cleaned_with_new_data(self) -> None:
        """
        Update playersCleaned with new data from playersOnline
        Used before cleaning playersOnline -> playersCleaned
        """
        with self.db_connection.connect() as (conn, cursor):
            query = """SELECT playersOnline.timestamp, playersOnline.players
            FROM playersOnline
            LEFT JOIN playersCleaned
            ON playersOnline.timestamp = playersCleaned.timestamp
            where playersCleaned.timestamp IS NULL;"""
            cursor.execute(query)
            rows = cursor.fetchall() # should only be one row if this program hasn't missed any minutes
            cursor.executemany("INSERT INTO playersCleaned VALUES (?,?,?);", [(i[0], i[1], 1) for i in rows])
            conn.commit()