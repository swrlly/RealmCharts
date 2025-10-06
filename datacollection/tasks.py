import re
import os
import gc
import requests
from dotenv import load_dotenv

from queue import Queue
from database import ETLFactory
from forecaster import Forecaster
from get_steam_reviews import SteamReviews

load_dotenv()

class Tasks:

    def __init__(self, links, db_link, logger):
        self.player_link = links[0]
        self.maint_link = links[1]
        self.logger = logger
        self.etl_factory = ETLFactory(db_link, logger)
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
        self.simulate_maintenance = os.getenv("SIMULATE_MAINTENANCE", False).lower() == "true"
        self.simulate_buggy_data = os.getenv("SIMLUATE_BUGGY_DATA", False).lower() == "true"

    def on_startup(self, time):
        # get latest data
        self.get_maintenance_status(time)
        self.get_player_count(time)
        self.insert_into_database()
        # insert current playercount now since fill_missing_times needs one time point now
        self.etl_factory.get_players().insert_missing_times()
        self.etl_factory.get_maintenance().insert_missing_times()
        self.etl_factory.get_cleaner().copy_into_players_cleaned()
        self.clean_playercount_data(window = None)
        self.group_cleaned_player_data()
        self.etl_factory.get_grouper().update_reviews_grouped()
        self.train_forecaster()

    def train_forecaster(self):
        # train forecaster and get first forecast
        data = self.etl_factory.get_grouper().select_grouped_data()
        # memory management
        if hasattr(self, "forecaster"):
            if hasattr(self.forecaster, "result"):
                del self.forecaster.result
            del self.forecaster
        gc.collect()
        self.forecaster = Forecaster(self.logger)
        self.forecaster.prepare_data(data)
        self.forecaster.train_model()
        forecast, params = self.forecaster.get_forecast()
        self.etl_factory.get_forecast().insert_into_forecast_horizon(forecast, params)
        self.etl_factory.get_forecast().insert_into_forecast(forecast, params)

    def get_new_forecast_once(self):
        # get new forecast given one new data point
        # first, check if maintenance
        maintenance_time = self.etl_factory.get_maintenance().get_maintenance_now()
        if maintenance_time[1] == 0:
            self.etl_factory.get_forecast().generate_forecast_during_maintenance(maintenance_time)

        # effects:
        # 1. upon startup, if model takes > 5 min to train, delay returning new forecast every 5 min
        # 2. upon new training cycle, if model takes > 5 min to train, use old forecaster results to return forecast for users
        if self.forecaster.result is not None:
            # allow forecaster to interpolate through maintenance
            data = self.etl_factory.get_grouper().select_grouped_data()
            forecast, params = self.forecaster.update_forecast_once(data)
            self.etl_factory.get_forecast().insert_into_forecast_horizon(forecast, params)
            self.etl_factory.get_forecast().insert_into_forecast(forecast, params)

    def update_forecast_horizon_with_actuals(self):
        self.etl_factory.get_forecast().update_forecast_horizon_with_actuals()

    def group_cleaned_player_data(self):
        self.etl_factory.get_grouper().group_cleaned_data()

    def clean_playercount_data(self, window):
        self.etl_factory.get_cleaner().clean_all_playercount_data(window)

    def one_minute_tasks(self, now):
        # queue maintenance status first
        self.get_maintenance_status(now)
        self.get_player_count(now)
        self.insert_into_database()
        self.clean_playercount_data(window = now - 24 * 60 * 60)

    def five_minute_tasks(self, defer = False):
        """`defer` = True when training new forecaster, False when using .append`"""
        self.group_cleaned_player_data()
        if not defer:
            self.get_new_forecast_once()
            self.update_forecast_horizon_with_actuals()

    # data collection mechanism

    def get_player_count(self, time) -> None:
        """Get player count at `time`"""
        if self.simulate_buggy_data:
            self.data_to_insert.put({"playersOnline": [time, 1635]})
            return

        count = None
        try:
            count = int(requests.get(self.player_link).content)
        except Exception as e:
            self.logger.info("Exception while requesting player count.")
        self.data_to_insert.put({"playersOnline": [time, count]})

    def get_maintenance_status(self, time) -> None:
        # assumption: <Maintenance> tag only appears during maintenance, and not before when people are asked to log out
        # assumption is true, verified with 9/17 maintenance
        if self.simulate_maintenance:
            self.data_to_insert.put({"maintenance": [time, 0, time + 60 * 60 * 2]})
            return

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

    def get_steam_reviews(self):
        reviews = self.review_getter.get_all_reviews()
        self.data_to_insert.put({"steamReviews": reviews})

    def insert_into_database(self):
        """
        Batch job to update scraped playercount/maintenance/reviews at one time point.
        Call this after you have collected all data
        """
        is_maintenance = False

        while not self.data_to_insert.empty():

            item = self.data_to_insert.get()

            # check if maintenance, maintenance data will always come before player data due to FIFO Queue
            if "maintenance" in item:
                self.etl_factory.get_maintenance().insert_one(item["maintenance"])
                if item["maintenance"][1] == False:
                    is_maintenance = True
                pass
            elif "playersOnline" in item:
                if is_maintenance:
                    self.etl_factory.get_players().insert_one([item["playersOnline"][0], 0])
                else:
                    self.etl_factory.get_players().insert_one(item["playersOnline"])
            elif "steamReviews" in item:
                self.etl_factory.get_reviews().insert_reviews(item["steamReviews"])
                self.etl_factory.get_grouper().update_reviews_grouped()
            self.data_to_insert.task_done()
