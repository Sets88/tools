import os
import tracemalloc
from datetime import datetime

last_mem_snapshot = None


def mem_profile():
    snaps = tracemalloc.take_snapshot()
    if last_mem_snapshot:
        previosus_snapshot = last_mem_snapshot
    else:
        last_mem_snapshot = snaps
        previosus_snapshot = snaps

    stats = snaps.compare_to(previosus_snapshot, 'lineno')

    with open('prof_%s_%s.log' % (os.getpid(), os.getpid()), 'a') as f:
        f.write(str(datetime.now()) + '\n')

        for stat in list(reversed(sorted(stats, key=lambda i: i.size)))[:20]:
            mem_data = "{} new KiB {} total KiB {} new {} total memory blocks: ".format(
                stat.size_diff/1024,
                stat.size / 1024,
                stat.count_diff,
                stat.count
            )

            f.write(mem_data + '\n')

            for line in stat.traceback.format():
                f.write(str(line) + '\n')

        last_mem_snapshot = snaps


tracemalloc.start(50)
