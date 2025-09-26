from statsmodels.tsa.stattools import acf, pacf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib
import datetime
import time
import os

matplotlib.use('agg')
lavender = "#6d56ffff"
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

def plot_significant_acorr(res, ax, is_acf = True):
    # looking at residuals (one step forecast)
    resid, conf_int = None, None
    if is_acf: resid, conf_int = acf(res.standardized_forecasts_error[0], nlags = 300, alpha = 0.005, missing = "conservative")
    else: resid, conf_int = pacf(res.standardized_forecasts_error[0], nlags = 300, alpha = 0.005)
    resid, conf_int = pd.Series(resid[1:]), conf_int[1:]
    significant = pd.Series(map(lambda x: np.all(x < 0) | np.all(x > 0), conf_int))
    #colors = cmap(np.linspace(0, 1, 100)) 
    ax.vlines(resid.index[significant == True], 
              ymin = [0 for _ in range(significant.sum())], 
              ymax = resid[significant == True], color = lavender);
    ax.set_title("Significant ACF, α = 0.005") if is_acf else ax.set_title("Significant PACF, α = 0.005")
    matplotlib.rcParams.update({'font.size': 3.5})
    #minimum, maximum = resid.index[significant == True].min(), resid.index[significant == True].max()
    for i in significant[significant == True].index:
        width = ax.get_ylim()[1] - ax.get_ylim()[0]
        one_unit = width / 100
        if resid[i] < 0: ax.text(x = i - len(str(i)) * 1.6, y = resid[i] - 2.75 * one_unit, s = f"{round(i / 12, 1)}h")
        else: ax.text(x = i - len(str(i)) * 1.4, y = resid[i] + 2 * one_unit, s = f"{round(i / 12, 1)}h")
        ax.set_ylim(
            bottom = ((1 / abs(ax.get_ylim()[0] / width)) ** (1/8)) * min(resid), 
            top = ((1 / abs(ax.get_ylim()[0] / width)) ** (1/8)) * max(resid))
    ax.axhline(y = 0, xmin = 0, xmax = 1, color = borderColor)
    matplotlib.rcParams.update({'font.size': 10})

def plot_and_save(res, df):
    now = time.gmtime(time.time())
    name = str(datetime.datetime(*now[:4]))[:-6]
    dir = f"data/models/{name}"
    done, ctr = False, 0
    while not done:
        try: 
            if ctr == 0: os.makedirs(dir)
            else: os.makedirs(dir + f" {ctr}")
            done = True
        except: 
            ctr += 1
    dir += f" {ctr}" if ctr > 0 else ""
    fig, axs = plt.subplots(3, 3, figsize = (20, 15))
    axs[0, 0].plot(res.level["smoothed"], color = lavender)
    axs[0, 0].set_title("level")
    axs[0, 1].plot(res.trend["smoothed"], color = lavender)
    axs[0, 1].set_title("trend")
    axs[0, 2].plot(res.autoregressive["smoothed"], color = lavender, alpha = 0.85, linewidth = 0.5)
    axs[0, 2].set_title("AR")
    axs[1, 0].plot(res.freq_seasonal[0]["smoothed"][-7 * 12 * 24:], color = lavender)
    axs[1, 0].set_title("Daily seasonality")
    axs[1, 1].plot(res.freq_seasonal[1]["smoothed"], color = lavender)
    axs[1, 1].set_title("Weekly seasonality")
    #axs[1, 2].hist(res.resid[(res.resid > -100) & (res.resid < 100)], color = lavender, bins = 200, width = 0.5, alpha = 0.6)
    axs[1, 2].hist(res.standardized_forecasts_error[0], color = lavender, bins = 150, width = 0.1, alpha = 0.6)
    axs[1, 2].set_title("Standardized forecasts error")

    plot_significant_acorr(res, axs[2, 0], is_acf = True)
    plot_significant_acorr(res, axs[2, 1], is_acf = False)

    start = df["timestamp"].max() + 300
    idx = [
        pd.to_datetime(i, unit = "s", utc = True).tz_convert("US/Pacific").day_name()[:3] + f" {pd.to_datetime(i, unit = 's', utc = True).tz_convert('US/Pacific').hour}" 
        for i in range(start, start + 300 * 14 * 12 * 24, 300 * 12 * 24)
    ]
    fore = res.get_forecast(14 * 12 * 24)
    axs[2, 2].plot(fore.predicted_mean, color = lavender)
    axs[2, 2].set_xticks(fore.predicted_mean.index[::12*24], idx, fontsize = "small")
    axs[2, 2].tick_params(axis = "x", labelrotation = 45)
    axs[2, 2].set_title("Forecast")
    fig.subplots_adjust(hspace = 0.3)
    plt.savefig(dir + "/decomposition.png", dpi = 200)
    # 200 mb+, don't save..
    # res.save(dir + "/model.pkl") 
    with open(dir + "/summary.txt", "w") as f:
        f.write(str(res.summary()))
        transition_matrix = res.model.ssm['transition'] 
        f.write(f"""\nCondition number: {np.linalg.cond(transition_matrix)}\nDeterminant: {np.linalg.det(transition_matrix)}\nEigenvalues: {np.abs(np.linalg.eigvals(transition_matrix))})""")
