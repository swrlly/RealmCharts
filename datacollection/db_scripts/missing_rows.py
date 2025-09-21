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
# left entry is start, right entry is end. 
# set +59 min after data came back online due to data generation mechanism
# times are in utc
remove = [
    # 9/2/2025 8:55 - 12:30 maintenance MOTMG 2025
    # data was 17 minutes late
    # for now, just set before data online to null. first starting time is 17 min after maintenance ended. todo
    [1756803326, 1756817186 + 1],
    # data was down, vps issue. set +59
    [1757389977, 1757423614], 
    # 9/10/2025 8:50 - 10:30 maintenance
    # data was 7 minute late, don't set +59 since maintenance. todo
    [1757493559, 1757500579 + 1], 
    # data was down again for 12+ hours, no info on why. this one had an issue where needed another restart after restarting
    # set +59
    [1758006727, 1758065287 + 1], 
    # 9/17/2025 8:55 - 10:30 maintenance
    # my maintenance detector + back up time was correct, but data was down (few hours late)
    # set +59 since way too late to detect maintenance effect
    [1758103207, 1758114307 + 1], 
]

# fill **existing rows** with null. use cases:
#   - host was down, incorrect playercounts. data relogging in
#       - remove 29 minutes of new data after relogging in to allow users to be seen within 29 minutes
#           - fine assumption because shatters can take less than 30 minutes, longest dungeon
#   - maintenance time, incorrect playercounts
#       - set maintenance times to null, we will automate this
#       - also consider setting to null 59 minutes (inclusive) of new data after maintenance. pros and cons:
#           - pros: 
#               - makes time series estimation better due to excluding maintenance shock effects
#               - data could log in some time after maintenance ends
#           - cons: model the shock effect directly in time series, and only set maintenance times to null
for r in remove:
    database.fill_null(r[0], r[1])
    database.logger.info(f"Filled playercounts between {r[0]} to {r[1]} with null.")
# create entries for missing times. use cases:
#   - my program was down (due to user error/bot not restarting after restart)
#   - host was down
n_missing = database.fill_missing_times()
database.logger.info(f"Created {n_missing} missing rows between time points with null.")

# fill maintenance table w missing player times
database.fill_maintenance_missing_times()
database.clean_all_playercount_data()