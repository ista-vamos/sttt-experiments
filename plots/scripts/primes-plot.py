#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from os.path import isfile
import sys

figs_size = (30, 14)
font_scale = 3.7

# "./times.csv" -> argv[1]
# "./errors_stats.csv" -> argv[2]
if not isfile(sys.argv[1]):
    print("Couldn't find file ", sys.argv[1])
    exit(1)

if not isfile(sys.argv[2]):
    print("Couldn't find file ", sys.argv[2])
    exit(1)

times = pd.read_csv(sys.argv[1])
stats = pd.read_csv(sys.argv[2])

try:
    tmp = times.groupby(by=["env", "buff_size", "primes"]).mean().loc["DRIO-Opt"]
except KeyError:
    print("Found no results...")
    exit(1)
times["drio_runtime"] = None

for buff_size in [128, 512, 1024, 2048]:
    for n_primes in range(10000, 40000 + 1, 10000):
        try:
            runtime = float(tmp.loc[buff_size].loc[n_primes])
            times.loc[
                (times.buff_size == buff_size) & (times.primes == n_primes), "drio_runtime"
            ] = runtime
        except KeyError:
            pass # missing result


times["diff_drio"] = 100 * ((times["time"] / times["drio_runtime"]) - 1)
times = times[times.env != "DRIO-Opt"]


def set_labels(obj, xlabel, ylabel):
    obj.set_xlabel(xlabel, labelpad=50)
    obj.set_ylabel(ylabel, labelpad=50)
    obj.tick_params(axis="x", pad=50)
    obj.tick_params(axis="y", pad=50)


figs_size = (18, 6)
sns.set(rc={"figure.figsize": figs_size}, font_scale=2)
sns.set_style("whitegrid")
fig, ax = plt.subplots(1, 4, gridspec_kw={"width_ratios": [0.6, 1, 0.1, 1]})
native_plot = sns.barplot(
    data=times[times.env == "Native"],
    ax=ax[0],
    y="diff_drio",
    x="primes",
    color="#5e35b1",
)
native_plot.set(title="Native")
native_plot.set_xlabel("Primes generated", labelpad=15)
native_plot.set_ylabel("Overhead [%]", labelpad=15)
xlabnum = len(native_plot.get_xticklabels())
native_plot.set_xticklabels([f"{val}k" for val in (10, 20, 30, 40) if val <= 10*xlabnum])

monitored_plot = sns.barplot(
    data=times[times.env == "DRIO-Monitored"],
    x="primes",
    ax=ax[1],
    y="diff_drio",
    hue="buff_size",
)
#monitored_plot.set_xticklabels([f"{val}k" for val in [10, 20, 30, 40]])
xlabnum = len(monitored_plot.get_xticklabels())
monitored_plot.set_xticklabels([f"{val}k" for val in (10, 20, 30, 40) if val <= 10*xlabnum])

monitored_plot.set(ylabel="", yticklabels=[], title="Monitor")
monitored_plot.set_xlabel("Primes generated", labelpad=15)
monitored_plot.legend(title="Arbiter buff. size")  # , bbox_to_anchor=(1, 1))

bplot = sns.boxplot(
    data=stats,
    y="errors_percentage",
    x="num_primes",
    hue="buff_size",
    ax=ax[3],
    whiskerprops=dict(linewidth=3),
    flierprops=dict(marker="o", markersize=2),  #    markerfacecolor='red'),
    capprops=dict(linewidth=3),
    medianprops=dict(linewidth=3, marker="|"),
)
xlabnum = len(bplot.get_xticklabels())
bplot.set_xticklabels([f"{val}k" for val in (10, 20, 30, 40) if val <= 10*xlabnum])
#bplot.set_xticklabels([f"{val}k" for val in [10, 20, 30, 40]])
bplot.set_xlabel("Primes generated", labelpad=15)
bplot.set_ylabel("Found errors [%]")
bplot.legend([], [], frameon=False)
bplot.yaxis.tick_right()
bplot.yaxis.set_label_position("right")
bplot.tick_params(axis="y", length=0, pad=10)

ax[2].axis("off")
plt.subplots_adjust(wspace=0.03, hspace=0)
plt.savefig("primes_plot.pdf", bbox_inches="tight", dpi=300)
