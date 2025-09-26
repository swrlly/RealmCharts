import sqlite3
import functools
from contextlib import contextmanager

class DatabaseConnection:

    def __init__(self, link, logger):
        self.link = link
        self.logger = logger
    
    @contextmanager
    def connect(self):
        """`with` statement"""
        conn = sqlite3.connect(self.link)
        cursor = conn.cursor()
        try:
            yield conn, cursor
        finally:
            conn.close()
    
    def handle_db_exceptions(self, func):
        """Handles exceptions and logging"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                print("calling", func.__module__ + "." + func.__name__)
                return func(*args, **kwargs)
            except Exception as e:
                class_name = func.__module__
                calling_func_name = func.__name__
                self.logger.error(f"Error in {class_name}.{calling_func_name}: {e}")
        return wrapper
            
