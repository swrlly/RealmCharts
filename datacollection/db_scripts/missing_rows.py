import sys
from pathlib import Path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from database import Database
import logging
from logger import create_logger

create_logger("logs")
database = Database("../data/players.db")
start = 1757389977
end = 1757423614
# host was down, incorrect playercounts. 
# remove 29 minutes of new data for 30 min window to update correctly
database.fill_null(start, end)
database.logger.info("Filled host down times with null.")
# create entries for missing times: my bot/host was down
database.fill_missing_times()
database.logger.info("Created missing rows with null.")
