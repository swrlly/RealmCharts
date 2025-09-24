import matplotlib.pyplot as plt
import datetime
import time
import os

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
plt.rcParams["figure.dpi"] = 300
plt.rcParams["axes.labelpad"] = 20
plt.rcParams["axes.titlepad"] = 20

def plot_and_save(res):
    now = time.gmtime(time.time())
    name = str(datetime.datetime(*now[:4]))[:-6]
    dir = f"data/models/{name}"
    os.makedirs(dir)
    fig, axs = plt.subplots(2, 3, figsize = (20, 8))
    axs[0, 0].plot(res.level["smoothed"])
    axs[0, 0].set_title("level")
    axs[0, 1].plot(res.trend["smoothed"])
    axs[0, 1].set_title("trend")
    axs[0, 2].plot(res.autoregressive["smoothed"])
    axs[0, 2].set_title("AR")
    axs[1, 0].plot(res.freq_seasonal[0]["smoothed"])
    axs[1, 0].set_title("Daily seasonality")
    axs[1, 1].plot(res.freq_seasonal[1]["smoothed"])
    axs[1, 1].set_title("Weekly seasonality")
    fig.subplots_adjust(hspace=0.3)
    plt.savefig(dir + "/decomposition.png", dpi = 300)
    # 200 mb+, don't save..
    # res.save(dir + "/model.pkl") 
    with open(dir + "/summary.txt", "w") as f:
        f.write(str(res.summary()))