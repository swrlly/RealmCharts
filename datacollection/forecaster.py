import gc
import pandas as pd
from statsmodels.tsa.statespace.structural import UnobservedComponents
from save_model import plot_and_save

class Forecaster:

    def __init__(self, logger):
        self.logger = logger
        self.df = None
        self.result = None
        self.params  = {
            "irregular" : True, 
            "freq_seasonal" : [{"period": 12 * 24, "harmonics": 4}, {"period": 12 * 24 * 7, "harmonics": 2}],
            "level" : "rtrend",
            "stochastic_level": True,
            "autoregressive": 4
        }
        self.forecast_length = 24 * 12

    def prepare_data(self, data, update_df = True):
        # ignore maintenance + buggy data.
        df = pd.DataFrame(data, columns = ["timestamp", "players", "online", "trustworthiness"])
        df.loc[df["trustworthiness"] < 0.2, "players"] = pd.NA
        df.loc[df["online"] == 0, "players"] = pd.NA
        if update_df: self.df = df
        else: return df

    def train_model(self):
        self.logger.info("Training forecasting model...")
        model = UnobservedComponents(endog = self.df["players"], initialization = "diffuse", **self.params)
        self.result = model.fit(method = "powell", optim_complex_step = True)
        plot_and_save(self.result, self.df)
        self.logger.info("Finished training model.")

    def get_forecast(self):
        # get 12 hour forecast
        forecast = self.result.get_forecast(self.forecast_length)
        return self.transform_forecast_data(forecast)
    
    def transform_forecast_data(self, forecast):
        # assumes you have the most updated data, including when adding 1 point
        start = self.df["timestamp"].max()
        forecast_data = pd.concat([pd.Series(data = [start + i * 300 for i in range(1, self.forecast_length + 1)], index = forecast.predicted_mean.index, dtype = pd.Int64Dtype(), name = "timestamp"),
                            forecast.predicted_mean,
                            forecast.conf_int(alpha = 0.5 - 0.341),
                            forecast.conf_int(alpha = 0.5 - 0.341 - 0.136),
                            forecast.conf_int(alpha = 0.5 - 0.341 - 0.136 - 0.021)], axis = 1).reset_index()
        return forecast_data.values.tolist()

    def find_new_data(self, new_data):
        # could just use max(timestamp) but making sure playersGrouped generation is in sync
        new_df = self.prepare_data(new_data, update_df = False)
        merged = pd.merge(new_df, self.df, how = "left", on = "timestamp", suffixes = ("", "_y"), indicator = True)
        new_row = merged[merged["_merge"] == "left_only"][["timestamp", "players", "online", "trustworthiness"]]
        del self.df
        gc.collect()
        self.df = new_df
        return new_row

    def update_forecast_once(self, new_df):
        # update forecast with one new unseen data point 5 minutes after our trained data
        new_row = self.find_new_data(new_df)
        new_result = self.result.append(new_row["players"])
        del self.result
        gc.collect()
        self.result = new_result
        return self.get_forecast()

    #def update_forecast_when_maintenance(self, new_df):
        #todo