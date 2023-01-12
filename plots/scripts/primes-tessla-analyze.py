#!/usr/bin/env python
# coding: utf-8

# In[58]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from os.path import basename
import sys

csvfile = sys.argv[1]

datait = pd.read_csv(csvfile)
datait["checked_perc"] = 100*datait.checked/datait.primes_num
datait["founderr_perc"] = (datait.errnum/datait.errgen)*100
datait
df=datait.loc[datait.errgen > 0]

if (len(df) == 0):
    exit(1)

def set_labels(obj, xlabel, ylabel):
    obj.set_xlabel(xlabel, labelpad=50)
    obj.set_ylabel(ylabel, labelpad=50)
    obj.tick_params(axis='x',pad=50)
    obj.tick_params(axis='y',pad=50)

f, ax = plt.subplots(figsize=(4, 2))
plot = sns.lineplot(data=datait,
                    x="arbiter_bufsize", y="checked_perc",
                    hue="type",
                    ax=ax, palette="deep", markers=True)

plot.legend(loc='center right',title="Arbiter type")
ax.set(xlabel='Arbiter buffer size', ylabel='Checked events (%)')
fig = plot.get_figure()
fig.savefig("primes_tessla_checked.pdf", bbox_inches='tight', dpi=300)

f, ax = plt.subplots(figsize=(4, 2))
plot = sns.lineplot(data=df,
                    x="arbiter_bufsize", y="founderr_perc",
                    hue="type",
                    ax=ax, palette="deep", markers=True)

plot.legend(loc='center right',title="Arbiter type")
ax.set(xlabel='Arbiter buffer size', ylabel='Found errors (%)')
fig = plot.get_figure()
fig.savefig("primes_tessla_errs.pdf", bbox_inches='tight', dpi=300)

