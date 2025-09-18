import time
import requests
import logging

# api reference: https://partner.steamgames.com/doc/store/getreviews
# 100,000 calls for steam api everyday.
# https://store.steampowered.com/appreviews/200210?json=1&filter=recent&language=all&num_per_page=100&day_range=1&purchase_type=all&cursor=*

class SteamReviews:

    def __init__(self, logger):
        self.url = "https://store.steampowered.com/appreviews/200210"
        self.params = {
            "json": 1,
            "filter": "recent", # filtering by recent WILL get all reviews
            "language": "all",
            "num_per_page": 100,
            "day_range": 1,
            "purchase_type": "all",
            "cursor": "*"
        }
        self.logger = logger
        self.headers = {
            "Cookie": "" # cookie
        }

    def query_once(self, session) -> dict:
        try:
            result = session.get(self.url, params = self.params, headers = self.headers)
            if "steamCountry" in result.cookies:
                self.headers["Cookie"] = "steamCountry=" + result.cookies["steamCountry"]
        except Exception as e:
            self.logger.info(f"Error while scraping reviews: {e}")
            return

        result = result.json()
        
        # only first set of results tell you how many total reviews there are
        if "total_reviews" in result["query_summary"]:
             self.logger.info(f"Total reviews to scrape: {result['query_summary']['total_reviews']}")
        # if we hit the end
        if result["query_summary"]["num_reviews"] == 0:
            return {}
        old_cursor = self.params["cursor"]
        self.params["cursor"] = result["cursor"].encode()
        return self.parse_result(result, old_cursor)

    def parse_result(self, result: dict, cursor):
        res = []
        for review in result["reviews"]:
            try:
                # playtime_at_review could be missing if user has games hidden
                add = {
                    "recommendation_id": int(review["recommendationid"]),
                    "author_id": int(review["author"]["steamid"]),
                    "playtime_forever": int(review["author"]["playtime_forever"]),
                    "playtime_last_two_weeks": int(review["author"]["playtime_last_two_weeks"]),
                    "playtime_at_review": int(review["author"]["playtime_at_review"]) if "playtime_at_review" in review["author"] else None,
                    "last_played": int(review["author"]["last_played"]),
                    "language": review["language"],
                    "review": review["review"],
                    "timestamp_created": int(review["timestamp_created"]),
                    "timestamp_updated": int(review["timestamp_updated"]),
                    "voted_up": bool(review["voted_up"]),
                    "votes_up": int(review["votes_up"]),
                    "votes_funny": int(review["votes_funny"]),
                    "comment_count": int(review["comment_count"]),
                    "cursor": cursor
                }
                res.append(add)
            except Exception as e:
                self.logger.info(f"Parsing review {review} had error.")

        #self.logger.info(f"Parsed {len(res)} reviews")
        return res

    def get_all_reviews(self):
        # batch scrape reviews, don't insert into db one by one.

        all_reviews = []
        self.logger.info("Starting hourly job for scraping Steam reviews..")

        session = requests.Session()

        while True:
            res = self.query_once(session)
            if not res:
                break
            all_reviews += res

        session.close()

        with open("data/reviews_last_scraped", "w") as f:
            f.write(str(int(time.time())))

        self.logger.info(f"Finished scraping {len(all_reviews)} reviews.")

        return all_reviews

    
if __name__ == "__main__":
    from logger import create_logger
    create_logger("old2")
    logger = logging.getLogger("testing steam reviews")
    s = SteamReviews(logger)
    s.get_all_reviews()
