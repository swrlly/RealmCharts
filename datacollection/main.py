import time
import logging
from logger import create_logger
from tasks import Tasks


def main():

    create_logger("logs")
    logger = logging.getLogger("Main")
    links = open("link", "r").read().strip().split("\n")
    db_link = "data/players.db"
    tasks = Tasks(links, db_link)
    clock = time.monotonic()
    logger.info("Started program.")
    while True:

        now = int(time.time())
        tasks.get_maintenance_status(now)
        tasks.get_player_count(now)
        time.sleep(60 - (time.monotonic() - clock) % 60)

if __name__ == "__main__":
    main()
