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
    clock = time.monotonic()
    current_hour = dt.datetime.now().hour

    tasks.on_startup()

    while True:

        now = int(time.time())
        # queue maintenance status first
        tasks.get_maintenance_status(now)
        tasks.get_player_count(now)
        # get reviews every hour
        if dt.datetime.now().hour - current_hour != 0:
            thread = Thread(target = tasks.get_steam_reviews)
            thread.start()
        current_hour = dt.datetime.now().hour

        # review data inserted after next playercount lookup
        tasks.insert_into_database()
        tasks.clean_playercount_data()
        time.sleep(60 - (time.monotonic() - clock) % 60)

if __name__ == "__main__":
    main()
