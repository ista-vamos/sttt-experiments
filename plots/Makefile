SHAMONDIR=../shamon
EXPERIMENTSDIR=$(SHAMONDIR)/experiments
ORIGINALDATA=original-data

all: plots

original: scalability-original primes-original primes-tessla-original bank-original dataraces-original
plots: scalability primes primes-tessla bank dataraces

figure-3-original: scalability-original
figure-4-original: primes-original
figure-5-original: primes-tessla-original
figure-6-original: bank-original

figure-3: scalability
figure-4: primes
figure-5: primes-tessla
figure-6: bank

######################################################################
## original plots
######################################################################

### scalability ##############################
scalability-original:
	python3 scripts/numbers-plot.py $(ORIGINALDATA)/scalability/numbers-8-10000000-1.csv 8
	mv scalability_plot_8_10000000_1_processed.pdf paper_figure_3.pdf
	-xdg-open paper_figure_3.pdf&


### primes ##############################
primes-original:
	python3 scripts/primes-plot.py $(ORIGINALDATA)/primes/times.csv  $(ORIGINALDATA)/primes/errors_stats.csv
	mv primes_plot.pdf paper_figure_4.pdf
	-xdg-open paper_figure_4.pdf&



### primes-tessla ##############################
primes-tessla-original:
	python3 scripts/primes-tessla-analyze.py $(ORIGINALDATA)/primes-tessla/all.csv
	mv primes_tessla_checked.pdf paper_figure_5_a.pdf
	mv primes_tessla_errs.pdf paper_figure_5_b.pdf
	-xdg-open paper_figure_5_a.pdf&
	-xdg-open paper_figure_5_b.pdf&

### bank-tessla ##############################
bank-tessla-original: bank-original
bank-original:
	python3 scripts/bank-analyze.py $(ORIGINALDATA)/bank/ $(ORIGINALDATA)/bank-tessla
	mv bank_plot_100000.pdf paper_figure_6.pdf
	-xdg-open paper_figure_6.pdf&

dataraces-original:
	python3 scripts/dataraces-analyze.py $(ORIGINALDATA)/dataraces/results-pure.csv  $(ORIGINALDATA)/dataraces/results.csv
	-xdg-open dataraces_correctenss.pdf&
	-xdg-open dataraces_errors.pdf&
	-xdg-open dataraces_memory.pdf&
	-xdg-open dataraces_times.pdf&





######################################################################
## reproduced plots
######################################################################

SCALABILITY_CSV=
scalability:
	-python3 scripts/numbers-plot.py $(EXPERIMENTSDIR)/scalability/numbers-8-*-1.csv
	-mv scalability_plot_8_*_1_processed.pdf figure_3.pdf
	-xdg-open figure_3.pdf&


### primes
primes:
	python3 scripts/primes-process.py $(EXPERIMENTSDIR)/primes/
	-python3 scripts/primes-plot.py /tmp/times.csv /tmp/errors_stats.csv
	-mv primes_plot.pdf figure_4.pdf
	-xdg-open figure_4.pdf&


### primes-tessla ##############################
primes-tessla:
	-python3 scripts/primes-tessla-merge.py $(EXPERIMENTSDIR)/primes/tessla-*.csv &&\
	python3 scripts/primes-tessla-analyze.py /tmp/all.csv &&\
	mv primes_tessla_checked.pdf figure_5_a.pdf &&\
	mv primes_tessla_errs.pdf figure_5_b.pdf
	-xdg-open figure_5_a.pdf&
	-xdg-open figure_5_b.pdf&


### primes-tessla ##############################
bank-tessla: bank
bank:
	-python3 scripts/bank-analyze.py $(EXPERIMENTSDIR)/bank/ $(EXPERIMENTSDIR)/bank-tessla
	-xdg-open bank_plot*.pdf&

dataraces:
	grep -v None $(EXPERIMENTSDIR)/dataraces/results.csv > $(EXPERIMENTSDIR)/dataraces/results-pure.csv
	python3 scripts/dataraces-analyze.py $(EXPERIMENTSDIR)/dataraces/results-pure.csv  $(EXPERIMENTSDIR)/dataraces/results.csv
	-xdg-open dataraces_correctenss.pdf&
	-xdg-open dataraces_errors.pdf&
	-xdg-open dataraces_memory.pdf&
	-xdg-open dataraces_times.pdf&

clean:
	-rm *.pdf

.PHONY: clean all
