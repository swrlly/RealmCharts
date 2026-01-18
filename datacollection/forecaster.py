import gc
import numpy as np
import pandas as pd
from patsy import dmatrix
from threading import Thread
from save_model import plot_and_save
from statsmodels.tsa.statespace.structural import UnobservedComponents

class Forecaster:

    def __init__(self, logger):
        self.logger = logger
        # all grouped data
        self.df = None
        # result object from model.fit()
        self.result = None
        # params for Unobserved Components
        self.params  = { # 4, 2 rtrend before wed 9/24
            "irregular" : True, 
            "freq_seasonal" : [{"period": 12 * 24, "harmonics": 8}, {"period": 12 * 24 * 7, "harmonics": 7}, {"period": 12 * 24 * 7, "harmonics": 1}],
            "level" : "strend",
            "stochastic_level": True,
            "autoregressive": 2
        }
        self.forecast_length = 24 * 12
        self.finished_training = False
        # column names of exogenous regressors
        self.exog_names = None
        self.maintenance_dates = [
            pd.Timestamp("2025-09-02 03:00:00", tz = "America/Los_Angeles"),  # MOTMG 2025
            pd.Timestamp("2025-09-30 03:00:00", tz = "America/Los_Angeles"),   # S24
            pd.Timestamp("2025-11-18 03:00:00", tz = "America/Los_Angeles"),   # S25
            pd.Timestamp("2025-01-13 02:00:00", tz = "America/Los_Angeles")   # S26
        ]

    def create_maintenance_spline(self, df, hours_effect=144):
        """
        spline basis exogenous regressors for seasonal start + MOTMG 2025 shock effect

        params:
        - maintenance_dates: list of maintenance start datetimes (I need to fill)
        - hours_effect: how long I believe the effect lasts (default 144 = 6 days = end of Sunday)
        """

        real_end = len(df)

        # create 24 hours of new rows for forecasting
        length, plot_length = 12 * 24 + 1, 14 * 12 * 24 + 1 
        exog_append = np.array([*[[pd.NA for _ in range(plot_length)] for _ in range(4)],
                                pd.date_range(start = df["time"][len(df)-1], periods = plot_length, freq = "5min"),
                                [pd.NA for _ in range(plot_length)]]).T
        exog_append = pd.DataFrame(data = exog_append,
                                index = [len(df) - 1 + i for i in range(plot_length)],
                                columns = ["timestamp", "players", "online", "trustworthiness", "time", "graph_x"])
        # drop first - was in real dataset
        exog_append.drop(index = exog_append.index[0], inplace = True)
        df = pd.concat([df, exog_append])
        
        # Initialize column to track hours since maintenance
        df["hours_since_maint"] = np.nan
        
        for maint_date in self.maintenance_dates:
            # Find all timestamps within the effect window
            mask = (df.time >= maint_date) & (df.time < maint_date + pd.Timedelta(hours=hours_effect))
            # Calculate hours since maintenance started
            df.loc[mask, "hours_since_maint"] = (df.time[mask] - maint_date).dt.total_seconds() / 3600

        # spline basis for Tue-Sun through maintenance:
        # 0 = Tue 3 AM - maint start
        # 12 = Tue 3 PM, direct effect of start of season
        # 48 = Thu 3 AM - midweek decrease
        # 96 = Sat 3 AM - start of weekend buildup
        # 120 = Sun 3 AM - middle of weekend effect
        # 144 = Mon 3 AM - end of maintenance shock

        # peaks at the aforementioned times
        knots = [12, 48, 96, 120]  
        valid_mask = df['hours_since_maint'].notna()
        hours_valid = df.loc[valid_mask, 'hours_since_maint'].values

        # natural cublc splines
        spline_basis = dmatrix(f"cr(hours_since_maint, knots={knots}) - 1", 
                            {"hours_since_maint": hours_valid},
                            return_type='dataframe')

        for col in spline_basis.columns:
            df[col] = 0.0
            df.loc[valid_mask, col] = spline_basis[col].values

        col_names = spline_basis.columns.to_list()
        # drop first and last spline, do not want start/end of week effects to interfere with other spline
        df.drop(axis = 1, labels = [col_names[0], col_names[-1]], inplace = True)
        col_names.pop(0), col_names.pop(len(col_names)-1)
        # set splines to be positive to only model increased player shock effect
        df[df[col_names] < 0] = 0
        # normalize spline to be able to compare coefficients
        df[col_names] /= df[col_names].max()
        # get future exog matrix
        self.future_exog = df.iloc[real_end:real_end+length-1][col_names]
        self.plot_exog = df.iloc[real_end:][col_names]
        # now restore df back to only seen data
        df = df.iloc[:real_end]

        self.exog_names = col_names
        return df

    def prepare_data(self, data, update_df = True):
        df = pd.DataFrame(data, columns = ["timestamp", "players", "online", "trustworthiness"])
        df["time"] = [i.tz_convert("America/Los_Angeles") for i in pd.to_datetime(df["timestamp"], unit = "s", utc = True)]
        df["graph_x"] = pd.Series(map(lambda x: x[:3], df.time.dt.day_name())) + " " + df.time.dt.hour.astype(str)
        # don't let model see maintenance / data outside of generating process (data < 60 min online)
        df.loc[df["trustworthiness"] < 0.2, "players"] = pd.NA
        df.loc[df["online"] == 0, "players"] = pd.NA
        # add spline exogenous regressors for now and forecast
        df = self.create_maintenance_spline(df)
        if update_df: self.df = df
        else: return df

    def create_exog_matrix(self, df):
        #self.logger.info(df.head(1))
        return df[self.exog_names].values

    def train_model(self):
        self.logger.info("Training forecasting model...")
        model = UnobservedComponents(endog = self.df["players"], exog = self.create_exog_matrix(self.df), initialization = "diffuse", **self.params)
        # later on, when training takes > 5 min, block all new forecasts until done 
        self.result = model.fit(method = "powell", cov_type = "oim", optim_hessian = "oim", optim_score = "harvey", optim_complex_step = True)
        self.logger.info("Finished training model.")
        thread = Thread(target = plot_and_save, args = (self.result, self.df, self.plot_exog))
        thread.start()

    def get_forecast(self):
        # get 12 hour forecast
        forecast = self.result.get_forecast(steps = self.forecast_length, exog = self.future_exog.values)
        return self.transform_forecast_data(forecast), self.get_model_spec()
    
    def transform_forecast_data(self, forecast):
        # assumes you have the most updated data, including after adding 1 point
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
        new_row = merged[merged["_merge"] == "left_only"]
        del self.df
        gc.collect()
        self.df = new_df
        return new_row

    def update_forecast_once(self, new_df):
        # update forecast with one new unseen data point 5 minutes after our trained data
        new_row = self.find_new_data(new_df)
        # Series on linux, number on NT 
        new_result = self.result.append(new_row["players"], exog = self.create_exog_matrix(new_row))
        del self.result
        gc.collect()
        self.result = new_result
        return self.get_forecast()

    def get_model_spec(self):
        """Saves model specs for forecasts"""
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
