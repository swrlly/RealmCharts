import gc
import pandas as pd
from threading import Thread
from statsmodels.tsa.statespace.structural import UnobservedComponents
from save_model import plot_and_save

class Forecaster:

    def __init__(self, logger):
        self.logger = logger
        self.df = None
        self.result = None
        self.params  = { # 4, 2 rtrend before wed 9/24
            "irregular" : True, 
            "freq_seasonal" : [{"period": 12 * 24, "harmonics": 8}, {"period": 12 * 24 * 7, "harmonics": 7}, {"period": 12 * 24 * 7, "harmonics": 1}],
            "level" : "strend",
            "stochastic_level": True,
            "autoregressive": 2
        }
        self.forecast_length = 24 * 12

    def prepare_data(self, data, update_df = True):
        # ignore maintenance + buggy data.
        df = pd.DataFrame(data, columns = ["timestamp", "players", "online", "trustworthiness"])
        df["time"] = pd.to_datetime(df["timestamp"], unit = "s", utc = True)#[i.tz_convert("America/Los_Angeles") for i in pd.to_datetime(df["timestamp"], unit = "s", utc = True)]
        df["graph_x"] = pd.Series(map(lambda x: x[:3], df.time.dt.day_name())) + " " + df.time.dt.hour.astype(str)
        df.loc[df["trustworthiness"] < 0.2, "players"] = pd.NA
        df.loc[df["online"] == 0, "players"] = pd.NA
        if update_df: self.df = df
        else: return df

    def train_model(self):
        self.logger.info("Training forecasting model...")
        model = UnobservedComponents(endog = self.df["players"], initialization = "diffuse", **self.params)
        self.result = model.fit(method = "powell", cov_type = "oim", optim_hessian = "oim", optim_score = "harvey", optim_complex_step = True)
        self.logger.info("Finished training model.")
        thread = Thread(target = plot_and_save, args = (self.result, self.df))
        thread.start()

    def get_forecast(self):
        # get 12 hour forecast
        forecast = self.result.get_forecast(self.forecast_length)
        return self.transform_forecast_data(forecast), self.get_model_spec()
    
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

    def get_model_spec(self):
        s = ""
        grouped = {}
        for p in self.params:
            if p == "level":
                s += f"{self.params[p]} "
            elif p == "autoregressive":
                s += f"ar{self.params[p]} "
            elif p == "freq_seasonal":
                for i in self.params[p]:
                    if i["period"] not in grouped:
                        grouped.update({i["period"] : [i["harmonics"]]})
                    else:
                        grouped[i["period"]].append(i["harmonics"])
                d = ""
                for i in grouped:
                    d += f"{str(i)}:{','.join(str(j) for j in grouped[i])} "
                s += d
        return s.strip()
