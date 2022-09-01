## Create container in namespace of other container to attach to it with gdb

    $ docker run -u0 --pid container:<container>  --privileged -ti --rm --name debugger <image_name_of_original_container> sh


## Find pid of target process

    $ ps aux
    PID   USER     TIME  COMMAND
         1 node      1:05 /sbin/docker-init -- docker-entrypoint.sh python test.py
         6 node      1d13 python test.py
         66 root      0:00 sh
         72 root      0:00 ps aux


## Attach to a process

    $ gdb -p 6


## Do anything with process

    (gdb) call (int) write(22, "{\"s\":\"XAUUSD\",\"p\":{\"r\":1801.93,\"t\":\"1645791182.34200\"}}", 55)
    $1 = 55



# Alpine image python debugging

    $ docker run -u0 --pid container:<container>  --privileged -ti --rm --name debugger <image_name_of_original_container> sh

## Find pid of target process

    $ ps aux
    PID   USER     TIME  COMMAND
         1 node      1:05 /sbin/docker-init -- docker-entrypoint.sh python test.py
         6 node      1d13 python test.py
         66 root      0:00 sh
         72 root      0:00 ps aux

## Install not stripped musl package

    $ apk add musl-dbg

## Attach to a process

    $ gdb -p 6

## Do a core dump of a process

For some reason gdb unable to find symbols in live process which not allows to trace stack trace
but it easiely finds symbols when attaching to core dump this problem appears only in alpine images,
because some alpine libs are stripped by default and for some reason gdb unable to find nonstripped libs(which was installed above)
in debian images even slim ones has non-stripped libs, so it possible to see correct stack trace

    generate-core-file test.core

## Determine version of python

    $ python --version
    Python 3.10.4

## Get gdb python lib from python source

Unfortunatly latest python versions assembled on alpine or debian slim base are stripped, so for more accurate debugging
better to use python on full debian image or assemble python by your own

    $ wget https://www.python.org/ftp/python/3.10.4/Python-3.10.4.tgz
    $ tar xzf Python-3.10.4.tgz
    $ cp ./Python-3.10.4/Tools/gdb/libpython.py .

## Run gdb on core dump

    gdb python test.core

## Load gdb python lib

    source libpython.py

## Use py-* to debug

    py-bt
