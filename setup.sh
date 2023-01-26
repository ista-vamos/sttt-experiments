# FULL EXPERIMENTS
REPEAT=10   #
SCALABILITY_NUM=10000000
PRIMES_10000="no"
BANK_NUM=100000
DATARACES_REPEAT_RUN=1
DATARACES_NONDETS="yes"
DATARACES_TIMEOUT=20


# COMMENT OUT/REMOVE THE FOLLOWING LINES FOR FULL EXPERIMENTS
# (or copy `scripts/setup-full.sh` to this file)
REPEAT=1                # how many time repeat each experiment
SCALABILITY_NUM=10000   # how many events emit in scalability experiments
PRIMES_10000="yes"      # run primes experiments with 10000 only
BANK_NUM=10000          # the (approximate) number of generated commands
DATARACES_REPEAT_RUN=1  # how many times run a single binary
			# setting this to > 1 makes sense only if we use multiple
			# input values which we don't in these experiments
# the artifact includes more benchmarks for dataraces than that are in the paper.
# The extra benchmarks are other benchmarks from SV-COMP that always terminate
# but that contain data non-determinism (nondeterministic inputs). For those benchmarks,
# the result depends on the inputs, so it is not sure whether a wrong answer is caused
# by the analysis or by a badly chosen input
DATARACES_NONDETS="no"  # run only on deterministic benchmarks
DATARACES_TIMEOUT=5     # timeout for a single benchmark (seconds)

