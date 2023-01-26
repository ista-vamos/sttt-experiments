#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os, sys
from os.path import basename

infile = sys.argv[1]
data = pd.read_csv(infile, header=0, skiprows=1,
                   names=["benchmark",
                          "tsan-races", "tsan-usertime", "tsan-systime", "tsan-time", "tsan-mem",
                          "hel-races", "hel-usertime", "hel-systime", "hel-time", "hel-mem",
                          "vamos-races", "vamos-usertime", "vamos-systime", "vamos-time", "vamos-mem",
                          "vamos-mem-mon", "vamos-eventsnum", "vamos-drop", "vamos-holes"],
                   )


# first, replace time in timeouts with 0, then we will get the limits of other<br>
# times and set a new time for timeout values
data.loc[data["tsan-races"].astype(str).str.contains("TO"), "tsan-time"] = 0.0
data.loc[data["hel-races"].astype(str).str.contains("TO"), "hel-time"] = 0.0
data.loc[data["vamos-races"].astype(str).str.contains("TO"), "vamos-time"] = 0.0


data["tsan-time"] = data["tsan-time"].astype(float)
data["hel-time"] = data["hel-time"].astype(float)
data["vamos-time"] = data["vamos-time"].astype(float)

lim = max(max(data["tsan-time"]),
          max(data["hel-time"]),
          max(data["vamos-time"]))


timeout = 1.3*lim
lim = timeout*1.05
assert lim > 0
#print(f"lim: {lim}, timeout: {timeout}")


data.loc[data["tsan-races"].astype(str).str.contains("TO"), "tsan-time"] = timeout
data.loc[data["hel-races"].astype(str).str.contains("TO"), "hel-time"] = timeout
data.loc[data["vamos-races"].astype(str).str.contains("TO"), "vamos-time"] = timeout


plt.rcParams.update({'font.size': 18})
fig = plt.figure(figsize=(4,4))
fig.tight_layout()
s = plt.scatter(data["tsan-time"], data["vamos-time"], color="DarkRed", marker="x",  alpha=.5)
s = plt.scatter(data["hel-time"], data["vamos-time"], color="DarkGreen", marker="x", alpha=.5)
plt.plot([0, timeout], [timeout, timeout], color="gray", linestyle="dashed", linewidth=0.4)
plt.plot([timeout, timeout], [0, timeout], color="gray", linestyle="dashed", linewidth=0.4)
plt.xlim(0, lim)
plt.ylim(0, lim)
plt.xticks([x/10 for x in range(0, int(10*timeout), 5)])
plt.yticks([x/10 for x in range(0, int(10*timeout), 5)])
# plt.grid(ls='--')
leg = plt.legend(["vs TSan", "vs Helgrind", "TO"],
                 fontsize=14,
                 loc="center right",
                 bbox_to_anchor=(0.94, 0.5)
                )
if not os.environ.get("NOCAP"):
    plt.title("Comparing running wall-time of Vamos vs TSan and Helgrind")
plt.ylabel("VAMOS time [s]")
plt.xlabel("Tool 2 time [s]")
plt.gca().set_aspect('equal')
#plt.subplots_adjust(wspace=0.03, hspace=0)
plt.savefig("dataraces_times.pdf", bbox_inches='tight', dpi=300)

infofile = f"{os.path.abspath(os.path.dirname(sys.argv[0]))}/../../dataraces/benchmarks/info.txt"
info = pd.read_csv(infofile, delimiter=" ", header=0, skiprows=0,
                   dtype={"benchmark" : str, "has-race" : bool, "is-nondet" :bool})
INFO = {}
for idx, row in info.iterrows():
    INFO[row["benchmark"].strip()] = row

def get_races(tool):
    tmp = data.loc[~(data[f"{tool}-races"].astype(str).str.contains("TO")), ("benchmark", f"{tool}-races")]
    tmp[f"{tool}-races"] = tmp[f"{tool}-races"].astype(int)
    tmp = tmp.groupby("benchmark").agg(['min', 'max'])
    tmp.reset_index(inplace=True)
    tmp["is-racy"] = tmp["benchmark"].apply(lambda b: INFO[b.strip()]["has-race"])
    tmp["is-nondet"] = tmp["benchmark"].apply(lambda b: INFO[b.strip()]["is-nondet"])
    tmp = tmp.loc[~tmp["is-nondet"]]
    #print("Records: ", len(tmp))
    return tmp

def get_timeouts(tool):
    tmp = pd.DataFrame()
    tmp["benchmark"] = data["benchmark"]
     # are all answers for a benchmark TO?
    tmp["is-to"] = data[f"{tool}-races"].apply(lambda x: True if "TO" in str(x) else False)
    tmp["is-nondet"] = tmp["benchmark"].apply(lambda b: INFO[b.strip()]["is-nondet"])
    tmp = tmp.loc[~tmp["is-nondet"]]
    tmp = tmp.groupby("benchmark").all()
    tmp = tmp.loc[tmp[f"is-to"]]
    tmp.reset_index(inplace=True)

    return tmp

tmp = get_races("tsan")
tsan_race_corr = tmp.loc[(tmp[("is-racy")]) & (tmp[("tsan-races", "max")].astype(int) > 0)]
tsan_race_wrng = tmp.loc[(~tmp[("is-racy")]) & (tmp[("tsan-races", "max")].astype(int) > 0)]
tsan_norace_corr = tmp.loc[(~tmp[("is-racy")]) & (tmp[("tsan-races", "max")].astype(int) == 0)]
tsan_norace_wrng = tmp.loc[(tmp[("is-racy")]) & (tmp[("tsan-races", "max")].astype(int) == 0)]
tsan_to = get_timeouts("tsan")


tmp = get_races("hel")
hel_race_corr = tmp.loc[(tmp[("is-racy")]) & (tmp[("hel-races", "max")].astype(int) > 0)]
hel_race_wrng = tmp.loc[(~tmp[("is-racy")]) & (tmp[("hel-races", "max")].astype(int) > 0)]
hel_norace_corr = tmp.loc[(~tmp[("is-racy")]) & (tmp[("hel-races", "max")].astype(int) == 0)]
hel_norace_wrng = tmp.loc[(tmp[("is-racy")]) & (tmp[("hel-races", "max")].astype(int) == 0)]
hel_to = get_timeouts("hel")


tmp = get_races("vamos")
vamos_race_corr = tmp.loc[(tmp[("is-racy")]) & (tmp[("vamos-races", "max")].astype(int) > 0)]
vamos_race_wrng = tmp.loc[(~tmp[("is-racy")]) & (tmp[("vamos-races", "max")].astype(int) > 0)]
vamos_norace_corr = tmp.loc[(~tmp[("is-racy")]) & (tmp[("vamos-races", "max")].astype(int) == 0)]
vamos_norace_wrng = tmp.loc[(tmp[("is-racy")]) & (tmp[("vamos-races", "max")].astype(int) == 0)]
vamos_to = get_timeouts("vamos")

def get_times(tool):
    tmp = data.loc[~(data[f"{tool}-races"].astype(str).str.contains("TO")), ("benchmark", f"{tool}-time")]
    tmp = tmp.groupby("benchmark").agg("mean")
    return tmp[f"{tool}-time"].sort_values().reset_index()

def plot_times(ax, tool, color):
    times = get_times(tool)
    return ax.plot(times.index, times[f"{tool}-time"], color=color)


plt.clf()
figs_size=(12, 3)
font_scale = 1
sns.set(rc={'figure.figsize':figs_size},
        font_scale=font_scale)
plt.figure(figsize=figs_size)
sns.set_style("white")
fig, (ax1, ax2) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [0.25,  0.75]})
fig.tight_layout()
plt.yticks(fontsize=16)


######## SCATTERS ######
colors = sns.color_palette("deep").as_hex()
vamos_color=colors[2]
tsan_color=colors[1]
hel_color=colors[0]


plot_times(ax1, "tsan", color=tsan_color)
plot_times(ax1, "hel", color=hel_color)
plot_times(ax1, "vamos", color=vamos_color)
ax1.set_yscale("log")
#s = ax1.scatter(data["tsan-time"], data["vamos-time"], color="DarkRed", marker="x",  alpha=.5)
#s = ax1.scatter(data["hel-time"], data["vamos-time"], color="DarkGreen", marker="x", alpha=.5)
#ax1.plot([0, timeout], [timeout, timeout], color="gray", linestyle="dashed", linewidth=0.4)
#ax1.plot([timeout, timeout], [0, timeout], color="gray", linestyle="dashed", linewidth=0.4)
#ax1.set_xlim(0, lim)
#ax1.set_ylim(0, lim)
#ax1.set_xticks([x/10 for x in range(0, int(10*timeout), 5)],
#               [f"{x/10:.1f}" for x in range(0, int(10*timeout), 5)],
#               fontsize=16)
#ax1.set_yticks([x/10 for x in range(0, int(10*timeout), 5)],
#               [f"{x/10:.1f}" for x in range(0, int(10*timeout), 5)],
#               fontsize=16)
#ax1.grid(ls='--')
#leg = ax1.legend(["TSan", "Helgrind", "VAMOS"],
#                 fontsize=16,
                # loc="center right",
                 #bbox_to_anchor=(0.94, 0.5)
#                )
#if not os.environ.get("NOCAP"):
#    ax1.title("Comparing running wall-time of Vamos vs TSan and Helgrind")
ax1.set_ylabel("Time [s]", fontsize=18, labelpad=12)
ax1.set_xlabel("# of benchmarks", fontsize=18, labelpad=15)
ax1.tick_params(axis='x', labelsize=16)
ax1.tick_params(axis='y', labelsize=14)



######## BARS ##########

vamos = [vamos_race_corr, vamos_race_wrng, vamos_norace_corr, vamos_norace_wrng, vamos_to]
tsan  = [tsan_race_corr,  tsan_race_wrng,  tsan_norace_corr,  tsan_norace_wrng,  tsan_to]
hel   = [hel_race_corr,   hel_race_wrng,   hel_norace_corr,   hel_norace_wrng,   hel_to]

labels =[
    "race\ncorrect", "race\nwrong", "no race\ncorrect", "no race\nwrong", "timeout"
]


barwidth=1
tools_num = 3
bars_no = len(labels)

sns.set_style("whitegrid")

bar1 = ax2.bar([x*barwidth for x in range(0, tools_num*bars_no, tools_num)],
               [len(g) for g in vamos],
               color=vamos_color, label="VAMOS")
bar2 = ax2.bar([x*barwidth for x in range(1, tools_num*bars_no, tools_num)],
               [len(g) for g in tsan],
               color=tsan_color, label="TSan")
bar3 = ax2.bar([x*barwidth for x in range(2, tools_num*bars_no, tools_num)],
               [len(g) for g in hel],
               color=hel_color, label="Helgrind")

ax2.set_xticks([x*barwidth for x in range(1, tools_num*bars_no, tools_num)], labels, fontsize=18)

ax2.tick_params(axis='x', pad=20)
ypos = -4
for x in range(0, bars_no):
    ax2.text(x*tools_num*barwidth, ypos,
             f"{len(vamos[x]):3}",
             fontsize=14,
             horizontalalignment='center',
             verticalalignment='center')
    ax2.text(x*tools_num*barwidth + 1, ypos,
             f"{len(tsan[x]):3}",
             fontsize=14,
             horizontalalignment='center',
             verticalalignment='center')
    ax2.text(x*tools_num*barwidth + 2, ypos,
             f"{len(hel[x]):3}",
             fontsize=14,
             horizontalalignment='center',
             verticalalignment='center')
ax2.legend(fontsize=16)
ax2.grid(True, axis='y', color = "black", linewidth = "0.2", linestyle = "-")

plt.setp(ax1.spines.values(), linewidth=0.2)
plt.setp(ax2.spines.values(), linewidth=0.2)

plt.subplots_adjust(wspace=0.15, hspace=0)
plt.savefig("dataraces.pdf", bbox_inches='tight', dpi=600)


v = sum(map(len, vamos))
t = sum(map(len, tsan))
h = sum(map(len, hel))
assert t == h, (t, h)
assert v == t, (v, t)


# In[345]:


data2 = data[~(data["tsan-races"].astype(str).str.contains("TO") |
               data["hel-races"].astype(str).str.contains("TO") |
               data["vamos-races"].astype(str).str.contains("TO"))]
mem = pd.DataFrame()
mem["tsan-mem"] = data2["tsan-mem"].astype(float)/1024.0
mem["hel-mem"] = data2["hel-mem"].astype(float)/1024.0
mem["vamos-mem"] = data2["vamos-mem"].astype(float)/1024.0
plt.clf()
fig = plt.figure(figsize=(4,4))
fig.tight_layout()
s = plt.scatter(mem["tsan-mem"], mem["vamos-mem"], color="DarkRed", marker="x",  alpha=.5)
s = plt.scatter(mem["hel-mem"], mem["vamos-mem"], color="DarkGreen", marker="x", alpha=.5)
lim = max(max(mem["tsan-mem"]), max(mem["hel-mem"]), max(mem["vamos-mem"]))
plt.xlim(0, lim)
plt.ylim(0,lim)
plt.legend(["vs TSan", "vs Helgrind"])
# gca = plt.gca()
# gca.set_aspect('equal')
plt.ylabel("VAMOS memory [MB]")
plt.xlabel("Tool 2 memory [MB]")
if not os.environ.get("NOCAP"):
    plt.title("Comparing memory consumption of Vamos vs TSan and Helgrind")
plt.savefig("dataraces_memory.pdf", bbox_inches='tight', dpi=300)


# how many answers diverged?
# get rows where all tools answered
fil = data.loc[~(data["tsan-races"].astype(str).str.contains("TO") |
               data["hel-races"].astype(str).str.contains("TO") |
               data["vamos-races"].astype(str).str.contains("TO"))]
tmp = pd.DataFrame()
tmp["benchmark"] = fil["benchmark"]
for tool in ("tsan", "hel", "vamos"):
    tmp[f"{tool}-found"] = fil[f"{tool}-races"].apply(lambda x: False if "TO" in str(x) else int(x) > 0)

# have the tool found a race in _all_ trials?
tmp = tmp.groupby("benchmark").all()
all_agree = tmp.loc[(tmp["tsan-found"] == tmp["hel-found"]) &
                    (tmp["tsan-found"] == tmp["vamos-found"])]
print("-"*50)
print(f"\033[32;mWhen all tools finished, they agreed on {len(all_agree)} from {len(tmp)} benchmarks, i.e. {100*(float(len(all_agree))/len(tmp)) :.2f}% of cases\033[0;m")

# get rows where all tools answered
fil = data.loc[~(data["tsan-races"].astype(str).str.contains("TO") |
               data["hel-races"].astype(str).str.contains("TO"))]
tmp = pd.DataFrame()
tmp["benchmark"] = fil["benchmark"]
for tool in ("tsan", "hel"):
    tmp[f"{tool}-found"] = fil[f"{tool}-races"].apply(lambda x: False if "TO" in str(x) else int(x) > 0)

# have the tool found a race in _all_ trials?
tmp = tmp.groupby("benchmark").all()
agree = tmp.loc[(tmp["tsan-found"] == tmp["hel-found"])]
print(f"\033[32;mWhen TSan and Helgrind finished, they agreed on {len(agree)} from {len(tmp)} benchmarks, i.e.  {100*(float(len(all_agree))/len(tmp)) :.2f}% of cases\033[0;m")


fil = data.loc[~(data["tsan-races"].astype(str).str.contains("TO") |
               data["vamos-races"].astype(str).str.contains("TO"))]
tmp = pd.DataFrame()
tmp["benchmark"] = fil["benchmark"]
for tool in ("tsan", "vamos"):
    tmp[f"{tool}-found"] = fil[f"{tool}-races"].apply(lambda x: False if "TO" in str(x) else int(x) > 0)

# have the tool found a race in _all_ trials?
tmp = tmp.groupby("benchmark").all()
agree = tmp.loc[(tmp["tsan-found"] == tmp["vamos-found"])]
print(f"\033[32;mWhen TSan and VAMOS finished, they agreed on {len(agree)} from {len(tmp)} benchmarks, i.e. {100*(float(len(all_agree))/len(tmp)) :.2f}% of cases\033[0;m")


# In[493]:


fil = data.loc[~(data["hel-races"].astype(str).str.contains("TO") |
               data["vamos-races"].astype(str).str.contains("TO"))]
tmp = pd.DataFrame()
tmp["benchmark"] = fil["benchmark"]
for tool in ("hel", "vamos"):
    tmp[f"{tool}-found"] = fil[f"{tool}-races"].apply(lambda x: False if "TO" in str(x) else int(x) > 0)

# have the tool found a race in _all_ trials?
tmp = tmp.groupby("benchmark").all()
agree = tmp.loc[(tmp["hel-found"] == tmp["vamos-found"])]
print(f"\033[32;mWhen Helgrind and VAMOS finished, they agreed on {len(agree)} from {len(tmp)} benchmarks, i.e. {100*(float(len(all_agree))/len(tmp)) :.2f}% of cases\033[0;m")
print("-"*50)
