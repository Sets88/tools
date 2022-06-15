Quick way of transfering home directory data from one computer to another one

On eestination side:

    nc -l 1234 | tar -zxp

On source side:

    tar -czpf - . | nc 192.168.1.2 1234

it's possible to add some useful params to skip unneeded directories and to ignore reading error like permissions errors:

    tar -czpf - --ignore-failed-read --exclude=./Library . | nc 192.168.1.2 1234

To transfer just one file, on source side:

    cat file | gzip | nc -l 1234

on destination side:

    nc 192.168.1.2 1234 | gzip -d > file
