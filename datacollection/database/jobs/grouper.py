from .interface import ETLJob

# modifies playersGrouped, reviewsGrouped

class Grouper(ETLJob):

    def __init__(self, db_connection, logger):
        super().__init__(db_connection, logger)
        self.group_cleaned_data = self.log_exceptions(self.group_cleaned_data)
        self.update_reviews_grouped = self.log_exceptions(self.update_reviews_grouped)

    def group_cleaned_data(self) -> int:
        """
        Updates `playersGrouped`
        Automates player data cleaning/transforming -> ready for forecasting
        Group cleaned data into 5 min intervals, standardizes timestamp into beginning of 5 min interval
        """
        with self.db_connection.connect() as (conn, cursor):
            query = """SELECT unixepoch(year || "-" || month || "-" || day || " " || hour || ":" || substr("00"||MIN(minute),-2,2) || ":00") as ts_start_of_minute_group,
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
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.executemany("INSERT OR REPLACE INTO playersGrouped VALUES (?,?,?,?);", [(i[0], i[1], i[2], i[3]) for i in rows])
            conn.commit()
            return cursor.rowcount

    def update_reviews_grouped(self) -> None:
        """
        Update `reviewsGrouped` view after done scraping steam
        get proportion of positive reviews over entire game history
        send sums for downstream average calculation in JS because average over averages because days with less reviews (samples) will affect statistics more strongly
        averaging once over the viewing window weighs each review's statistics equally
        """

        with self.db_connection.connect() as (conn, cursor):
            cursor.execute("DELETE FROM reviewsGrouped;")
            conn.commit()

            query = """-- create cumsum of reviews
            -- recommendation_id 61328679 is botting playtime with online botter
            WITH added_date AS (
                SELECT 
                    timestamp_created,
                    voted_up,
                    playtime_last_two_weeks,
                    playtime_forever,
                    playtime_at_review,
                    SUM(voted_up) OVER (ORDER BY timestamp_created) AS total_votes_up,
                    ROW_NUMBER() OVER (ORDER BY timestamp_created) AS total_votes,
                    strftime("%Y", DATETIME(timestamp_created, "unixepoch")) AS year,
                    strftime("%m", DATETIME(timestamp_created, "unixepoch")) AS month,
                    strftime("%d", DATETIME(timestamp_created, "unixepoch")) AS day
                FROM steamReviews)

            -- create statistics by day
            SELECT 
                unixepoch(MIN(year) || "-" || MIN(month) || "-" || MIN(day)) as timestamp,
                COUNT(timestamp_created) as daily_total_reviews,
                ROUND(MAX(total_votes_up)*1.0 / MAX(total_votes), 5) as total_proportion_positive, -- max gets EoD statistics; most updated.
                CAST(SUM(playtime_last_two_weeks) AS INT) as daily_total_playtime_last_two_weeks,
                SUM(voted_up) as daily_total_votes_up, 
                SUM(playtime_at_review) as daily_total_playtime_at_review,
                SUM(playtime_forever) as daily_total_playtime_forever
            FROM added_date
            GROUP BY year, month, day;"""
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.executemany("INSERT OR REPLACE INTO reviewsGrouped VALUES (?,?,?,?,?,?,?);", results)
            conn.commit()

    def select_grouped_data(self) -> list:
        
        with self.db_connection.connect() as (conn, cursor):
            cursor.execute("SELECT * FROM playersGrouped;")
            result = cursor.fetchall()
            return result