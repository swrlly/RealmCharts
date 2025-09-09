import os
import time
import logging
import requests
from Database import Database
from Logger import CreateLogger

clock = time.monotonic()
link = open("link", "r").read().strip()

def main():
    CreateLogger("logs")
    logger = logging.getLogger("Main")
    while True:
        try:
            database = Database()
            count = int(requests.get(link).content)
            t = int(time.time())
            database.Write([t, count])
            time.sleep(60 - (time.monotonic() - clock) % 60)
        except Exception as e:
            logger.info("Exception: {}".format(e))
            time.sleep(60 - (time.monotonic() - clock) % 60)

if __name__ == "__main__":
    main()
