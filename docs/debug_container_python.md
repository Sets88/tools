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
in debian images even slim ones has non-stripped libs, so it possible to see correct stack trace without any extra movements

    (gdb ) generate-core-file test.core


so with alpine images you can force load musl lib symbols to do that you need to find musl lib memory location and add symbol file for it

    (gdb) info sharedlibrary
    From                To                  Syms Read   Shared Object Library
    0x00007f051624c590  0x00007f051647c7b1  Yes         target:/usr/local/lib/libpython3.10.so.1.0
    0x00007f05165c9070  0x00007f05166107e9  Yes (*)     target:/lib/ld-musl-x86_64.so.1
    0x00007f0515df4510  0x00007f0515dfbac1  Yes         target:/usr/local/lib/python3.10/lib-dynload/math.cpython-310-x86_64-linux-gnu.so
    .....
    (gdb) add-symbol-file /usr/lib/debug/lib/ld-musl-x86_64.so.1.debug  0x00007f05165c9070

after this you can debug running process normal way

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

    $ gdb python test.core

## Load gdb python lib

    (gdb) source libpython.py

## Use py-* to debug

    (gdb) py-bt

## Geting python shell inside working process

Lets imagine you are trying to get shell in python process inside alpine conainer, so you have to install musl-dbg and gdb furthermore you have to find memory location of musl lib
and use it to load symbol file, next you have to go to original conainer and install rpdb inside its python environment by

    $ pip install rpdb

rpdb will provide you a python shell on tcp port inside of this container, now in debugging container we run command to set breakpoint

    $ gdb -p 6 -ex 'set confirm off' -ex 'add-symbol-file /usr/lib/debug/lib/ld-musl-x86_64.so.1.debug 0x00007fcb648fc070' -ex 'call PyGILState_Ensure(),PyRun_SimpleString("import rpdb; rpdb.set_trace()"),PyGILState_Release($1)' -ex detach -ex quit

go back to original container and connect to port 4444

    nc 127.0.0.1 4444

and whoala you've just got your python shell inside running process

## Memory leak investigation

Sometimes the main object of investigateion is memory leak, we can use core dump to find top rough amount of object instances:

    $ hexdump some_dump | awk '{printf "%s%s%s%s\n%s%s%s%s\n", $5,$4,$3,$2,$9,$8,$7,$6}' | sort | uniq -c | sort -nr | head
    24798217 0000000000000000
    22728645 0000000000000001
    8840204 00007f46c22da0c0
    4550896 00007f46c22d5f40
    3965252
    335843 0000000000000002
    265495 ffffffffffffffff
    200475 00007f46c22d5680
    124736 00007f46c22d7740
    120437 00007f46c22da600

    $ gdb python some_dump
    (gdb) info symbol 0x7f46c22d5f40
    PyTuple_Type in section .data of /usr/local/lib/libpython3.10.so.1.0

Which tells us that there is a posability roughly 4550896 of tuple instances in core dump

You can also connect gdb to the process and try to find the leaking point, for example, like this:

Attach to a process

    $ gdb -p 6

Acquire GIL

    call PyGILState_Ensure()

Get the last 10,000 objects

    call PyRun_SimpleString("import gc; objs = gc.get_objects()[-1000:]")

Prepare a dictionary where the key is the object's id and the value is a list of object ids that reference it

    call PyRun_SimpleString("import itertools; objs2 = {id(y): [id(z) for z in gc.get_referrers(y)[-1000:]] for y in [x for x in objs]}")

Invert the dictionary, where the key is the object's id and the value is a list of object ids it references, and sort by the number of references

    call PyRun_SimpleString("open('/tmp/debug1', 'w').write(str(sorted(tuple({i: [k for k, v in objs2.items() if i in v] for i in list(itertools.chain(*objs2.values()))}.items()), key=lambda i: len(i[1]))))")

In the simplest cases, a memory leak occurs in the places where there are the most references to objects

Save the contents of the object with the most references for further investigation

    call PyRun_SimpleString("import ctypes; open('/tmp/debug2', 'w').write(str(ctypes.cast(139868276332736, ctypes.py_object).value))")

Release GIL

    call PyGILState_Release($1)

