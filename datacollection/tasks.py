import re
import logging
import requests
from queue import Queue
from database import Database
from get_steam_reviews import SteamReviews


class Tasks:

    def __init__(self, links, db_link, logger):
        self.player_link = links[0]
        self.maint_link = links[1]
        self.logger = logger
        self.db_connection = Database(db_link, logger)
        self.headers = {
            "User-Agent": "UnityPlayer/2021.3.16f1 (UnityWebRequest/1.0, libcurl/7.84.0-DEV)",
            "Accept": "*/*",
            "Accept-Encoding": "deflate, gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Unity-Version": "2021.3.16f1"
        }
        self.review_getter = SteamReviews(logger)
        self.data_to_insert = Queue()

    def get_maintenance_status(self, time) -> None:
        content = ""
        online = None
        estimated_time = None
        try:
            content = requests.post(self.maint_link, headers = self.headers).content.decode("utf-8")
        except Exception as e:
            self.logger.info("Exception while requesting maintenance status.")
            self.data_to_insert.put({"maintenance": [time, online, estimated_time]})
            #self.db_connection.insert_new_maintenance([time, online, estimated_time])

        maint = re.search("<Maintenance>(.+)</Maintenance>", content)
        if maint == None:
            online = True
            self.data_to_insert.put({"maintenance": [time, online, estimated_time]})
            #self.db_connection.insert_new_maintenance([time, online, estimated_time])
        else:
            online = False
            estimated_time = int(re.search("<Time>(.+)</Time>", maint.group(0)).group(1))
            self.data_to_insert.put({"maintenance": [time, online, estimated_time]})
            #self.db_connection.insert_new_maintenance([time, online, estimated_time])

    def get_player_count(self, time) -> None:
        count = None
        try:
            count = int(requests.get(self.player_link).content)
        except Exception as e:
            self.logger.info("Exception while requesting player count.")
        self.data_to_insert.put({"playersOnline": [time, count]})
        #self.db_connection.insert_new_playercount([time, count])

    def get_steam_reviews(self):
        reviews = self.review_getter.get_all_reviews()
        self.data_to_insert.put({"steamReviews": reviews})

    def insert_into_database(self):
        while not self.data_to_insert.empty():
            item = self.data_to_insert.get()
            if "playersOnline" in item:
                self.db_connection.insert_new_playercount(item["playersOnline"])
            elif "maintenance" in item:
                self.db_connection.insert_new_maintenance(item["maintenance"])
            elif "steamReviews" in item:
                self.db_connection.insert_reviews(item["steamReviews"])
            self.data_to_insert.task_done()
        print('done')

        