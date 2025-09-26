from .connection import DatabaseConnection
from .jobs import *

class ETLFactory:
    def __init__(self, link, logger):
        self.connection = DatabaseConnection(link, logger)
        self.logger = logger
        self._players = None
        self._maintenance = None
        self._reviews = None
        self._forecast = None
        self._cleaner = None
        self._grouper = None
    
    def get_players(self):
        if self._players is None:
            self._players = Players(self.connection, self.logger)
        return self._players

    def get_maintenance(self):
        if self._maintenance is None:
            self._maintenance = Maintenance(self.connection, self.logger)
        return self._maintenance

    def get_reviews(self):
        if self._reviews is None:
            self._reviews = Reviews(self.connection, self.logger)
        return self._reviews

    def get_forecast(self):
        if self._forecast is None:
            self._forecast = Forecast(self.connection, self.logger)
        return self._forecast

    def get_cleaner(self):
        if self._cleaner is None:
            self._cleaner = Cleaner(self.connection, self.logger)
        return self._cleaner

    def get_grouper(self):
        if self._grouper is None:
            self._grouper = Grouper(self.connection, self.logger)
        return self._grouper