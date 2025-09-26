from .interface import ETLJob

# modifies forecast, forecastHorizon, maintenanceForecast

class Forecast(ETLJob):

    def __init__(self, db_connection, logger):
        super().__init__(db_connection, logger)
        self.insert_into_forecast = self.log_exceptions(self.insert_into_forecast)
        self.insert_into_forecast_horizon = self.log_exceptions(self.insert_into_forecast_horizon)
        self.update_forecast_horizon_with_actuals = self.log_exceptions(self.update_forecast_horizon_with_actuals)
        self.generate_forecast_during_maintenance = self.log_exceptions(self.generate_forecast_during_maintenance)

    def insert_into_forecast(self, data, params) -> None:
        """
        Updates `forecast` with new forecast.
        Only insert future time points
        """

        with self.db_connection.connect() as (conn, cursor):
            cursor.executemany("INSERT OR REPLACE INTO forecast VALUES (?,?,?,?,?,?,?,?,?,?);", [i + [params] for i in data])
            conn.commit()

    def insert_into_forecast_horizon(self, data, params):
        """Updates forecastHorizon with forecasts"""

        with self.db_connection.connect() as (conn, cursor):
            one_hour = data[12 - 1]
            six_hour = data[6*12 - 1]
            twelve_hour = data[12*12 - 1]
            twenty_four_hour = data[24*12 - 1]
            cursor.execute("INSERT OR IGNORE INTO forecastHorizon VALUES (?,?,?,?,?);", [one_hour[1], 12, one_hour[2], None, params])
            cursor.execute("INSERT OR IGNORE INTO forecastHorizon VALUES (?,?,?,?,?);", [six_hour[1], 6*12, six_hour[2], None, params])
            cursor.execute("INSERT OR IGNORE INTO forecastHorizon VALUES (?,?,?,?,?);", [twelve_hour[1], 12*12, twelve_hour[2], None, params])
            cursor.execute("INSERT OR IGNORE INTO forecastHorizon VALUES (?,?,?,?,?);", [twenty_four_hour[1], 24*12, twenty_four_hour[2], None, params])
            conn.commit()

    def update_forecast_horizon_with_actuals(self):
        """Updates `forecastHorizon` with actual collected data"""

        with self.db_connection.connect() as (conn, cursor):
            cursor.execute("""SELECT forecastHorizon.timestamp,
            playersGrouped.players
            FROM forecastHorizon
            LEFT JOIN playersGrouped
            ON forecastHorizon.timestamp = playersGrouped.timestamp
            WHERE playersGrouped.online = 1 AND playersGrouped.trustworthiness >= 0.2;""")
            results = cursor.fetchall()
            results = [{"timestamp": i[0], "actual_value": i[1]} for i in results]
            # only add once (primary key will catch it)
            cursor.executemany("UPDATE OR IGNORE forecastHorizon SET actual_value = :actual_value WHERE timestamp = :timestamp;", results)
            conn.commit()

    def generate_forecast_during_maintenance(self, data):
        """Updates `maintenanceForecast` with 0's until DECA's est. end time"""

        now, online, est_time = data[0], data[1], data[2]
        now -= now % 300
        new_rows = []
        for add in range(300, est_time - now, 300):
            new_rows.append([0, now + add, 0, 0, 0, 0, 0, 0, 0])

        with self.db_connection.connect() as (conn, cursor):
            cursor.executemany("INSERT OR REPLACE INTO maintenanceForecast VALUES (?,?,?,?,?,?,?,?,?);", new_rows)
            conn.commit()