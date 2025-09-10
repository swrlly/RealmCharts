import os
import time
import logging
import requests
from database import Database
from logger import create_logger

clock = time.monotonic()
link = open("link", "r").read().strip()
db_link = "data/players.db"

def main():

    create_logger("logs")
    logger = logging.getLogger("Main")

    while True:

        t = int(time.time())
        database = Database(db_link)
        count = None

        try:
            count = int(requests.get(link).content)
        except Exception as e:
            logger.info("Exception while requesting player count.")

        database.insert_new_row([t, count])
        time.sleep(60 - (time.monotonic() - clock) % 60)

if __name__ == "__main__":
    main()
