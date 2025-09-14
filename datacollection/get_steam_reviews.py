import time
import requests
import logging
from typing import Any

# api reference: https://partner.steamgames.com/doc/store/getreviews
# 100,000 calls for steam api everyday.

class SteamReviews:

    def __init__(self, logger):
        self.url = "https://store.steampowered.com/appreviews/200210"
        self.params = {
            "json": 1,
            "filter": "all",
            "language": "all",
            "num_per_page": 100,
            "day_range": 1, # setting to 1 gets all reviews
            "purchase_type": "all",
            "cursor": "*"
        }
        self.logger = logger

    def query_once(self) -> dict:
        try:
            result = requests.get(self.url, params = self.params).json()
        except Exception as e:
            self.logger.info(f"Error while scraping reviews: {e}")
            return
        
        # only first set of results tell you how many total reviews there are
        if "total_reviews" in result["query_summary"]:
             self.logger.info(f"Total reviews to scrape: {result["query_summary"]["num_reviews"]}")

        self.params["cursor"] = result["cursor"].encode()

        if result["query_summary"]["num_reviews"] == 0:
            return {}
        return self.parse_result(result)

    def parse_result(self, result: dict) -> list(dict[Any, Any]):
        res = []
        for review in result["reviews"]:
            add = {
                "recommendation_id": int(review["recommendationid"]),
                "author_id": int(review["author"]["steamid"]),
                "playtime_forever": int(review["author"]["playtime_forever"]),
                "playtime_last_two_weeks": int(review["author"]["playtime_last_two_weeks"]),
                "playtime_at_review": int(review["author"]["playtime_at_review"]),
                "last_played": int(review["author"]["last_played"]),
                "language": review["language"],
                "review": review["review"],
                "timestamp_created": int(review["timestamp_created"]),
                "timestamp_updated": int(review["timestamp_updated"]),
                "voted_up": bool(review["voted_up"]),
                "votes_up": int(review["votes_up"]),
                "votes_funny": int(review["votes_funny"]),
                "comment_count": int(review["comment_count"])
            }
            res.append(add)
        return res

    def get_all_reviews(self):
        # batch scrape reviews, don't insert into db one by one.

        all_reviews = []
        stop = False
        self.logger.info("Starting RotMG review scraping from Steam...")

        while not stop:
            res = self.query_once()
            if not res:
                break
            all_reviews += res

        self.logger.info(f"Finished scraping {len(all_reviews)} reviews.")
        return all_reviews

    
if __name__ == "__main__":
    s = SteamReviews()
    s.get_all_reviews()