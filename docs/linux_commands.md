# taskset

control which CPU cores are available to a process

    # taskset -cp 12345
    pid 12345's current affinity list: 0-15
    # taskset -c 0-3 12345
    pid 12345's current affinity list: 0-15
    pid 12345's new affinity list: 0-3
