#!/usr/bin/python3

import sys
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from statistics import mean
import pandas as pd
import seaborn as sns
from os.path import basename

# source_wait_cyc, arbiter_buffer_size, source_waited,
# processed, dropped, dropped_times, delay

def get_params(path):
    parts = basename(path).split('-')
    assert len(parts) == 4
    assert parts[0] == 'numbers'
    assert parts[3].endswith('.csv')
    return int(parts[1]), int(parts[2]), int(parts[3][:-4])

try:
    BS, NUM, SRCNUM = get_params(sys.argv[1])
    print(f"SHM buffer size: {BS}, NUM of events: {NUM}, SOURCES NUM: {SRCNUM}")
except ValueError:
    print("Invalid/no file, giving up...")
    exit(0)

datait = pd.read_csv(sys.argv[1])
if SRCNUM == 1:
    datait.columns = ["source_wait_cyc","arbiter_buffer_size",
                      "source_waited","processed","dropped",
                      "dropped_times","delay"]
else:
    datait.columns = ["source_wait_cyc","arbiter_buffer_size",
                      "source_waited1","source_waited2",
                      "processed","dropped","dropped_times","delay"]

datait["processed_percentage"] = 100*datait.processed/NUM

############################################################3
f, ax = plt.subplots(figsize=(8, 3))
ax.set(xscale="symlog")

plot = sns.lineplot(data=datait, x="arbiter_buffer_size", y="processed_percentage",
                    hue="source_wait_cyc", style="source_wait_cyc",
                    ax=ax, palette="deep",markers=True, dashes=False)#, ci="sd")
plot.legend(loc='lower right', ncol=2, title="Waiting [cyc.]")
for line in plot.lines:
    line.set_linestyle("--")
ax.set(xlabel='Arbiter buffer size', ylabel='Processed events (%)',
       #title="% of Processed Events vs Buffer Size w/ Diff. Waiting Cycles"
       )
fig = plot.get_figure()
fig.savefig(f"scalability_plot_{BS}_{NUM}_{SRCNUM}_processed.pdf", bbox_inches='tight', dpi=300)

