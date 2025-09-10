import re
import logging
import requests
from database import Database

class Tasks:

    def __init__(self, links, db_link):
        self.player_link = links[0]
        self.maint_link = links[1]
        self.logger = logging.getLogger("Tasks")
        self.db_connection = Database(db_link)
        self.headers = {
            "User-Agent": "UnityPlayer/2021.3.16f1 (UnityWebRequest/1.0, libcurl/7.84.0-DEV)",
            "Accept": "*/*",
            "Accept-Encoding": "deflate, gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Unity-Version": "2021.3.16f1"
        }

    def get_maintenance_status(self, time) -> None:
        content = ""
        online = None
        estimated_time = None
        try:
            content = requests.post(self.maint_link, headers = self.headers).content.decode("utf-8")
        except Exception as e:
            self.logger.info("Exception while requesting maintenance status.")
            self.db_connection.insert_new_maintenance([time, online, estimated_time])

        maint = re.search("<Maintenance>(.+)</Maintenance>", content)
        if maint == None:
            online = True
            self.db_connection.insert_new_maintenance([time, online, estimated_time])
        else:
            online = False
            estimated_time = int(re.search("<Time>(.+)</Time>", maint.group(0)).group(1))
            self.db_connection.insert_new_maintenance([time, online, estimated_time])

    def get_player_count(self, time) -> None:
        count = None
        try:
            count = int(requests.get(self.player_link).content)
        except Exception as e:
            self.logger.info("Exception while requesting player count.")
        self.db_connection.insert_new_playercount([time, count])
        