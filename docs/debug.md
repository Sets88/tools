# Strace

## Trace process

    $ strace -p <pid> -f -s 1000 -r -ttt -T -o <filename>

# Regex to split output

    to open it in visidata, after open hit "space" and type "split-col" to split into columns

    ^(\[pid\s+[0-9]+\]\s+)?([0-9\.]+)\s+\(\+\s+([0-9\.]+)\)(.*)(\s=\s.*)<([0-9\.]+)>$

## Summarise time spent in syscall grouped by syscall

    $ strace -f -c -w -p <pid>
