import time
import logging
import datetime as dt
from tasks import Tasks
from threading import Thread
from logger import create_logger


def main():

    create_logger("logs")
    logger = logging.getLogger("Main")
    logger.info("Started program.")

    db_link = "data/players.db"
    links = open("link", "r").read().strip().split("\n")
    tasks = Tasks(links, db_link, logger)
    tasks.on_startup(int(time.time()))
    time.sleep(60 - time.time() % 60)
    clock = time.monotonic()
    current_hour = dt.datetime.now().hour
    while True:

        now = int(time.time())
        # queue maintenance status first
        tasks.get_maintenance_status(now)
        tasks.get_player_count(now)
        # get reviews every hour, nserted after next playercount lookup
        if dt.datetime.now().hour - current_hour != 0:
            thread = Thread(target = tasks.get_steam_reviews)
            thread.start()
        current_hour = dt.datetime.now().hour
        tasks.insert_into_database()
        # clean player data after inserting. restrict last 48 hours for speedier query
        # needs to be fast since frontend depends on playersCleaned
        tasks.clean_playercount_data(window = now - 48 * 60 * 60)
        if now % (5 * 60) == 0:
            tasks.group_cleaned_player_data()
            tasks.get_new_forecast_once()
            if now % (6 * 60 * 60) == 0:
                tasks.train_forecaster()
        time.sleep(60 - (time.monotonic() - clock) % 60)

if __name__ == "__main__":
    main()
