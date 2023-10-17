# Strace

## Trace process

    $ strace -p <pid> -f -s 1000 -r -ttt -T -o <filename>

## Summarise time spent in syscall grouped by syscall

    $ strace -f -c -w -p <pid>
