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
    thread = Thread(target = tasks.on_startup, args = (int(time.time()), ))
    thread.start()
    time.sleep(60.1 - time.time() % 60)
    clock = time.monotonic()
    current_hour = dt.datetime.now().hour
    while True:

        now = int(time.time())
        if now % (60 * 60) == 0:
            thread = Thread(target = tasks.get_steam_reviews)
            thread.start()

        tasks.one_minute_tasks(now)

        if now % (5 * 60) == 0:
            #if now % (6 * 60 * 60) == 0:
            #    tasks.five_minute_tasks(defer = True)
            #    thread = Thread(target = tasks.train_forecaster)
            #    thread.start()
            #else:
            tasks.five_minute_tasks(defer = False)

        
        time.sleep(60 - (time.monotonic() - clock) % 60)

if __name__ == "__main__":
    main()
