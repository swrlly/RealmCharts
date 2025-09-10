import os
import time
import logging
import requests
from database import Database
from logger import create_logger

clock = time.monotonic()
link = open("link", "r").read().strip()

def main():

    create_logger("logs")
    logger = logging.getLogger("Main")

    while True:

        t = int(time.time())
        database = Database()
        count = None

        try:
            count = int(requests.get(link).content)
        except Exception as e:
            logger.info("Exception while requesting: {}".format(e))

        database.insert([t, count])
        time.sleep(60 - (time.monotonic() - clock) % 60)

if __name__ == "__main__":
    main()
