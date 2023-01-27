from asyncore import write
from itertools import count
import sys

_shm_buff_sizes = [8]
_arbiter_buff_sizes = [128, 512, 1024, 2048]
_counts_gen_primes = [10000, 20000, 30000, 40000]

def get_percentage(val, total):
    return (float(val) / total) * 100


def get_errors_file(
    shm_buff_sizes=_shm_buff_sizes,
    arbiter_buff_sizes=_arbiter_buff_sizes,
    counts_gen_primes=_counts_gen_primes,
    drop_sizes=[""],
    outputfile="/tmp/errors_stats.csv",
):
    """
    This functions only looks for rows in files times-man-*.csv that contain
    c-c-dm-stats
    """
    GENERATED_ERRORS=10
    is_autodrop_test = type(drop_sizes[0]) != str

    row_name = "c-c-dm-errs-stats"

    # columns of what we are interested
    # rowname, 2*(drop, skip, proccessed), errors, time
    errors = 7

    output_file = open(outputfile, "w")
    output_file.writelines(f"buff_size,errors_percentage,num_primes\n")

    for buff_size in shm_buff_sizes:
        for arbiter_buff in arbiter_buff_sizes:
            for count_primes in counts_gen_primes:
                for drop_size in drop_sizes:
                    try:
                        file = open(
                            f"{sys.argv[1]}/times-{buff_size}-{arbiter_buff}-{count_primes}.csv",
                            "r",
                        )
                        lines = file.readlines()

                        for line in lines:
                            parts = line.split(",")
                            if parts[0] == row_name:
                                output_file.write(
                                    f"{arbiter_buff},{get_percentage(parts[errors], GENERATED_ERRORS)},{count_primes}\n"
                                )
                        file.close()
                    except FileNotFoundError as e:
                        print(e)
                        pass

    output_file.close()


def get_times_file(
    shm_buff_sizes=_shm_buff_sizes,
    drop_sizes=[""],
    arbiter_buff_sizes=_arbiter_buff_sizes,
    counts_gen_primes=_counts_gen_primes,
    outputfile="/tmp/times.csv",
    is_overhead_times=False,
):
    """
    This functions only looks for rows in files times-man-*.csv that contain
    c-c-dm-stats
    """
    is_autodrop_test = type(drop_sizes[0]) != str
    # columns of what we are interested

    output_file = open(outputfile, "w")
    csv_file_header = "buff_size,primes,env,time"
    if is_overhead_times:
        csv_file_header += ",wait_cycles,shm_buff"

    if is_autodrop_test:
        csv_file_header += ",drop_size"

    output_file.writelines(f"{csv_file_header}\n")
    for buff_size in shm_buff_sizes:
        for arbiter_buff in arbiter_buff_sizes:
            for count_primes in counts_gen_primes:
                for drop_size in drop_sizes:
                    try:
                        file = open(
                            f"{sys.argv[1]}/times-{buff_size}-{arbiter_buff}-{count_primes}.csv",
                            "r",
                        )

                        for line in file:
                            line = line.replace("\n", "")
                            parts = line.split(",")
                            env_name = ""
                            if parts[0] == "c-native":
                                env_name = "Native"
                            elif parts[0] == "c-drio":
                                env_name = "DRIO-Opt"
                            elif parts[0] == "c-c-empty":
                                env_name = "DRIO-Empty"
                            elif parts[0] == "c-c-dm":
                                env_name = "DRIO-Monitored"
                            if not is_overhead_times:

                                if parts[0] in [
                                    "c-native",
                                    "c-drio",
                                    "c-c-empty",
                                    "c-c-dm",
                                ]:
                                    output_file.write(
                                        f"{arbiter_buff},{count_primes},{env_name},{parts[1]}\n"
                                    )
                            else:
                                if parts[0] in ["c-c-empty", "c-c-dm"]:
                                    output_file.write(
                                        f"{arbiter_buff},{count_primes},{env_name},{parts[1]},{parts[2]},{buff_size}\n"
                                    )
                        file.close()
                    except FileNotFoundError as e:
                        print(e)
                        pass

    output_file.close()


get_errors_file()
get_times_file()

