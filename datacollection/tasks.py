import re
import logging
import requests
from queue import Queue
from database import Database
from forecaster import Forecaster
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
        self.forecaster = None
        self.data_to_insert = Queue()

    def on_startup(self, time):
        self.get_player_count(time)
        self.get_maintenance_status(time)
        self.insert_into_database()
        # call when program starts, don't queue since data is needed downstream
        n_missing = self.db_connection.fill_missing_times()
        self.logger.info(f"Created {n_missing} missing rows between time points with null.")
        # fill maintenance table w missing player times
        self.db_connection.fill_maintenance_missing_times()
        self.db_connection.copy_into_players_cleaned()
        self.clean_playercount_data(window = None)
        self.group_cleaned_player_data()
        self.train_forecaster()

    def train_forecaster(self):
        # train forecaster and get first forecast
        data = self.db_connection.select_grouped_data()
        self.forecaster = Forecaster()
        self.forecaster.prepare_data(data)
        self.forecaster.train_model()
        forecast = self.forecaster.get_forecast()
        self.db_connection.insert_into_forecast(forecast)

    def get_new_forecast_once(self):
        # get new forecast given one new data point
        # first, check if maintenance
        maintenance_time = self.db_connection.select_maintenance()
        if maintenance_time[1] == 0:
            # todo
            return

        data = self.db_connection.select_grouped_data()
        forecast = self.forecaster.update_forecast_once(data)
        self.db_connection.insert_into_forecast(forecast)

    def group_cleaned_player_data(self):
        # transform data to be ready for forecasting
        self.db_connection.group_cleaned_data()

    def clean_playercount_data(self, window):
        # insert new entries from playersOnline into playersCleaned
        # set <= 9/20 maintenance to 0, set bugged sequential player data to null
        self.db_connection.clean_all_playercount_data(window)

    def get_maintenance_status(self, time) -> None:
        # assumption: <Maintenance> tag only appears during maintenance, and not before when people are asked to log out
        # assumption is true, verified with 9/17 maintenance
        content = ""
        online = None
        estimated_time = None
        try:
            content = requests.post(self.maint_link, headers = self.headers).content.decode("utf-8")
        except Exception as e:
            self.logger.info("Exception while requesting maintenance status.")
            self.data_to_insert.put({"maintenance": [time, online, estimated_time]})
            return

        maint = re.search("<Maintenance>(.+)</Maintenance>", content)
        if maint == None:
            online = True
        else:
            online = False
            estimated_time = int(re.search("<Time>(.+)</Time>", maint.group(0)).group(1))

        self.data_to_insert.put({"maintenance": [time, online, estimated_time]})

    def get_player_count(self, time) -> None:
        # get player count at one time point
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
        # batch job to update all data at one time point.
        # call this after you have collected all data

        is_maintenance = False

        while not self.data_to_insert.empty():

            item = self.data_to_insert.get()

            # check if maintenance, maintenance data will always come before player data due to queue being FIFO
            if "maintenance" in item:
                self.db_connection.insert_new_maintenance(item["maintenance"])
                if item["maintenance"][1] == False:
                    is_maintenance = True
            elif "playersOnline" in item:
                if is_maintenance:
                    self.db_connection.insert_new_playercount([item["playersOnline"][0], 0])
                else:
                    self.db_connection.insert_new_playercount(item["playersOnline"])
            elif "steamReviews" in item:
                self.db_connection.insert_reviews(item["steamReviews"])
            self.data_to_insert.task_done()