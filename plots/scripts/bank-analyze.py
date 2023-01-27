#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os, sys
from os.path import basename

def get_params(path):
    parts = basename(path).split('-')
    assert len(parts) in (4,6), path
    assert parts[0] == "bank"
    assert parts[-1].endswith('.csv')
    if len(parts) == 4:
    # SHM buf size, arbiter buf size, num
        return int(parts[1]), int(parts[2]), int(parts[-1][:-4])
    return int(parts[1]), int(parts[2]), int(parts[3])

def read_data(csvfiles):
    data = {}
    for cf in csvfiles:
        shmbufsize, arbbufsize, num = get_params(cf)
        stats = pd.read_csv(cf, names=['err_freq', 'err_gen', 'err_found', 'time', 'holes_in',
                                       'holes_out', "drop_in", "drop_out"])
        df = data.setdefault(num, {}).setdefault(shmbufsize, {}).setdefault(arbbufsize, pd.DataFrame())
        data[num][shmbufsize][arbbufsize] = pd.concat([df, stats], ignore_index=True)
    return data

def read_data_tessla(csvfiles):
    data = {}
    for cf in csvfiles:
        shmbufsize, arbbufsize, num = get_params(cf)
        stats = pd.read_csv(cf, names=['err_freq', 'err_gen', 'err_found', 'time', 'holes_in',
                                       'holes_out', 'mon_utime', 'mon_systime', 'mon_walltime'])
        df = data.setdefault(num, {}).setdefault(shmbufsize, {}).setdefault(arbbufsize, pd.DataFrame())
        data[num][shmbufsize][arbbufsize] = pd.concat([df, stats], ignore_index=True)
    return data

def set_labels(obj, xlabel, ylabel):
    obj.set_xlabel(xlabel, labelpad=50)
    obj.set_ylabel(ylabel, labelpad=50)
    obj.tick_params(axis='x',pad=50)
    obj.tick_params(axis='y',pad=50)


data = read_data((f"{sys.argv[1]}/{f}" for f in os.listdir(os.curdir + f"/{sys.argv[1]}") if f.endswith(".csv")))
dataT = read_data_tessla((f"{sys.argv[2]}/{f}" for f in os.listdir(os.curdir + f"/{sys.argv[2]}") if f.endswith(".csv")))

for NUM in data.keys():
    data0 = data[NUM]
    print("-"*50)
    for shmsize, tmp in data0.items():
        for arbsize, D in tmp.items():
            print(f"NUM: {NUM}, SHM size: {shmsize}, arbiter size: {arbsize}")
            print(f"  avg holes-in %: {(100*D['holes_in']/NUM).mean()}, avg holes-out %: {(100*D['holes_out']/NUM).mean()}")
            print(f"  avg dropped-in %: {(100*D['drop_in']/NUM).mean()}, avg dropped-out %: {(100*D['drop_out']/NUM).mean()}")
    print("-"*50)
    S = {}
    for arbsize, tmp in data0[1].items():
        tmp = tmp.loc[tmp.err_freq != 0]
        S[int(arbsize)] = (100*(tmp.err_found - tmp.err_gen)/tmp.err_gen)
    sorted_arbsizes = sorted(list(S.keys()))
    df = pd.DataFrame(S, columns=sorted_arbsizes)

    dataT0 = dataT.get(NUM)
    if dataT0 is None:
        print(f"!!! Results for TeSSLa are missing !!!")
        continue

    ST = {}
    for arbsize, tmp in dataT0[1].items():
        tmp = tmp.loc[tmp.err_freq != 0]
        ST[int(arbsize)] = (100*(tmp.err_found - tmp.err_gen)/tmp.err_gen)
    sorted_arbsizes2 = sorted(list(S.keys()))
    assert sorted_arbsizes == sorted_arbsizes2, (sorted_arbsizes, sorted_arbsizes2)
    dfT = pd.DataFrame(ST, columns=sorted_arbsizes)

    figs_size = (20,6)
    font_scale = 2
    sns.set(rc={'figure.figsize':figs_size}, font_scale=font_scale)
    sns.set_style("whitegrid")

    fig, ax =plt.subplots(1, 2, sharey=True,
                          gridspec_kw={'width_ratios': [1, 1]})

    vam = sns.boxplot(data=df, ax=ax[0],
                         whiskerprops=dict(linewidth=3),
                        flierprops=dict(marker='o', markersize=2),
                        capprops=dict(linewidth=3),
                         medianprops=dict(linewidth=3))
    tes = sns.boxplot(data=dfT, ax=ax[1],
                         whiskerprops=dict(linewidth=3),
                        flierprops=dict(marker='o', markersize=2),
                        capprops=dict(linewidth=3),
                         medianprops=dict(linewidth=3))
    vam.set_xlabel('Arbiter buffer size', labelpad=15)
    vam.set_ylabel('Δ in detected errors [%]', labelpad=15)
    tes.set_xlabel('Arbiter buffer size', labelpad=15)
    tes.set_ylabel("")

    plt.subplots_adjust(wspace=0.03, hspace=0)
    plt.savefig(f"bank_plot_{NUM}.pdf", bbox_inches='tight', dpi=300)

