from .interface import ETLJob

# modifies steamReviews

class Reviews(ETLJob):

    def __init__(self, db_connection, logger):
        super().__init__(db_connection, logger)
        self.insert_reviews = self.log_exceptions(self.insert_reviews)
        self.count_reviews = self.log_exceptions(self.count_reviews)
    
    def insert_reviews(self, results: list) -> None:
        """
        Updates `steamReviews`
        Overwrite old ones with new info (ex. updated review, new upvotes, etc.)
        """

        with self.db_connection.connect() as (conn, cursor):
            cursor.executemany(
                """INSERT OR REPLACE INTO steamReviews VALUES (:recommendation_id, :author_id, :playtime_forever,
                :playtime_last_two_weeks, :playtime_at_review, :last_played, :language, :review, :timestamp_created,
                :timestamp_updated, :voted_up, :votes_up, :votes_funny, :comment_count, :cursor)  ;""", results
                )
            conn.commit()
        
    def count_reviews(self) -> int:
        with self.db_connection.connect() as (conn, cursor):
            cursor.execute("SELECT COUNT(*) FROM steamReviews;")
            result = cursor.fetchone()[0]
            return result