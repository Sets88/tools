## Create container in namespace of other container to attach to it with gdb

    $ docker run -u0 --pid container:<container>  --privileged -ti --rm --name debugger <image_name_of_original_container> sh


## Find pid of target process

    $ ps aux
    PID   USER     TIME  COMMAND
         1 node      1:05 /sbin/docker-init -- docker-entrypoint.sh node index.js
         6 node      1d13 node index.js
         66 root      0:00 sh
         72 root      0:00 ps aux


## Attach to a process

    $ gdb -p 6


## Do anything with process

    (gdb) call (int) write(22, "{\"s\":\"XAUUSD\",\"p\":{\"r\":1801.93,\"t\":\"1645791182.34200\"}}", 55)
    $1 = 55



# Alpine image python debugging (have to be compiled without stripping libs)

    $ docker run -u0 --pid container:<container>  --privileged -ti --rm --name debugger <image_name_of_original_container> sh

## Find pid of target process

    $ ps aux
    PID   USER     TIME  COMMAND
         1 node      1:05 /sbin/docker-init -- docker-entrypoint.sh node index.js
         6 node      1d13 node index.js
         66 root      0:00 sh
         72 root      0:00 ps aux

## Attach to a process

    $ gdb -p 6

## Do a core dump of a process

    generate-core-file test.core

## Install not stripped musl package

    $ apk add musl-dbg

## Determine version of python

    $ python --version
    Python 3.10.4

## Get gdb python lib from python source

    $ wget https://www.python.org/ftp/python/3.10.4/Python-3.10.4.tgz
    $ tar xzf Python-3.10.4.tgz
    $ cp ./Python-3.10.4/Tools/gdb/libpython.py .

## Run gdb on core dump

    gdb python test.core

## Load gdb python lib

    source libpython.py

## Use py-* to debug

    py-bt
