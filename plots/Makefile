EXPERIMENTSDIR=..
ORIGINALDATA=original-data
OUTDIR=/opt/results

all: plots

original: outdir scalability-original primes-original primes-tessla-original bank-original dataraces-original
plots: outdir scalability primes primes-tessla bank dataraces

figure-3-original: scalability-original
figure-4-original: primes-original
figure-5-original: primes-tessla-original
figure-6-original: bank-original

figure-3: scalability
figure-4: primes
figure-5: primes-tessla
figure-6: bank

outdir:
	mkdir -p $(OUTDIR)

######################################################################
## original plots
######################################################################

### scalability ##############################
scalability-original: outdir
	python3 scripts/numbers-plot.py $(ORIGINALDATA)/scalability/numbers-8-10000000-1.csv 8
	mv scalability_plot_8_10000000_1_processed.pdf paper_figure_3.pdf
	-cp paper_figure_3.pdf $(OUTDIR)


### primes ##############################
primes-original: outdir
	python3 scripts/primes-plot.py $(ORIGINALDATA)/primes/times.csv  $(ORIGINALDATA)/primes/errors_stats.csv
	mv primes_plot.pdf paper_figure_4.pdf
	-cp paper_figure_4.pdf $(OUTDIR)



### primes-tessla ##############################
primes-tessla-original: outdir
	python3 scripts/primes-tessla-analyze.py $(ORIGINALDATA)/primes-tessla/all.csv
	mv primes_tessla_checked.pdf paper_figure_5_a.pdf
	mv primes_tessla_errs.pdf paper_figure_5_b.pdf
	-cp paper_figure_5_a.pdf $(OUTDIR)
	-cp paper_figure_5_b.pdf $(OUTDIR)

### bank-tessla ##############################
bank-tessla-original: outdir bank-original
bank-original: outdir
	python3 scripts/bank-analyze.py $(ORIGINALDATA)/bank/ $(ORIGINALDATA)/bank-tessla
	mv bank_plot_100000.pdf paper_figure_6.pdf
	-cp paper_figure_6.pdf $(OUTDIR)

dataraces-original: outdir
	python3 scripts/dataraces-analyze.py $(ORIGINALDATA)/dataraces/results.csv
	-cp dataraces.pdf $(OUTDIR)/paper_dataraces.pdf
	-cp dataraces_memory.pdf $(OUTDIR)/paper_dataraces_memory.pdf
	-cp dataraces_times.pdf $(OUTDIR)/paper_dataraces_times.pdf


######################################################################
## reproduced plots
######################################################################

SCALABILITY_CSV=
scalability: outdir
	-python3 scripts/numbers-plot.py $(EXPERIMENTSDIR)/scalability/numbers-8-*-1.csv
	-mv scalability_plot_8_*_1_processed.pdf figure_3.pdf
	-cp figure_3.pdf $(OUTDIR)


### primes
primes: outdir
	python3 scripts/primes-process.py $(EXPERIMENTSDIR)/primes/
	-python3 scripts/primes-plot.py /tmp/times.csv /tmp/errors_stats.csv
	-mv primes_plot.pdf figure_4.pdf
	-cp figure_4.pdf $(OUTDIR)


### primes-tessla ##############################
primes-tessla: outdir
	-python3 scripts/primes-tessla-merge.py $(EXPERIMENTSDIR)/primes/tessla-*.csv &&\
	python3 scripts/primes-tessla-analyze.py /tmp/all.csv &&\
	mv primes_tessla_checked.pdf figure_5_a.pdf &&\
	mv primes_tessla_errs.pdf figure_5_b.pdf
	-cp figure_5_a.pdf $(OUTDIR)
	-cp figure_5_b.pdf $(OUTDIR)


### primes-tessla ##############################
bank-tessla: outdir bank
bank:
	-python3 scripts/bank-analyze.py $(EXPERIMENTSDIR)/bank/ $(EXPERIMENTSDIR)/bank-tessla
	-cp bank_plot*.pdf $(OUTDIR)

dataraces: outdir
	python3 scripts/dataraces-analyze.py $(EXPERIMENTSDIR)/dataraces/results.csv
	-cp dataraces.pdf $(OUTDIR)
	-cp dataraces_memory.pdf $(OUTDIR)
	-cp dataraces_times.pdf $(OUTDIR)

clean:
	-rm *.pdf

.PHONY: clean all outdir
