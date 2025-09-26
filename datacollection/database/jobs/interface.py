#from abc import ABC, abstractmethod

class ETLJob:#(ABC):

    def __init__(self, db_connection, logger):
        self.db_connection = db_connection
        self.logger = logger
    
    @property
    def log_exceptions(self):
        return self.db_connection.handle_db_exceptions
    """
    @abstractmethod
    def one_minute_jobs(self):
        pass

    @abstractmethod
    def five_minute_jobs(self):
        pass

    @abstractmethod
    def one_hour_jobs(self):
        pass

    @abstractmethod
    def six_hour_jobs(self):
        pass
    """