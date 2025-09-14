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
    current_day = dt.datetime.now().day

    while True:

        now = int(time.time())
        tasks.get_maintenance_status(now)
        tasks.get_player_count(now)
        num_reviews = tasks.db_connection.count_reviews()[0]
        # get reviews every day
        if dt.datetime.now().day - current_day != 0:
            thread = Thread(target = tasks.get_steam_reviews)
            thread.start()
            logger.info("Getting steam reviews.")
        # review data inserted after next playercount lookup
        tasks.insert_into_database()

        current_day = dt.datetime.now().day
        time.sleep(60 - (time.monotonic() - clock) % 60)
        


if __name__ == "__main__":
    main()
