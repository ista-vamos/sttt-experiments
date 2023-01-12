# Plots

This directory contains scripts that generate plots. Plots can be generated
either from the data that we measured (see later) or from data reproduced by
experiments in this artifact.

After the generation, plots should be automatically opened. If this step for
some reason fails, the plots still can be opened manually in a PDF viewer. They
are generated into this directory.


## Generating plots from our data

The directory `original-data` contains .csv files with data that we measured.
By typing `make original`, plots are generated from this data. The resulting
files are named `paper_figure_N.pdf` where `N` is the number of the figure from
the paper. Plots should be automatically opened after their generation.

The makefile contains also targets to generate single figures, e.g., to generate
the figure for "scalability" experiments, type `make scalability-original` or
`make figure-3-original`.

Data races detection experiments are not in the paper and thus the generated
files are not prefixed with `paper_`, but with `dataraces_`.

## Generating plots from reproduced data

By typing `make plots` or just `make`, plots from the reproduced data are generated.
The resulting files are named `figure_N.pdf` where `N` is the number of the figure
from the paper. Again, the plots should be automatically opened.

As with generating plots from our data, the makefile contains also targets to
generate single figures, e.g., to generate the figure for "scalability"
experiments, type `make scalability` or `make figure-3`.

NOTE: it is assumed that the experiments were already ran as instructed and
that they are in `../shamon/experiments`. If you change the artifact layout,
paths need to be adjusted for the scripts to work.
