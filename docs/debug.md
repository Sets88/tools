# Strace

## Trace process

    $ strace -p <pid> -f -s 1000 -r -ttt -T -o <filename>

# Regex to split output

    to open it in visidata, after open hit "space" and type "split-col" to split into columns

    ^([0-9]+\s+)?([0-9\.]+)\s+\(\+\s+([0-9\.]+)\)\s+(.*?)\s*(?:=\s*([\-0-9xa-f\.]+|[\-0-9xa-f]+\s+[A-Z]+\s+\(.*\)|[\-0-9xa-f]+\s+\(flags\s+[A-Z_\|]+\))\s+<([0-9\.]+)>)?

    or(depending on os)

    ^(\[pid\s+[0-9]+\][\s\t]+)?([0-9\.]+)\s+\(\+\s+([0-9\.]+)\)(.*?)((?:=\s*([\-0-9xa-f\.]+|[\-0-9xa-f]+\s+[A-Z]+\s+\(.*\)|[\-0-9xa-f]+\s+\(flags\s+[A-Z_\|]+\))\s+<([0-9\.]+)>)|<unfinished ...>)$

## Summarise time spent in syscall grouped by syscall

    $ strace -f -c -w -p <pid>
