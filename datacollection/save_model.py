import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
import datetime
import time
import os

matplotlib.use('agg')
lavender = "#BE90F7"
lightBlue = "#9cdcfe"
textColor = "#D3D3D3"
bgColor = "#090909"
borderColor = "#212121"
graphColor = "#121212"

plt.rcParams["axes.facecolor"] = graphColor
plt.rcParams["axes.titlecolor"] = textColor
plt.rcParams["figure.facecolor"] = bgColor
plt.rcParams["xtick.color"] = textColor
plt.rcParams["xtick.labelcolor"] = textColor
plt.rcParams["axes.labelcolor"] = textColor
plt.rcParams["text.color"] = textColor
plt.rcParams["ytick.color"] = textColor
plt.rcParams["ytick.labelcolor"] = textColor
plt.rcParams["legend.labelcolor"] = textColor
plt.rcParams["legend.facecolor"] = graphColor
plt.rcParams["legend.edgecolor"] = borderColor
#plt.rcParams["figure.dpi"] = 400
plt.rcParams["axes.labelpad"] = 20
plt.rcParams["axes.titlepad"] = 20

def plot_and_save(res, df):
    now = time.gmtime(time.time())
    name = str(datetime.datetime(*now[:4]))[:-6]
    dir = f"data/models/{name}"
    done, ctr = False, 1
    while not done:
        try: 
            os.makedirs(dir + f" {ctr}")
            done = True
        except: 
            ctr += 1
    dir += f" {ctr}"
    fig, axs = plt.subplots(2, 3, figsize = (20, 8))
    axs[0, 0].plot(res.level["smoothed"], color = lavender, linewidth = 0.5)
    axs[0, 0].set_title("level")
    axs[0, 1].plot(res.trend["smoothed"], color = lavender, linewidth = 0.5)
    axs[0, 1].set_title("trend")
    axs[0, 2].plot(res.autoregressive["smoothed"], color = lavender, linewidth = 0.5)
    axs[0, 2].set_title("AR")
    axs[1, 0].plot(res.freq_seasonal[0]["smoothed"], color = lavender, linewidth = 0.5)
    axs[1, 0].set_title("Daily seasonality")
    axs[1, 1].plot(res.freq_seasonal[1]["smoothed"], color = lavender, linewidth = 0.5)
    axs[1, 1].set_title("Weekly seasonality")
    start = df["timestamp"].max() + 300
    idx = [
        pd.to_datetime(i, unit = "s", utc = True).tz_convert("US/Pacific").day_name()[:3] + f" {pd.to_datetime(i, unit = "s", utc = True).tz_convert("US/Pacific").hour}" 
        for i in range(start, start + 300 * 14 * 12 * 24, 300 * 12 * 24)
    ]
    fore = res.get_forecast(14 * 12 * 24)
    axs[1, 2].plot(fore.predicted_mean, color = lavender, linewidth = 0.5)
    axs[1, 2].set_xticks(fore.predicted_mean.index[::12*24], idx, fontsize = "small")
    axs[1, 2].tick_params(axis = "x", labelrotation = 45)
    axs[1, 2].set_title("2 week prediction")
    fig.subplots_adjust(hspace=0.3)
    plt.savefig(dir + "/decomposition.png", dpi = 200)
    # 200 mb+, don't save..
    # res.save(dir + "/model.pkl") 
    with open(dir + "/summary.txt", "w") as f:
        f.write(str(res.summary()))