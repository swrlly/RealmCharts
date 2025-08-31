import time
import logging
import requests
from Logger import CreateLogger
from Database import Database

clock = time.monotonic()
link = "https://realmstock.network/Public/PlayersOnline"

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

if __name__ == "__main__":
    main()