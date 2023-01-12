import sys
from os.path import basename

def get_params(path):
    parts = basename(path).split('-')
    assert len(parts) == 5, path
    assert parts[0] == 'tessla'
    assert parts[-1].endswith('.csv')
    return parts[1], int(parts[2]), int(parts[3]), int(parts[-1][:-4])

with open('/tmp/all.csv', 'w') as out:
    out.write("type,shm_bufsize,arbiter_bufsize,primes_num,checked,errnum,errgen,time\n")
    for p in sys.argv[1:]:
        if basename(p) in ('tessla-all.csv', 'all.csv'):
            continue
        try:
            ty, bs, arbs, num = get_params(p)
        except AssertionError: # invalid name
            continue
        with open(p, 'r') as inp:
            for line in inp:
                out.write(f"{ty},{bs},{arbs},{num},")
                out.write(line)

