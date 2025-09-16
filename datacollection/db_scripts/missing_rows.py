import sys
from pathlib import Path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from database import Database
import logging
from logger import create_logger

create_logger("logs")
logger = logging.getLogger("missing_rows")
database = Database("../data/players.db", logger)
# left entry is start, right entry is end. will set *existing rows* to null.
remove = [
    [1757389977, 1757423614], # bots were down
    [1757493559, 1757500579 + 1] # 9/10/2025 8:50 - 10:30 maintenance
]

# fill existing rows with null. use cases:
#   - host was down, incorrect playercounts. bots relogging in
#       - remove 29 minutes of new data after relogging in to allow users to be seen within 29 minutes
#           - fine assumption because shatters can take less than 30 minutes, longest dungeon
#   - maintenance time, incorrect playercounts
#       - set maintenance times to null, we will automate this
#       - also consider setting to null 29 minutes of new data after maintenance. pros and cons:
#           - pros: 
#               - makes time series estimation better due to excluding maintenance shock effects
#               - bots could log in some time after maintenance ends
#           - cons: model the shock effect directly in time series, and only set maintenance times to null
for r in remove:
    database.fill_null(r[0], r[1])
    database.logger.info(f"Filled playercounts between {r[0]} to {r[1]} with null.")
# create entries for missing times. use cases:
#   - my program was down (due to user error/bot not restarting after restart)
#   - host was down
database.fill_missing_times()
database.logger.info("Created missing rows between time points with null.")